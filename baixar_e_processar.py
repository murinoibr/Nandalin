#!/usr/bin/env python3
"""
================================================================
🎬 NANDALIN - PROCESSADOR DE VÍDEOS PREMIUM 8K
================================================================
Baixa vídeos do Google Drive, processa com MAXIMA qualidade
até 8K (7680x4320) usando upscaling Lanczos, filtros de
melhoria cinematográfica e formatação para Stories (9:16).

Prioridade #1: QUALIDADE MÁXIMA 8K

Dependências:
    pip install gdown opencv-python numpy

Uso:
    python baixar_e_processar.py
    
    Ou com opções:
    python baixar_e_processar.py --link "LINK_DA_PASTA"
    python baixar_e_processar.py --arquivo "NOME_DO_VIDEO.mp4"
    python baixar_e_processar.py --listar
    python baixar_e_processar.py --modo 8k-hor
================================================================
"""

import subprocess
import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# ========================================
# CONFIGURAÇÃO 8K — QUALIDADE MÁXIMA
# ========================================

# Link da pasta do Google Drive
GOOGLE_DRIVE_FOLDER_ID = "1f2xZSV4YjFIrYHw8I89NNUcS6GpO0V_e"
GOOGLE_DRIVE_FOLDER_URL = f"https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}"

# Pastas do projeto
PASTA_VIDEOS_ORIGINAIS = "videos_originais"
PASTA_VIDEOS_PROCESSADOS = "videos_processados_8k"
PASTA_VIDEOS_STORIES = "videos_stories_8k"

# ========================================
# RESoluções 8K ALVO
# ========================================
RES_8K_HORIZONTAL = (7680, 4320)    # 16:9 — 8K UHD
RES_8K_VERTICAL   = (4320, 7680)   # 9:16 — 8K Story
RES_4K_HORIZONTAL = (3840, 2160)    # 16:9 — 4K UHD
RES_4K_VERTICAL   = (2160, 3840)   # 9:16 — 4K Story
RES_2K_HORIZONTAL = (2560, 1440)    # 16:9 — QHD
RES_2K_VERTICAL   = (1440, 2560)   # 9:16 — QHD Story

# ========================================
# CONFIGURAÇÕES DE PROCESSAMENTO 8K
# ========================================

CONFIG_PROCESSAMENTO = {
    # --- Modo de saída ---
    "modo_saida": "story",          # "story" (9:16) | "original" (mantém ratio) | "fit-8k" (cabe no 8k)
    
    # --- Upscaling 8K ---
    "upscaling_8k": True,           # Ativar upscale para 8K
    "resolucao_alvo": "8k",         # "8k" | "4k" | "2k" | "auto"
    "scaler": "lanczos",            # lanczos = melhor qualidade de upscaling
    
    # --- Qualidade de encode ---
    "codec": "libx265",             # libx265 (HEVC) para 8K | libx264 para compatibilidade
    "crf_qualidade": 15,            # 0-51 (menor = melhor). 15 = qualidade quase lossless
    "preset": "slow",               # slow = melhor compressão/qualidade
    "pixel_format": "yuv420p10le",  # 10-bit para HDR/8K
    "fps_saida": 60,                # 60 FPS para fluidez premium
    "bitrate_audio": "320k",        # Áudio de alta qualidade
    "sample_rate": 48000,           # 48kHz profissional
    
    # --- Filtros de melhoria (aplicados APÓS upscale) ---
    "melhorar_qualidade": True,
    "nitidez": True,                # Unsharp mask profissional
    "nitidez_pos_upscale": True,    # Nitidez adicional pós-upscale
    "reducao_ruido": True,          # Denoise avançado
    "reducao_ruido_forca": 4,       # 1-7 (mais = mais forte, mais lento)
    
    # --- Cor e tons ---
    "saturacao": 1.5,               # 1.0 = original
    "contraste": 1.25,              # 1.0 = original
    "brilho": 0.03,                 # -1.0 a 1.0
    "gamma": 0.95,                  # <1 = mais brilho nas sombras
    "temperatura_cor": 5500,        # Kelvin (5500 = neutro/dia)
    "colorbalance": True,           # Balanceamento de cores profissional
    "curvas_cinematica": True,      # Curvas cinematográficas
}

# ========================================
# MENSAGENS COLORIDAS
# ========================================

class Cores:
    VERDE = "\033[92m"
    AMARELO = "\033[93m"
    VERMELHO = "\033[91m"
    AZUL = "\033[94m"
    MAGENTA = "\033[95m"
    CIANO = "\033[96m"
    BRANCO = "\033[97m"
    NEGRITO = "\033[1m"
    RESET = "\033[0m"
    BG_VERDE = "\033[42m"
    BG_AZUL = "\033[44m"

def mensagem(texto, cor=Cores.VERDE):
    print(f"{cor}{texto}{Cores.RESET}")

