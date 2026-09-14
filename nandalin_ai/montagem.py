# -*- coding: utf-8 -*-
"""
✂️ MONTAGEM AUTOMÁTICA — O editor profissional
================================================
Transforma as cenas escolhidas pela análise em um Reel/Story pronto:

- Cortes cronológicos nas melhores cenas
- Zoom cinematográfico (Ken Burns) automático
- Hook em texto grande nos primeiros segundos
- Legendas dinâmicas por cena
- Áudio original preservado + opção de música de fundo
- Saída vertical 9:16 (1080x1920 padrão; 4K/8K opcional)
"""

import os
import random
import subprocess
import tempfile
from pathlib import Path

from .cores import Cores, mensagem, aviso, erro, info, ok, linha
from .util import (get_video_info, esc_texto_ffmpeg, fonte_disponivel,
                   PASTA_TEMP, PASTA_IA)

RESOLUCOES = {
    "hd": (1080, 1920),
    "fullhd": (1080, 1920),
    "4k": (2160, 3840),
    "8k": (4320, 7680),
}

def _par( valor):
    return valor if valor % 2 == 0 else valor + 1

def _resolver_resolucao(resolucao):
    resolucao = str(resolucao).lower()
    if resolucao in RESOLUCOES:
        return RESOLUCOES[resolucao]
    if "x" in resolucao:
        try:
            w, h = [int(x) for x in resolucao.split("x")]
            return (_par(w), _par(h))
        except Exception:
            pass
    return RESOLUCOES["hd"]

def _quebrar_texto(texto, max_chars=38):
    """Divide texto em linhas de até max_chars de largura."""
    texto = str(texto).strip()
    if not texto:
        return []
    palavras = texto.split()
    linhas, atual = [], ""
    for p in palavras:
        if len(atual) + len(p) + 1 > max_chars:
            linhas.append(atual)
            atual = p
        else:
            atual = (atual + " " + p).strip()
    if atual:
        linhas.append(atual)
    return linhas

def _filtro_drawtext_linha(texto, H, porcao_y, tamanho, nome_fonte, relargura=0.5):
    """Drawtext de uma linha centralizada."""
    texto_esc = esc_texto_ffmpeg(texto)
    fonte_esc = esc_texto_ffmpeg(nome_fonte)
    y = int(H * porcao_y)
    return (
        f"drawtext=fontfile={fonte_esc}:text='{texto_esc}':"
        f"fontsize={tamanho}:fontcolor=white:"
        f"borderw={max(2, tamanho // 12)}:bordercolor=black@0.85:"
        f"box=1:boxcolor=black@0.45:boxborderw={max(8, tamanho // 6)}:"
        f"x=(w-text_w)/2:y={y}"
    )

def _filtros_shot(inicio, fim, duracao, fps, W, H, zoom, nome_fonte,
                  textos_linhas, porcao_texto, tamanho_texto, com_fade=False):
    """Pipeline de vídeo de um único corte."""
    f = []
    f.append(f"trim=start={inicio:.3f}:end={fim:.3f}")
    f.append("setpts=PTS-STARTPTS")

    # Escala com folga para o zoom — em 4K/8K usa folga mínima (memória é crítica)
    folga = 1.15 if H * W < 8_000_000 else 1.0
    sW, sH = _par(int(W * folga)), _par(int(H * folga))
    f.append(f"scale={sW}:{sH}:flags=lanczos")

    # Zoom cinematográfico (Ken Burns)
    frames = max(2, int(round((fim - inicio) * fps)))
    if zoom == "in":
        zexpr = f"min(1.22,1+(0.22*on/{frames}))"
    elif zoom == "out":
        zexpr = f"max(1.0,1.22-(0.22*on/{frames}))"
    elif zoom == "suave":
        zexpr = f"min(1.12,1+(0.12*on/{frames}))"
    else:
        zexpr = "1"
    f.append(
        f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:fps={fps}:s={W}x{H}"
    )

    # Melhoria leve de cor (estética NANDALIN)
    f.append("eq=saturation=1.15:contrast=1.04:gamma=0.98")

    # Fades
    if com_fade:
        f.append("fade=t=in:st=0:d=0.25")
        f.append(f"fade=t=out:st={max(0.0, duracao - 0.3):.2f}:d=0.3")

    # Textos (hook/legendas)
    if textos_linhas:
        n_linhas = len(textos_linhas)
        espaco = 0.16
        inicio_y = porcao_texto - (espaco * (n_linhas - 1)) / 2
        for i, txt in enumerate(textos_linhas):
            f.append(_filtro_drawtext_linha(txt, H, inicio_y + i * espaco,
                                            tamanho_texto, nome_fonte))

    return f

