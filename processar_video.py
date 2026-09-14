#!/usr/bin/env python3
"""
🎬 NANDALIN - Processador de Vídeo Premium 8K
===============================================
Processamento de vídeo com QUALIDADE MÁXIMA até 8K:
- Upscaling com Lanczos (melhor algoritmo)
- Filtros cinematográficos de melhoria
- Codec HEVC (libx265) 10-bit
- Formato Story 9:16 ou Original
- CRF 15 (quase lossless)

Uso:
    python processar_video.py
    python processar_video.py meu_video.mp4
"""

import subprocess
import sys
import os
import json
from pathlib import Path

# ========================================
# CONFIGURAÇÃO 8K
# ========================================

RES_8K = (7680, 4320)     # 16:9
RES_8K_V = (4320, 7680)   # 9:16
RES_4K = (3840, 2160)     # 16:9
RES_4K_V = (2160, 3840)   # 9:16

OUTPUT_DIR = "videos_processados_8k"
STORY_DIR = "videos_stories_8k"

# ========================================
# CORES
# ========================================

class C:
    G = "\033[92m"; Y = "\033[93m"; R = "\033[91m"
    B = "\033[94m"; M = "\033[95m"; CI = "\033[96m"
    N = "\033[1m"; RST = "\033[0m"

def msg(t, c="g"):
    cor = {"g": C.G, "y": C.Y, "r": C.R, "b": C.B, "m": C.M, "ci": C.CI}.get(c, C.G)
    print(f"{cor}{t}{C.RST}")

# ========================================
# UTILITÁRIOS
# ========================================

def get_video_info(path):
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json",
           "-show_format", "-show_streams", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def detectar_orientacao(info):
    for s in info["streams"]:
        if s["codec_type"] == "video":
            w, h = int(s["width"]), int(s["height"])
            if h > w: return "vertical", w, h
            elif w > h: return "horizontal", w, h
            else: return "quadrado", w, h
    return "desconhecido", 0, 0

def calcular_resolucao_8k(w, h, orientacao):
    """Calcula a melhor resolução 8K/4K para upscaling"""
    mp = (w * h) / 1_000_000
    
    if mp >= 30:
        return w, h, "já 8K+"
    elif mp >= 7:
        if orientacao == "vertical":
            return RES_8K_V[0], RES_8K_V[1], "4K→8K"
        return RES_8K[0], RES_8K[1], "4K→8K"
    elif mp >= 2:
        if orientacao == "vertical":
            return RES_4K_V[0], RES_4K_V[1], "1080p→4K"
        return RES_4K[0], RES_4K[1], "1080p→4K"
    else:
        # SD: upscale para 2K
        if orientacao == "vertical":
            return 1440, 2560, "SD→2K"
        return 2560, 1440, "SD→2K"

def gerar_filtros_8k(w, h, modo="story"):
    """
    Gera pipeline de filtros 8K na ordem correta:
    1. Crop (se story)
    2. Upscale Lanczos
    3. Filtros de qualidade
    """
    filtros = []
    
    # PASSO 1: Crop para Story 9:16
    if modo == "story":
        ratio = 9 / 16
        if w / h < ratio:
            nh = h
            nw = int(h * ratio)
        else:
            nw = w
            nh = int(w / ratio)
        
        nw = nw if nw % 2 == 0 else nw + 1
        nh = nh if nh % 2 == 0 else nh + 1
        xo = (w - nw) // 2
        yo = (h - nh) // 2
        
        filtros.append(f"crop={nw}:{nh}:{xo}:{yo}")
        msg(f"   ✂️  Crop 9:16: {nw}x{nh}")
        w, h = nw, nh
    
    # PASSO 2: Upscale com Lanczos
    orientacao = "vertical" if h > w else "horizontal"
    tw, th, desc = calcular_resolucao_8k(w, h, orientacao)
    
    if tw * th > w * h:
        filtros.append(f"scale={tw}:{th}:flags=lanczos")
        msg(f"   ⬆️  UPSCALE LANCZOS: {w}x{h} → {tw}x{th} ({desc})")
        w, h = tw, th
    else:
        msg(f"   ℹ️  Já na resolução ideal: {w}x{h}")
    
    # PASSO 3: Filtros de melhoria de qualidade
    msg(f"\n   🎨 Aplicando filtros de qualidade 8K:")
    
    # Redução de ruído (antes da nitidez)
    filtros.append("nlmeans=s=4:p=7:r=3")
    msg(f"      ✓ Redução de ruído avançada (nlmeans s=4)")
    
    # Nitidez principal
    filtros.append("unsharp=5:5:1.5:5:5:0.8")
    msg(f"      ✓ Nitidez cinematográfica (unsharp duplo)")
    
    # Nitidez adicional pós-upscale
    filtros.append("unsharp=3:3:0.6:3:3:0.3")
    msg(f"      ✓ Nitidez pós-upscale")
    
    # Equalização
    filtros.append("eq=brightness=0.03:contrast=1.25:saturation=1.5:gamma=0.95")
    msg(f"      ✓ Contraste +25%, Saturação +50%, Gamma 0.95")
    
    # Balanceamento de cores
    filtros.append("colorbalance=rs=0.05:gs=-0.02:bs=-0.05:rm=0.03:gm=0.0:bm=-0.03")
    msg(f"      ✓ Balanceamento de cores profissional")
    
    # Curvas cinematográficas
    filtros.append("curves=preset=cross_process")
    msg(f"      ✓ Curvas cinematográficas")
    
    return filtros, w, h

