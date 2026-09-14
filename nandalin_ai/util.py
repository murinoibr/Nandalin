# -*- coding: utf-8 -*-
"""Utilitários compartilhados do NANDALIN AI: ffprobe, fontes, pastas."""

import json
import os
import subprocess
import sys
from pathlib import Path

# ========================================
# PASTAS DO PROJETO
# ========================================
PASTA_ORIGINAIS = "videos_originais"
PASTA_STORIES = "videos_stories_8k"
PASTA_PROCESSADOS = "videos_processados_8k"
PASTA_IA = "saidas_ia"          # onde o NANDALIN AI grava os Reels criados
PASTA_TEMP = "temp_ia"          # arquivos temporários da montagem

EXTENSOES_VIDEO = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.mxf', '.prores', '.m4v'}

# ========================================
# FONTES PARA LEGENDAS (descobrir automaticamente)
# ========================================
CANDIDATAS_FONTE = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/local/share/fonts/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]

def fonte_disponivel():
    """Retorna o caminho de uma fonte com negrito disponível."""
    for f in CANDIDATAS_FONTE:
        if os.path.exists(f):
            return f
    # Fallback: procurar qualquer .ttf no sistema
    for base in ["/usr/share/fonts/truetype", "/usr/local/share/fonts", "/System/Library/Fonts"]:
        if os.path.isdir(base):
            for raiz, _, arquivos in os.walk(base):
                for a in arquivos:
                    if a.lower().endswith((".ttf", ".otf")):
                        return os.path.join(raiz, a)
    return None

# ========================================
# CRIAÇÃO DE PASTAS
# ========================================
def criar_pastas():
    for pasta in [PASTA_ORIGINAIS, PASTA_STORIES, PASTA_PROCESSADOS, PASTA_IA, PASTA_TEMP]:
        Path(pasta).mkdir(exist_ok=True)

# ========================================
# FFPROBE
# ========================================
def get_video_info(path):
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json",
           "-show_format", "-show_streams", str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def detectar_orientacao(info):
    for s in info["streams"]:
        if s["codec_type"] == "video":
            w, h = int(s["width"]), int(s["height"])
            if h > w:
                return "vertical", w, h
            elif w > h:
                return "horizontal", w, h
            return "quadrado", w, h
    return "desconhecido", 0, 0

def duracao(info):
    try:
        return float(info["format"].get("duration", 0))
    except (TypeError, ValueError):
        return 0.0

def resumir_info(info):
    """Resumo legível do vídeo."""
    orientacao, w, h = detectar_orientacao(info)
    d = duracao(info)
    fps = 0
    codec = "?"
    for s in info["streams"]:
        if s["codec_type"] == "video":
            fps = eval_rational(s.get("avg_frame_rate", "0/1"))
            codec = s.get("codec_name", "?")
            break
    return {
        "orientacao": orientacao, "width": w, "height": h,
        "duracao": d, "fps": fps, "codec": codec,
        "megapixels": (w * h) / 1_000_000,
    }

def eval_rational(v):
    try:
        a, b = v.split("/")
        a, b = float(a), float(b)
        return a / b if b else 0
    except Exception:
        return 0.0

# ========================================
# LISTAR VÍDEOS LOCAIS
# ========================================
def listar_videos_locais():
    videos = []
    for pasta in [PASTA_ORIGINAIS, "."]:
        if Path(pasta).exists():
            for arquivo in Path(pasta).iterdir():
                if arquivo.suffix.lower() in EXTENSOES_VIDEO and arquivo.is_file():
                    videos.append(str(arquivo))
    # ordenar: primeiro os que estão em videos_originais
    videos.sort(key=lambda v: (PASTA_ORIGINAIS not in v, v))
    return videos

# ========================================
# CHECAGEM DE FERRAMENTAS
# ========================================
def checar_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

def tem_opencv():
    try:
        import cv2  # noqa
        return True
    except ImportError:
        return False

# ========================================
# ESCAPES PARA FFMPEG
# ========================================
def esc_texto_ffmpeg(texto):
    """Escapa texto para uso em filtros ffmpeg (drawtext etc.)."""
    texto = str(texto)
    texto = texto.replace("\\", "\\\\")
    texto = texto.replace(":", "\\:")
    texto = texto.replace("'", "\u2019")   # aspas simples quebram drawtext
    texto = texto.replace(",", "\\,")
    texto = texto.replace("%", "\\%")
    texto = texto.replace(";", "\\;")
    return texto