def _media_duracao_shot(selecao):
    if not selecao:
        return 2.0
    return sum(s["fim"] - s["inicio"] for s in selecao) / len(selecao)

def montar_reel(path_entrada, selecao, conceito, saida=None,
                resolucao="hd", fps=30, efeito_zoom="auto", musica_fundo=None,
                volume_texto=True, nome_base="reel"):
    """
    Monta o Reel completo a partir da seleção de cenas.

    conceito: {"hook": str, "legendas": [str,...], "hashtags": [...], "tema": str}
    """
    W0, H0 = _resolver_resolucao(resolucao)
    W, H = _par(W0), _par(H0)
    nome_fonte = fonte_disponivel()
    if not nome_fonte:
        aviso("Nenhuma fonte encontrada — o vídeo será gerado sem textos.")

    Path(PASTA_TEMP).mkdir(exist_ok=True)
    Path(PASTA_IA).mkdir(exist_ok=True)
    if not saida:
        saida = str(Path(PASTA_IA) / f"{nome_base}_{W}x{H}.mp4")

    # Efeitos de zoom alternados automaticamente
    if efeito_zoom == "auto":
        ciclos = ["in", "suave", "out", "in", "suave", "out", "in"]
    elif efeito_zoom == "in":
        ciclos = ["in"] * 8
    elif efeito_zoom == "out":
        ciclos = ["out"] * 8
    else:
        ciclos = ["suave"] * 8

    # Textos por cena
    hook = conceito.get("hook", "")
    legendas = conceito.get("legendas", []) or []
    tem_textos = bool(nome_fonte)

    tmanh_hook = max(40, int(W * 0.052))
    tmanh_legenda = max(30, int(W * 0.034))

    arquivos_shot = []
    nomes_cena = []

    mensagem(f"\n{Cores.NEGRITO}╔{'═' * 54}╗")
    mensagem(f"{Cores.NEGRITO}║  🎬 MONTANDO REEL EM {W}x{H} — {len(selecao)} cenas{Cores.RESET}")
    mensagem(f"{Cores.NEGRITO}╚{'═' * 54}╝")

    for idx, seg in enumerate(selecao):
        inicio, fim = seg["inicio"], seg["fim"]
        dur = fim - inicio
        if dur <= 0.1:
            continue

        zoom = ciclos[idx % len(ciclos)]

        # Textos desta cena
        linhas_texto = []
        if idx == 0 and hook and tem_textos:
            linhas_texto = _quebrar_texto(hook.upper(), max_chars=30 if W >= 2160 else 24)
            porcao = 0.16
            tamanho = tmanh_hook
        elif tem_textos and legendas:
            l = _quebrar_texto(legendas[min(idx, len(legendas) - 1)], max_chars=34 if W >= 2160 else 26)
            linhas_texto = l
            porcao = 0.80
            tamanho = tmanh_legenda
        else:
            porcao, tamanho = 0.80, tmanh_legenda

        com_fade = (idx == 0) or (idx == len(selecao) - 1)

        # Trim relativo (o -ss já recorta no início; timestamps recomeçam em 0)
        filtros = _filtros_shot(0.0, dur, dur, fps, W, H, zoom, nome_fonte or "",
                                linhas_texto, porcao, tamanho, com_fade)
        vf = ",".join(filtros)

        nome = f"cena_{idx:02d}.mp4"
        caminho = str(Path(PASTA_TEMP) / nome)
        arquivos_shot.append(caminho)
        nomes_cena.append(f"{inicio:.1f}s→{fim:.1f}s ({dur:.1f}s) {'👤' if seg.get('tem_rosto') else '  '}")

        # Preset adaptativo: 4K/8K usam preset mais leve (menos memória)
        preset_x264 = "faster" if (W * H) >= 8_000_000 else "fast"

        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{inicio:.3f}", "-t", f"{dur:.3f}", "-i", str(path_entrada),
            "-vf", vf,
            "-c:v", "libx264", "-preset", preset_x264, "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-max_muxing_queue_size", "2048",
            "-r", str(fps),
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            caminho,
        ]
        ok(f"  Cena {idx + 1}/{len(selecao)}  {nomes_cena[-1]}  zoom={zoom}")
        r = None
        for tentativa in range(3):  # 1ª tentativa + 2 retentativas (recursos transitórios)
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0:
                break
            if tentativa < 2:
                aviso(f"  Tentando novamente a cena {idx + 1} ({tentativa + 2}/3)...")
        if r is not None and r.returncode != 0:
            erro(f"Falha ao renderizar cena {idx + 1}: {r.stderr[-250:]}")
            return None, None

    if not arquivos_shot:
        erro("Nenhuma cena válida para montar.")
        return None, None

    # Concatenar cenas
    lista = str(Path(PASTA_TEMP) / "concat_lista.txt")
    with open(lista, "w") as f:
        for a in arquivos_shot:
            f.write(f"file '{Path(a).resolve().as_posix()}'\n")

    temporario = str(Path(PASTA_TEMP) / "reel_sem_musica.mp4")
    cmd_concat = ["ffmpeg", "-y", "-v", "error", "-f", "concat",
                  "-safe", "0", "-i", lista, "-c", "copy", temporario]
    r = subprocess.run(cmd_concat, capture_output=True, text=True)
    if r.returncode != 0:
        erro(f"Falha na concatenação: {r.stderr[-300:]}")
        return None, None

    # Música de fundo (opcional)
    if musica_fundo and Path(musica_fundo).exists():
        final = saida
        cmd_mix = [
            "ffmpeg", "-y", "-v", "error",
            "-i", temporario, "-i", musica_fundo,
            "-filter_complex",
            "[1:a]volume=0.22[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=3[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            final,
        ]
        ok("🎵 Adicionando música de fundo...")
        r = subprocess.run(cmd_mix, capture_output=True, text=True)
        if r.returncode != 0:
            aviso("Falha ao misturar música; usando áudio original.")
            final = temporario
    else:
        final = temporario

    # mover para pasta definitiva se temporario != final
    if final == temporario and saida != temporario:
        import shutil
        shutil.move(temporario, saida)
        final = saida

    # métricas do Reel criado
    metricas = {
        "duracao": sum(s["fim"] - s["inicio"] for s in selecao),
        "n_cortes": len(arquivos_shot),
        "energia_media": round(float(sum(s.get("energia", 0.4) for s in selecao)) / max(len(selecao), 1), 2),
        "tem_rosto": any(s.get("tem_rosto") for s in selecao),
        "variacao_cena": round(min(1.0, len(selecao) / 7), 2),
        "taxa_completude": 1.0,
        "resolucao": f"{W}x{H}",
    }

    # limpeza de temporários
    for a in arquivos_shot:
        try:
            os.remove(a)
        except OSError:
            pass
    try:
        os.remove(lista)
    except OSError:
        pass

    return final, metricas

def limpar_temp():
    try:
        import shutil
        shutil.rmtree(PASTA_TEMP, ignore_errors=True)
        Path(PASTA_TEMP).mkdir(exist_ok=True)
    except Exception:
        pass