def cabecalho():
    print()
    print(f"{Cores.NEGRITO}{Cores.BG_AZUL}{Cores.BRANCO}" + "=" * 64)
    print("  🎬 NANDALIN — PROCESSADOR DE VÍDEOS PREMIUM 8K")
    print("  📊 Qualidade Máxima • Lanczos • HEVC • 10-bit • 60fps")
    print("=" * 64 + f"{Cores.RESET}")
    print()

# ========================================
# CRIAÇÃO DE PASTAS
# ========================================

def criar_pastas():
    """Cria as pastas necessárias"""
    pastas = [
        PASTA_VIDEOS_ORIGINAIS,
        PASTA_VIDEOS_PROCESSADOS,
        PASTA_VIDEOS_STORIES
    ]
    
    for pasta in pastas:
        Path(pasta).mkdir(exist_ok=True)
    
    mensagem("📁 Pastas criadas/verificadas")

# ========================================
# DOWNLOAD DO GOOGLE DRIVE
# ========================================

def verificar_gdown():
    """Verifica se o gdown está instalado"""
    try:
        import gdown
        return True
    except ImportError:
        return False

def instalar_gdown():
    """Instala o gdown automaticamente"""
    mensagem("📦 Instalando gdown...", Cores.AMARELO)
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "gdown"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        mensagem("✅ gdown instalado com sucesso!")
        return True
    else:
        mensagem("❌ Erro ao instalar gdown", Cores.VERMELHO)
        return False

def listar_videos_pasta():
    """Lista e baixa os vídeos da pasta do Google Drive"""
    import gdown
    
    mensagem(f"\n📂 Baixando vídeos da pasta do Google Drive...")
    mensagem(f"🔗 {GOOGLE_DRIVE_FOLDER_URL}\n")
    
    try:
        output = gdown.download_folder(
            GOOGLE_DRIVE_FOLDER_URL,
            output=PASTA_VIDEOS_ORIGINAIS,
            quiet=False,
            remaining_ok=True
        )
        
        if output:
            mensagem(f"\n✅ {len(output)} arquivo(s) baixado(s)")
            return output
        else:
            mensagem("⚠️ Nenhum arquivo encontrado na pasta", Cores.AMARELO)
            return []
            
    except Exception as e:
        mensagem(f"❌ Erro ao baixar: {e}", Cores.VERMELHO)
        return []

def baixar_video_especifico(file_id_or_url):
    """Baixa um vídeo específico do Google Drive"""
    import gdown
    
    mensagem(f"\n📥 Baixando vídeo...")
    
    try:
        if "drive.google.com" in file_id_or_url:
            url = file_id_or_url
        else:
            url = f"https://drive.google.com/uc?id={file_id_or_url}"
        
        output = gdown.download(url, output=PASTA_VIDEOS_ORIGINAIS, quiet=False)
        
        if output:
            mensagem(f"✅ Baixado: {output}")
            return output
        else:
            mensagem("❌ Falha no download", Cores.VERMELHO)
            return None
            
    except Exception as e:
        mensagem(f"❌ Erro: {e}", Cores.VERMELHO)
        return None

# ========================================
# UTILITÁRIOS DE VÍDEO
# ========================================

def get_video_info(path):
    """Obtém informações completas do vídeo"""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def detectar_orientacao(info):
    """Detecta a orientação e retorna dimensões"""
    for stream in info["streams"]:
        if stream["codec_type"] == "video":
            width = int(stream["width"])
            height = int(stream["height"])
            
            if height > width:
                return "vertical", width, height
            elif width > height:
                return "horizontal", width, height
            else:
                return "quadrado", width, height
    
    return "desconhecido", 0, 0

def calcular_resolucao_alvo(width, height, config):
    """Calcula a resolução alvo baseada na config e na resolução original"""
    
    orientacao = "vertical" if height > width else "horizontal"
    megapixels_orig = (width * height) / 1_000_000
    
    # Determinar resolução alvo
    res_config = config["resolucao_alvo"]
    
    if res_config == "auto":
        # Auto: escolher a melhor resolução que faça sentido
        if megapixels_orig >= 30:
            # Já é 8K ou superior — manter
            return width, height, "já 8K+"
        elif megapixels_orig >= 7:
            # É 4K — upscale para 8K
            if orientacao == "vertical":
                return RES_8K_VERTICAL[0], RES_8K_VERTICAL[1], "4K → 8K vertical"
            else:
                return RES_8K_HORIZONTAL[0], RES_8K_HORIZONTAL[1], "4K → 8K"
        elif megapixels_orig >= 2:
            # É 1080p — upscale para 4K ou 8K
            if orientacao == "vertical":
                return RES_4K_VERTICAL[0], RES_4K_VERTICAL[1], "1080p → 4K vertical"
            else:
                return RES_4K_HORIZONTAL[0], RES_4K_HORIZONTAL[1], "1080p → 4K"
        else:
            # SD ou menor — upscale para 2K
            if orientacao == "vertical":
                return RES_2K_VERTICAL[0], RES_2K_VERTICAL[1], "SD → 2K vertical"
            else:
                return RES_2K_HORIZONTAL[0], RES_2K_HORIZONTAL[1], "SD → 2K"
    
    elif res_config == "8k":
        if orientacao == "vertical":
            return RES_8K_VERTICAL[0], RES_8K_VERTICAL[1], "→ 8K vertical (4320x7680)"
        else:
            return RES_8K_HORIZONTAL[0], RES_8K_HORIZONTAL[1], "→ 8K UHD (7680x4320)"
    
    elif res_config == "4k":
        if orientacao == "vertical":
            return RES_4K_VERTICAL[0], RES_4K_VERTICAL[1], "→ 4K vertical (2160x3840)"
        else:
            return RES_4K_HORIZONTAL[0], RES_4K_HORIZONTAL[1], "→ 4K UHD (3840x2160)"
    
    elif res_config == "2k":
        if orientacao == "vertical":
            return RES_2K_VERTICAL[0], RES_2K_VERTICAL[1], "→ 2K vertical (1440x2560)"
        else:
            return RES_2K_HORIZONTAL[0], RES_2K_HORIZONTAL[1], "→ 2K QHD (2560x1440)"
    
    # Fallback
    return width, height, "mantido original"