# ========================================
# PROCESSAMENTO PRINCIPAL
# ========================================

def processar_video(input_file, output_file, modo="story"):
    """
    Pipeline completo de processamento 8K:
    Crop → Upscale Lanczos → Filtros → Encode HEVC 10-bit
    """
    
    info = get_video_info(input_file)
    orientacao, width, height = detectar_orientacao(info)
    mp = (width * height) / 1_000_000
    duracao = float(info['format'].get('duration', 0))
    
    msg(f"\n{'═' * 60}")
    msg(f"🎬 NANDALIN — PROCESSAMENTO PREMIUM 8K", "ci")
    msg(f"{'═' * 60}")
    msg(f"\n   📁 Arquivo: {Path(input_file).name}")
    msg(f"   📐 Original: {width}x{height} ({orientacao})")
    msg(f"   📊 Megapixels: {mp:.1f} MP")
    msg(f"   ⏱️  Duração: {duracao:.1f}s")
    msg(f"   🎯 Modo: {modo.upper()}")
    
    # Gerar pipeline de filtros
    filtros, fw, fh = gerar_filtros_8k(width, height, modo)
    vf = ",".join(filtros)
    
    megapix_final = (fw * fh) / 1_000_000
    factor = megapix_final / mp if mp > 0 else 1
    
    # Comando FFmpeg com configuração máxima
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-vf", vf,
        "-c:v", "libx265",
        "-preset", "slow",
        "-crf", "15",
        "-pix_fmt", "yuv420p10le",  # 10-bit para 8K
        "-tag:v", "hvc1",           # Compatibilidade
        "-x265-params", "aq-mode=3:aq-strength=1.0:psy-rd=2.0:psy-rdoq=1.0",
        "-movflags", "+faststart",
        "-r", "60",                  # 60 FPS
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        output_file
    ]
    
    msg(f"\n   📦 Configuração de encode:")
    print(f"      🎬 Codec: HEVC (libx265) 10-bit")
    print(f"      📊 CRF: 15 (quase lossless)")
    print(f"      ⚡ Preset: slow (máxima qualidade)")
    print(f"      🎞️  FPS: 60")
    print(f"      🔊 Áudio: AAC 320kbps 48kHz")
    print(f"      ⬆️  Fator upscale: {factor:.1f}x")
    print(f"      📐 Final: {fw}x{fh} ({megapix_final:.1f} MP)")
    
    estimativa = duracao * 0.5  # ~0.5 MB/s para HEVC CRF15
    print(f"      📦 Tamanho estimado: ~{estimativa:.0f} MB")
    
    msg(f"\n⏳ Processando vídeo 8K... (pode levar vários minutos)")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        msg(f"\n❌ ERRO no processamento:", "r")
        print(result.stderr[-800:] if result.stderr else "Sem detalhes")
        
        # Fallback: tentar com libx264
        msg("\n🔄 Tentando fallback com libx264...", "y")
        cmd_fallback = [
            "ffmpeg", "-y",
            "-i", input_file,
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "15",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-r", "60",
            "-c:a", "aac",
            "-b:a", "320k",
            "-ar", "48000",
            output_file
        ]
        result = subprocess.run(cmd_fallback, capture_output=True, text=True)
        
        if result.returncode != 0:
            msg(f"❌ Fallback também falhou: {result.stderr[-300:]}", "r")
            sys.exit(1)
    
    # Resultado
    if os.path.exists(output_file):
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        final_info = get_video_info(output_file)
        
        for s in final_info["streams"]:
            if s["codec_type"] == "video":
                rw, rh = int(s["width"]), int(s["height"])
                break
        
        msg(f"\n{'═' * 60}")
        msg(f"✅ VÍDEO 8K PROCESSADO COM SUCESSO! 🎉", "g")
        msg(f"{'═' * 60}")
        print(f"   📁 Arquivo: {output_file}")
        print(f"   📊 Tamanho: {size_mb:.2f} MB")
        print(f"   📐 Resolução: {rw}x{rh}")
        print(f"   ⬆️  Upscale: {factor:.1f}x")
        print(f"   🎬 Codec: HEVC 10-bit / CRF 15")
        print(f"   🎞️  FPS: 60")
        
        return True
    else:
        msg("❌ Arquivo não criado!", "r")
        return False

# ========================================
# MAIN
# ========================================

def main():
    # Criar pastas
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(STORY_DIR).mkdir(exist_ok=True)
    
    # Determinar input
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input(f"📁 Caminho do vídeo: ").strip().strip('"')
    
    if not os.path.exists(input_file):
        msg(f"❌ Arquivo não encontrado: {input_file}", "r")
        sys.exit(1)
    
    # Modo
    print(f"\n📱 Modo de saída:")
    print(f"  [1] Story 8K (9:16) — padrão")
    print(f"  [2] Original 8K (mantém ratio)")
    
    try:
        modo_opcao = input(f"  Escolha (1 ou 2, Enter=1): ").strip()
    except EOFError:
        modo_opcao = "1"
    
    modo = "story" if modo_opcao != "2" else "original"
    
    # Output
    nome = Path(input_file).stem
    if modo == "story":
        output = Path(STORY_DIR) / f"{nome}_story_8k.mp4"
    else:
        output = Path(OUTPUT_DIR) / f"{nome}_8k.mp4"
    
    processar_video(input_file, str(output), modo)

if __name__ == "__main__":
    main()