# ========================================
# PIPELINE DE FILTROS 8K
# ========================================

def gerar_filtros_upscale_e_melhoria(width, height, config):
    """
    Gera o pipeline completo de filtros FFmpeg:
    1. Crop para formato desejado (se story)
    2. Upscale com Lanczos
    3. Filtros de melhoria de qualidade (APÓS upscale)
    
    IMPORTANTE: A ordem é fundamental!
    Primeiro crop, depois scale (upscale), depois filtros de qualidade.
    Assim a nitidez e os filtros atuam na resolução final.
    """
    
    filtros = []
    orientacao = "vertical" if height > width else "horizontal"
    
    # ====================================
    # PASSO 1: CROP (se modo story)
    # ====================================
    if config["modo_saida"] == "story":
        target_ratio = 9 / 16
        
        if width / height < target_ratio:
            new_height = height
            new_width = int(height * target_ratio)
        else:
            new_width = width
            new_height = int(width / target_ratio)
        
        # Garantir dimensões pares
        new_width = new_width if new_width % 2 == 0 else new_width + 1
        new_height = new_height if new_height % 2 == 0 else new_height + 1
        
        x_offset = (width - new_width) // 2
        y_offset = (height - new_height) // 2
        
        filtros.append(f"crop={new_width}:{new_height}:{x_offset}:{y_offset}")
        mensagem(f"✂️  Crop 9:16: {new_width}x{new_height}")
        
        # Atualizar dimensões para o próximo passo
        width = new_width
        height = new_height
        orientacao = "vertical"
    
    elif config["modo_saida"] == "fit-8k":
        # Ajustar para caber dentro do 8K mantendo ratio
        if orientacao == "vertical":
            max_w, max_h = RES_8K_VERTICAL
        else:
            max_w, max_h = RES_8K_HORIZONTAL
        
        scale_factor = min(max_w / width, max_h / height)
        new_w = int(width * scale_factor)
        new_h = int(height * scale_factor)
        
        # Garantir pares
        new_w = new_w if new_w % 2 == 0 else new_w + 1
        new_h = new_h if new_h % 2 == 0 else new_h + 1
        
        filtros.append(f"scale={new_w}:{new_h}:flags=lanczos")
        mensagem(f"📐 Scale para fit-8K: {new_w}x{new_h}")
        
        width = new_w
        height = new_h
    
    # ====================================
    # PASSO 2: UPSCALE COM LANCZOS (prioridade #1)
    # ====================================
    if config["upscaling_8k"]:
        target_w, target_h, desc = calcular_resolucao_alvo(width, height, config)
        
        # Só fazer upscale se a resolução alvo for maior
        if target_w * target_h > width * height:
            filtros.append(f"scale={target_w}:{target_h}:flags=lanczos")
            mensagem(f"⬆️  UPSCALE LANCZOS: {width}x{height} → {target_w}x{target_h} {desc}")
        else:
            mensagem(f"ℹ️  Resolução original já é maior ou igual ao alvo ({width}x{height})")
    
    # ====================================
    # PASSO 3: FILTROS DE MELHORIA DE QUALIDADE
    # (aplicados na resolução FINAL para máxima eficácia)
    # ====================================
    
    if config["melhorar_qualidade"]:
        
        # --- 3a. Redução de ruído (ANTES da nitidez para melhor resultado) ---
        if config["reducao_ruido"]:
            forca = config["reducao_ruido_forca"]
            filtros.append(f"nlmeans=s={forca}:p=7:r=3")
        
        # --- 3b. Nitidez principal (unsharp mask profissional) ---
        if config["nitidez"]:
            filtros.append("unsharp=5:5:1.5:5:5:0.8")
        
        # --- 3c. Nitidez adicional pós-upscale ---
        if config["nitidez_pos_upscale"]:
            filtros.append("unsharp=3:3:0.6:3:3:0.3")
        
        # --- 3d. Equalização: brilho, contraste, saturação, gamma ---
        filtros.append(
            f"eq="
            f"brightness={config['brilho']}:"
            f"contrast={config['contraste']}:"
            f"saturation={config['saturacao']}:"
            f"gamma={config['gamma']}"
        )
        
        # --- 3e. Balanceamento de cores profissional ---
        if config["colorbalance"]:
            filtros.append(
                "colorbalance="
                "rs=0.05:gs=-0.02:bs=-0.05:"
                "rm=0.03:gm=0.0:bm=-0.03"
            )
        
        # --- 3f. Curvas cinematográficas ---
        if config["curvas_cinematica"]:
            filtros.append("curves=preset=cross_process")
        
        # --- 3g. Temperatura de cor ---
        temp = config["temperatura_cor"]
        if temp != 6500:  # 6500K = neutro D65
            filtros.append(f"colortemperature=temperature={temp}")
    
    return filtros

def construir_comando_ffmpeg(input_file, output_file, filtros, config):
    """Constrói o comando FFmpeg completo com configuração 8K"""
    
    vf_string = ",".join(filtros)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-vf", vf_string,
        "-c:v", config["codec"],
        "-preset", config["preset"],
        "-crf", str(config["crf_qualidade"]),
        "-pix_fmt", config["pixel_format"],
        "-movflags", "+faststart",
        "-r", str(config["fps_saida"]),
    ]
    
    # Parâmetros extras para HEVC (libx265)
    if config["codec"] == "libx265":
        cmd.extend([
            "-tag:v", "hvc1",       # Compatibilidade Apple
            "-x265-params", "aq-mode=3:aq-strength=1.0:psy-rd=2.0:psy-rdoq=1.0",
        ])
    
    # Áudio
    cmd.extend([
        "-c:a", "aac",
        "-b:a", config["bitrate_audio"],
        "-ar", str(config["sample_rate"]),
        output_file
    ])
    
    return cmd

# ========================================
# PROCESSAMENTO PRINCIPAL
# ========================================

def processar_video(input_file, output_file, config):
    """Processa o vídeo com pipeline completo de qualidade 8K"""
    
    info = get_video_info(input_file)
    orientacao, width, height = detectar_orientacao(info)
    
    # Informações detalhadas do original
    megapixels = (width * height) / 1_000_000
    duracao = float(info['format'].get('duration', 0))
    
    mensagem(f"\n{'─' * 60}")
    mensagem(f"📹 ANALISANDO: {Path(input_file).name}")
    mensagem(f"{'─' * 60}")
    mensagem(f"   📐 Resolução original: {width}x{height} ({orientacao})")
    mensagem(f"   📊 Megapixels: {megapixels:.1f} MP")
    mensagem(f"   ⏱️  Duração: {duracao:.1f}s")
    
    # Calcular resolução alvo para exibição
    if config["upscaling_8k"]:
        _, _, desc = calcular_resolucao_alvo(width, height, config)
        mensagem(f"   🎯 Alvo: {desc}")
    
    # Gerar pipeline de filtros
    filtros = gerar_filtros_upscale_e_melhoria(width, height, config)
    
    if not filtros:
        filtros = ["null"]  # Fallback sem filtros
    
    # Construir comando
    cmd = construir_comando_ffmpeg(input_file, output_file, filtros, config)
    
    # Exibir resumo da configuração
    mensagem(f"\n🎨 PIPELINE DE QUALIDADE 8K:")
    print(f"   📱 Modo: {config['modo_saida'].upper()}")
    print(f"   ⬆️  Upscale: {'✓ Lanczos' if config['upscaling_8k'] else '✗'}")
    print(f"   🎬 Codec: {config['codec'].upper()} {'(HEVC/10-bit)' if config['codec'] == 'libx265' else '(AVC)'}")
    print(f"   📊 CRF: {config['crf_qualidade']} {'(quase lossless)' if config['crf_qualidade'] <= 15 else ''}")
    print(f"   🎞️  FPS: {config['fps_saida']}")
    print(f"   🎨 Pixel: {config['pixel_format']}")
    print(f"   🔊 Áudio: {config['bitrate_audio']} / {config['sample_rate']}Hz")
    print()
    print(f"   ✨ Filtros de qualidade:")
    print(f"      {'✓' if config['reducao_ruido'] else '✗'} Redução de ruído (nlmeans s={config['reducao_ruido_forca']})")
    print(f"      {'✓' if config['nitidez'] else '✗'} Nitidez (unsharp mask)")
    print(f"      {'✓' if config['nitidez_pos_upscale'] else '✗'} Nitidez pós-upscale")
    print(f"      🌈 Saturação: +{int((config['saturacao']-1)*100)}%")
    print(f"      🔆 Contraste: +{int((config['contraste']-1)*100)}%")
    print(f"      ☀️  Brilho: +{int(config['brilho']*100)}%")
    print(f"      🎭 Gamma: {config['gamma']}")
    print(f"      {'✓' if config['colorbalance'] else '✗'} Balanceamento de cores")
    print(f"      {'✓' if config['curvas_cinematica'] else '✗'} Curvas cinematográficas")
    print(f"      🌡️  Temperatura: {config['temperatura_cor']}K")
    
    # Estimativa de tamanho
    if config["codec"] == "libx265":
        estimativa_mb = duracao * 0.5  # HEVC ~0.5 MB/s para CRF 15
    else:
        estimativa_mb = duracao * 1.0  # AVC ~1.0 MB/s para CRF 15
    
    print(f"\n   📦 Tamanho estimado: ~{estimativa_mb:.0f} MB")
    
    mensagem(f"\n⏳ Processando... (pode levar vários minutos para 8K)")
    print(f"   🔧 Comando FFmpeg: {' '.join(cmd[:10])}...\n")
    
    # Executar
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        mensagem(f"\n❌ ERRO no processamento:", Cores.VERMELHO)
        # Mostrar últimas linhas do erro
        erro = result.stderr[-800:] if result.stderr else "Sem detalhes"
        print(erro)
        
        # Tentar fallback com libx264 se HEVC falhou
        if config["codec"] == "libx265":
            mensagem("\n🔄 Tentando fallback com libx264...", Cores.AMARELO)
            config_fallback = config.copy()
            config_fallback["codec"] = "libx264"
            config_fallback["pixel_format"] = "yuv420p"
            return processar_video(input_file, output_file, config_fallback)
        
        return False
    
    # Verificar resultado
    if os.path.exists(output_file):
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        final_info = get_video_info(output_file)
        
        for stream in final_info["streams"]:
            if stream["codec_type"] == "video":
                fw = int(stream["width"])
                fh = int(stream["height"])
                break
        
        megapixels_final = (fw * fh) / 1_000_000
        factor = megapixels_final / megapixels if megapixels > 0 else 0
        
        mensagem(f"\n{'═' * 60}")
        mensagem(f"✅ VÍDEO 8K PROCESSADO COM SUCESSO!", Cores.BG_VERDE)
        mensagem(f"{'═' * 60}")
        print(f"   📁 Arquivo: {output_file}")
        print(f"   📊 Tamanho: {size_mb:.2f} MB")
        print(f"   📐 Resolução: {fw}x{fh} ({megapixels_final:.1f} MP)")
        print(f"   ⬆️  Fator de upscale: {factor:.1f}x")
        print(f"   🎬 Codec: {config['codec'].upper()}")
        
        return True
    else:
        mensagem("❌ Arquivo de saída não foi criado!", Cores.VERMELHO)
        return False

# ========================================
# LISTAR VÍDEOS LOCAIS
# ========================================

def listar_videos_locais():
    """Lista vídeos já baixados localmente"""
    extensoes = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.mxf', '.prores'}
    videos = []
    
    for pasta in [PASTA_VIDEOS_ORIGINAIS, "."]:
        if Path(pasta).exists():
            for arquivo in Path(pasta).iterdir():
                if arquivo.suffix.lower() in extensoes and arquivo.is_file():
                    videos.append(str(arquivo))
    
    return videos

# ========================================
# MENU PRINCIPAL
# ========================================

def mostrar_config_atual(config):
    """Exibe a configuração atual formatada"""
    print(f"\n  {Cores.NEGRITO}📊 CONFIGURAÇÃO 8K ATUAL:{Cores.RESET}\n")
    print(f"  {'─' * 45}")
    print(f"  📱 Modo de saída:      {config['modo_saida']}")
    print(f"  ⬆️  Upscale 8K:         {'✓' if config['upscaling_8k'] else '✗'}")
    print(f"  🎯 Resolução alvo:     {config['resolucao_alvo']}")
    print(f"  🎬 Codec:              {config['codec']}")
    print(f"  📊 CRF:                {config['crf_qualidade']}")
    print(f"  ⚡ Preset:             {config['preset']}")
    print(f"  🎨 Pixel format:       {config['pixel_format']}")
    print(f"  🎞️  FPS:                {config['fps_saida']}")
    print(f"  🔊 Áudio:              {config['bitrate_audio']}")
    print(f"  {'─' * 45}")
    print(f"  ✨ Nitidez:            {'✓' if config['nitidez'] else '✗'}")
    print(f"  ✨ Nitidez pós-upscale:{'✓' if config['nitidez_pos_upscale'] else '✗'}")
    print(f"  🧹 Redução de ruído:   {'✓'} (força {config['reducao_ruido_forca']})")
    print(f"  🌈 Saturação:          {config['saturacao']}")
    print(f"  🔆 Contraste:          {config['contraste']}")
    print(f"  ☀️  Brilho:             {config['brilho']}")
    print(f"  🎭 Gamma:              {config['gamma']}")
    print(f"  🌡️  Temperatura:        {config['temperatura_cor']}K")
    print(f"  {'─' * 45}")

def menu_principal():
    """Exibe o menu e processa opções"""
    
    cabecalho()
    criar_pastas()
    
    if not verificar_gdown():
        if not instalar_gdown():
            mensagem("❌ Instale gdown: pip install gdown", Cores.VERMELHO)
            return
    
    while True:
        print()
        print(f"{Cores.CIANO}{'═' * 55}{Cores.RESET}")
        print(f"{Cores.NEGRITO}  📋 MENU PRINCIPAL — NANDALIN 8K{Cores.RESET}")
        print(f"{Cores.CIANO}{'═' * 55}{Cores.RESET}")
        print()
        print(f"  {Cores.VERDE}[1]{Cores.RESET} 📥 Baixar TODOS os vídeos da pasta Drive")
        print(f"  {Cores.VERDE}[2]{Cores.RESET} 📥 Baixar um vídeo específico")
        print(f"  {Cores.VERDE}[3]{Cores.RESET} 📂 Listar vídeos já baixados")
        print(f"  {Cores.VERDE}[4]{Cores.RESET} 🎬 Processar em modo STORY 8K (9:16)")
        print(f"  {Cores.VERDE}[5]{Cores.RESET} 🎬 Processar em modo ORIGINAL 8K (16:9)")
        print(f"  {Cores.VERDE}[6]{Cores.RESET} 🎬 Processar um vídeo específico")
        print(f"  {Cores.VERDE}[7]{Cores.RESET} ⚙️  Configurar qualidade/8K")
        print(f"  {Cores.VERDE}[8]{Cores.RESET} 📊 Mostrar configuração atual")
        print(f"  {Cores.VERDE}[0]{Cores.RESET} 🚪 Sair")
        print()
        
        opcao = input(f"  {Cores.AMARELO}Escolha: {Cores.RESET}").strip()
        print()
        
        if opcao == "1":
            listar_videos_pasta()
            
        elif opcao == "2":
            file_id = input(f"  {Cores.AMARELO}Link ou ID do arquivo: {Cores.RESET}").strip()
            if file_id:
                baixar_video_especifico(file_id)
            
        elif opcao == "3":
            videos = listar_videos_locais()
            if videos:
                mensagem(f"📂 {len(videos)} vídeo(s):\n")
                for i, v in enumerate(videos, 1):
                    size = os.path.getsize(v) / (1024 * 1024)
                    info = get_video_info(v)
                    _, w, h = detectar_orientacao(info)
                    print(f"  {i}. {Path(v).name} — {w}x{h} ({size:.1f} MB)")
            else:
                mensagem("⚠️ Nenhum vídeo encontrado", Cores.AMARELO)
        
        elif opcao == "4":
            # Processar todos em modo Story 8K
            config_story = CONFIG_PROCESSAMENTO.copy()
            config_story["modo_saida"] = "story"
            
            videos = listar_videos_locais()
            if not videos:
                mensagem("⚠️ Nenhum vídeo para processar", Cores.AMARELO)
                continue
            
            mostrar_config_atual(config_story)
            confirmar = input(f"\n  {Cores.AMARELO}Processar {len(videos)} vídeo(s) em STORY 8K? (s/n): {Cores.RESET}").strip().lower()
            if confirmar != 's':
                continue
            
            mensagem(f"\n🎬 Processando {len(videos)} vídeo(s) em STORY 8K...\n")
            sucesso = 0
            
            for i, video in enumerate(videos, 1):
                nome = Path(video).stem
                output = Path(PASTA_VIDEOS_STORIES) / f"{nome}_story_8k.mp4"
                
                mensagem(f"\n{'─' * 50}")
                mensagem(f"📹 Vídeo {i}/{len(videos)}: {Path(video).name}")
                
                if processar_video(str(video), str(output), config_story):
                    sucesso += 1
            
            mensagem(f"\n{'═' * 55}")
            mensagem(f"📊 RESULTADO: {sucesso}/{len(videos)} processados com sucesso!")
        
        elif opcao == "5":
            # Processar todos em modo Original 8K
            config_orig = CONFIG_PROCESSAMENTO.copy()
            config_orig["modo_saida"] = "original"
            
            videos = listar_videos_locais()
            if not videos:
                mensagem("⚠️ Nenhum vídeo para processar", Cores.AMARELO)
                continue
            
            mostrar_config_atual(config_orig)
            confirmar = input(f"\n  {Cores.AMARELO}Processar {len(videos)} vídeo(s) em ORIGINAL 8K? (s/n): {Cores.RESET}").strip().lower()
            if confirmar != 's':
                continue
            
            mensagem(f"\n🎬 Processando {len(videos)} vídeo(s) em ORIGINAL 8K...\n")
            sucesso = 0
            
            for i, video in enumerate(videos, 1):
                nome = Path(video).stem
                output = Path(PASTA_VIDEOS_PROCESSADOS) / f"{nome}_8k.mp4"
                
                mensagem(f"\n{'─' * 50}")
                mensagem(f"📹 Vídeo {i}/{len(videos)}: {Path(video).name}")
                
                if processar_video(str(video), str(output), config_orig):
                    sucesso += 1
            
            mensagem(f"\n{'═' * 55}")
            mensagem(f"📊 RESULTADO: {sucesso}/{len(videos)} processados!")
        
        elif opcao == "6":
            # Processar um específico
            videos = listar_videos_locais()
            if not videos:
                mensagem("⚠️ Nenhum vídeo encontrado", Cores.AMARELO)
                continue
            
            print(f"  Vídeos disponíveis:\n")
            for i, v in enumerate(videos, 1):
                info = get_video_info(v)
                _, w, h = detectar_orientacao(info)
                size = os.path.getsize(v) / (1024 * 1024)
                print(f"  {i}. {Path(v).name} — {w}x{h} ({size:.1f} MB)")
            
            try:
                idx = int(input(f"\n  {Cores.AMARELO}Número: {Cores.RESET}").strip()) - 1
                if 0 <= idx < len(videos):
                    video = videos[idx]
                    
                    print(f"\n  Modo de saída:")
                    print(f"  [1] Story 8K (9:16)")
                    print(f"  [2] Original 8K (mantém ratio)")
                    modo = input(f"  {Cores.AMARELO}Escolha: {Cores.RESET}").strip()
                    
                    config_sel = CONFIG_PROCESSAMENTO.copy()
                    if modo == "2":
                        config_sel["modo_saida"] = "original"
                        nome = Path(video).stem
                        output = Path(PASTA_VIDEOS_PROCESSADOS) / f"{nome}_8k.mp4"
                    else:
                        config_sel["modo_saida"] = "story"
                        nome = Path(video).stem
                        output = Path(PASTA_VIDEOS_STORIES) / f"{nome}_story_8k.mp4"
                    
                    processar_video(str(video), str(output), config_sel)
                else:
                    mensagem("❌ Número inválido", Cores.VERMELHO)
            except (ValueError, EOFError):
                mensagem("❌ Entrada inválida", Cores.VERMELHO)
        
        elif opcao == "7":
            # Configurar
            print(f"\n  {Cores.NEGRITO}⚙️ CONFIGURAR QUALIDADE 8K:{Cores.RESET}\n")
            print(f"  [1]  Modo de saída:      {CONFIG_PROCESSAMENTO['modo_saida']}")
            print(f"  [2]  Upscale 8K:         {'✓' if CONFIG_PROCESSAMENTO['upscaling_8k'] else '✗'}")
            print(f"  [3]  Resolução alvo:     {CONFIG_PROCESSAMENTO['resolucao_alvo']}")
            print(f"  [4]  Codec:              {CONFIG_PROCESSAMENTO['codec']}")
            print(f"  [5]  CRF:                {CONFIG_PROCESSAMENTO['crf_qualidade']}")
            print(f"  [6]  FPS:                {CONFIG_PROCESSAMENTO['fps_saida']}")
            print(f"  [7]  Saturação:          {CONFIG_PROCESSAMENTO['saturacao']}")
            print(f"  [8]  Contraste:          {CONFIG_PROCESSAMENTO['contraste']}")
            print(f"  [9]  Brilho:             {CONFIG_PROCESSAMENTO['brilho']}")
            print(f"  [10] Força denoise:      {CONFIG_PROCESSAMENTO['reducao_ruido_forca']}")
            print(f"  [11] Temperatura cor:    {CONFIG_PROCESSAMENTO['temperatura_cor']}K")
            
            try:
                cfg = input(f"\n  {Cores.AMARELO}Alterar opção (número): {Cores.RESET}").strip()
                
                if cfg == "1":
                    modo = CONFIG_PROCESSAMENTO['modo_saida']
                    CONFIG_PROCESSAMENTO['modo_saida'] = "original" if modo == "story" else "story"
                elif cfg == "2":
                    CONFIG_PROCESSAMENTO['upscaling_8k'] = not CONFIG_PROCESSAMENTO['upscaling_8k']
                elif cfg == "3":
                    val = input(f"  Resolução (8k/4k/2k/auto): ").strip().lower()
                    if val in ["8k", "4k", "2k", "auto"]:
                        CONFIG_PROCESSAMENTO['resolucao_alvo'] = val
                elif cfg == "4":
                    val = input(f"  Codec (libx265/libx264): ").strip().lower()
                    if val in ["libx265", "libx264"]:
                        CONFIG_PROCESSAMENTO['codec'] = val
                elif cfg == "5":
                    val = int(input(f"  CRF (0-51, menor=melhor): ").strip())
                    CONFIG_PROCESSAMENTO['crf_qualidade'] = max(0, min(51, val))
                elif cfg == "6":
                    val = int(input(f"  FPS (24/30/60/120): ").strip())
                    CONFIG_PROCESSAMENTO['fps_saida'] = max(1, min(120, val))
                elif cfg == "7":
                    val = float(input(f"  Saturação (1.0-3.0): ").strip())
                    CONFIG_PROCESSAMENTO['saturacao'] = max(1.0, min(3.0, val))
                elif cfg == "8":
                    val = float(input(f"  Contraste (1.0-2.0): ").strip())
                    CONFIG_PROCESSAMENTO['contraste'] = max(1.0, min(2.0, val))
                elif cfg == "9":
                    val = float(input(f"  Brilho (-0.5 a 0.5): ").strip())
                    CONFIG_PROCESSAMENTO['brilho'] = max(-0.5, min(0.5, val))
                elif cfg == "10":
                    val = int(input(f"  Força denoise (1-7): ").strip())
                    CONFIG_PROCESSAMENTO['reducao_ruido_forca'] = max(1, min(7, val))
                elif cfg == "11":
                    val = int(input(f"  Temperatura em Kelvin (2000-10000): ").strip())
                    CONFIG_PROCESSAMENTO['temperatura_cor'] = max(2000, min(10000, val))
                
                mensagem("✅ Configuração atualizada!")
            except (ValueError, EOFError):
                pass
        
        elif opcao == "8":
            mostrar_config_atual(CONFIG_PROCESSAMENTO)
            print(f"\n  📁 Pasta originais: {PASTA_VIDEOS_ORIGINAIS}/")
            print(f"  📁 Pasta stories 8K: {PASTA_VIDEOS_STORIES}/")
            print(f"  📁 Pasta processados 8K: {PASTA_VIDEOS_PROCESSADOS}/")
            print(f"  🔗 Pasta Drive: {GOOGLE_DRIVE_FOLDER_URL}")
        
        elif opcao == "0":
            mensagem("\n👋 Até logo! Produza conteúdo premium! 🎬\n")
            break
        
        else:
            mensagem("❌ Opção inválida", Cores.VERMELHO)

# ========================================
# ARGUMENTOS DE LINHA DE COMANDO
# ========================================

def main():
    parser = argparse.ArgumentParser(
        description="🎬 NANDALIN — Processador de Vídeos Premium 8K"
    )
    
    parser.add_argument("--link", "-l", help="Link ou ID no Google Drive")
    parser.add_argument("--arquivo", "-a", help="Arquivo local para processar")
    parser.add_argument("--listar", "-ls", action="store_true", help="Listar vídeos baixados")
    parser.add_argument("--baixar-todos", "-bt", action="store_true", help="Baixar todos da pasta")
    parser.add_argument("--processar-todos", "-pt", action="store_true", help="Processar todos (Story 8K)")
    parser.add_argument("--modo", "-m", choices=["story", "original", "fit-8k"], 
                        default="story", help="Modo de saída")
    parser.add_argument("--resolucao", "-r", choices=["8k", "4k", "2k", "auto"],
                        default="8k", help="Resolução alvo")
    parser.add_argument("--codec", "-c", choices=["libx265", "libx264"],
                        default="libx265", help="Codec de vídeo")
    parser.add_argument("--crf", type=int, default=15, help="CRF (0-51, menor=melhor)")
    parser.add_argument("--fps", type=int, default=60, help="FPS de saída")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        menu_principal()
        return
    
    criar_pastas()
    
    if not verificar_gdown():
        instalar_gdown()
    
    # Aplicar argumentos na config
    CONFIG_PROCESSAMENTO["modo_saida"] = args.modo
    CONFIG_PROCESSAMENTO["resolucao_alvo"] = args.resolucao
    CONFIG_PROCESSAMENTO["codec"] = args.codec
    CONFIG_PROCESSAMENTO["crf_qualidade"] = args.crf
    CONFIG_PROCESSAMENTO["fps_saida"] = args.fps
    
    if args.link:
        if "drive.google.com/drive/folders" in args.link:
            listar_videos_pasta()
        else:
            baixar_video_especifico(args.link)
    
    elif args.baixar_todos:
        listar_videos_pasta()
    
    elif args.listar:
        videos = listar_videos_locais()
        if videos:
            mensagem(f"📂 {len(videos)} vídeo(s):\n")
            for i, v in enumerate(videos, 1):
                info = get_video_info(v)
                _, w, h = detectar_orientacao(info)
                size = os.path.getsize(v) / (1024 * 1024)
                print(f"  {i}. {Path(v).name} — {w}x{h} ({size:.1f} MB)")
        else:
            mensagem("⚠️ Nenhum vídeo encontrado", Cores.AMARELO)
    
    elif args.arquivo:
        if os.path.exists(args.arquivo):
            nome = Path(args.arquivo).stem
            if args.modo == "story":
                output = Path(PASTA_VIDEOS_STORIES) / f"{nome}_story_8k.mp4"
            else:
                output = Path(PASTA_VIDEOS_PROCESSADOS) / f"{nome}_8k.mp4"
            processar_video(args.arquivo, str(output), CONFIG_PROCESSAMENTO)
        else:
            mensagem(f"❌ Arquivo não encontrado: {args.arquivo}", Cores.VERMELHO)
    
    elif args.processar_todos:
        videos = listar_videos_locais()
        if videos:
            for video in videos:
                nome = Path(video).stem
                if args.modo == "story":
                    output = Path(PASTA_VIDEOS_STORIES) / f"{nome}_story_8k.mp4"
                else:
                    output = Path(PASTA_VIDEOS_PROCESSADOS) / f"{nome}_8k.mp4"
                processar_video(str(video), str(output), CONFIG_PROCESSAMENTO)

if __name__ == "__main__":
    main()
