#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 NANDALIN PRO — Aplicativo Profissional de Melhoria de Vídeo com IA
=====================================================================
Interface Web completa para:
- Upscaling inteligente 4K / 8K
- Edição profissional com IA
- Análise de cenas e momentos
- Color grading cinematográfico
- Export em múltiplos formatos

Uso:
    python app.py
    python app.py --port 8080
"""

import subprocess
import sys
import os
import json
import uuid
import time
import threading
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename

# ========================================
# CONFIGURAÇÃO
# ========================================

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 * 1024  # 4GB max upload
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.getcwd(), 'processed')
app.config['TEMP_FOLDER'] = os.path.join(os.getcwd(), 'temp_web')

# Criar pastas
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['TEMP_FOLDER']]:
    Path(folder).mkdir(parents=True, exist_ok=True)

# Jobs em andamento
jobs = {}
jobs_lock = threading.Lock()

# ========================================
# UTILITÁRIOS DE VÍDEO
# ========================================

def get_video_info(path):
    """Obtém informações completas do vídeo via ffprobe"""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}

def detectar_orientacao(info):
    """Detecta orientação do vídeo"""
    for s in info.get("streams", []):
        if s.get("codec_type") == "video":
            w, h = int(s["width"]), int(s["height"])
            if h > w:
                return "vertical", w, h
            elif w > h:
                return "horizontal", w, h
            else:
                return "quadrado", w, h
    return "desconhecido", 0, 0

def formatar_duracao(segundos):
    """Formata segundos em HH:MM:SS"""
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

# ========================================
# ANÁLISE INTELIGENTE COM IA
# ========================================

def analise_ia_completa(video_path, job_id):
    """Análise completa do vídeo usando IA/OpenCV"""
    try:
        import cv2
        import numpy as np
        has_cv2 = True
    except ImportError:
        has_cv2 = False

    info = get_video_info(video_path)
    orientacao, width, height = detectar_orientacao(info)
    duracao = float(info.get("format", {}).get("duration", 0))
    mp = (width * height) / 1_000_000

    resultado = {
        "info_basica": {
            "arquivo": os.path.basename(video_path),
            "resolucao": f"{width}x{height}",
            "largura": width,
            "altura": height,
            "orientacao": orientacao,
            "megapixels": round(mp, 2),
            "duracao_seg": round(duracao, 2),
            "duracao_formatada": formatar_duracao(duracao),
        },
        "cenas": [],
        "melhores_momentos": [],
        "analise_qualidade": {},
        "recomendacoes": [],
    }

    if not has_cv2:
        resultado["recomendacoes"].append({
            "tipo": "info",
            "texto": "Instale opencv-python para análise avançada: pip install opencv-python"
        })
        return resultado

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # === DETECÇÃO DE CENAS ===
    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        return resultado

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    cenas = []
    frame_atual = 0
    scores_frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)

        diff = cv2.absdiff(prev_gray, gray_blur)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        score = float(np.sum(thresh) / 255.0)

        tempo = frame_atual / fps

        # Análise de qualidade por frame (a cada segundo)
        if frame_atual % max(1, int(fps)) == 0:
            nitidez = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            contraste = float(gray.std())
            brilho = float(gray.mean())
            q_score = (nitidez * 0.5) + (contraste * 0.3) + (abs(brilho - 127) * 0.2)

            scores_frames.append({
                "tempo": round(tempo, 2),
                "nitidez": round(nitidez, 2),
                "contraste": round(contraste, 2),
                "brilho": round(brilho, 2),
                "score": round(q_score, 2),
            })

        if score > 1000:
            cenas.append({
                "tempo": round(tempo, 2),
                "frame": frame_atual,
                "score": round(score, 2),
                "duracao": 0,
            })

        prev_gray = gray_blur
        frame_atual += 1

    cap.release()

    # Calcular duração das cenas
    for i in range(len(cenas)):
        if i + 1 < len(cenas):
            cenas[i]["duracao"] = round(cenas[i + 1]["tempo"] - cenas[i]["tempo"], 2)
        else:
            cenas[i]["duracao"] = round(duracao - cenas[i]["tempo"], 2)

    resultado["cenas"] = cenas

    # === MELHORES MOMENTOS ===
    scores_frames.sort(key=lambda x: x["score"], reverse=True)
    resultado["melhores_momentos"] = scores_frames[:10]

    # === ANÁLISE DE QUALIDADE GERAL ===
    if scores_frames:
        scores = [f["score"] for f in scores_frames]
        nitidezes = [f["nitidez"] for f in scores_frames]
        contrastes = [f["contraste"] for f in scores_frames]
        brilhos = [f["brilho"] for f in scores_frames]

        media_score = sum(scores) / len(scores)
        media_nitidez = sum(nitidezes) / len(nitidezes)
        media_contraste = sum(contrastes) / len(contrastes)
        media_brilho = sum(brilhos) / len(brilhos)

        # Classificar qualidade
        if media_nitidez > 500:
            nitidez_classe = "Alta"
        elif media_nitidez > 100:
            nitidez_classe = "Média"
        else:
            nitidez_classe = "Baixa"

        if media_contraste > 60:
            contraste_classe = "Alto"
        elif media_contraste > 30:
            contraste_classe = "Médio"
        else:
            contraste_classe = "Baixo"

        resultado["analise_qualidade"] = {
            "score_geral": round(media_score, 2),
            "nitidez_media": round(media_nitidez, 2),
            "nitidez_classe": nitidez_classe,
            "contraste_medio": round(media_contraste, 2),
            "contraste_classe": contraste_classe,
            "brilho_medio": round(media_brilho, 2),
            "total_cenas": len(cenas),
            "total_frames": total_frames,
            "fps": round(fps, 2),
        }

    # === RECOMENDAÇÕES INTELIGENTES ===
    recomendacoes = []

    if mp < 2:
        recomendacoes.append({
            "tipo": "upscaling",
            "icone": "⬆️",
            "titulo": "Upscale para 4K",
            "texto": f"Resolução atual ({width}x{height}) pode ser melhorada para 4K (3840x2160)."
        })
    elif mp < 7:
        recomendacoes.append({
            "tipo": "upscaling",
            "icone": "⬆️",
            "titulo": "Upscale para 8K",
            "texto": f"Resolução atual ({width}x{height}) pode ser melhorada para 8K (7680x4320)."
        })

    if resultado["analise_qualidade"].get("nitidez_classe") == "Baixa":
        recomendacoes.append({
            "tipo": "nitidez",
            "icone": "✨",
            "titulo": "Nitidez Baixa Detectada",
            "texto": "Recomenda-se aplicar unsharp mask dupla para melhorar nitidez."
        })

    if resultado["analise_qualidade"].get("contraste_classe") == "Baixo":
        recomendacoes.append({
            "tipo": "contraste",
            "icone": "🔆",
            "titulo": "Contraste Baixo",
            "texto": "Recomenda-se aumentar contraste e aplicar curvas cinematográficas."
        })

    if len(cenas) > 5:
        recomendacoes.append({
            "tipo": "edicao",
            "icone": "✂️",
            "titulo": "Múltiplas Cenas Detectadas",
            "texto": f"{len(cenas)} mudanças de cena detectadas. Considere cortes inteligentes."
        })

    if mp >= 7:
        recomendacoes.append({
            "tipo": "qualidade",
            "icone": "🏆",
            "titulo": "Alta Resolução",
            "texto": "Seu vídeo já possui alta resolução. Aproveite para exportar em 8K!"
        })

    resultado["recomendacoes"] = recomendacoes

    return resultado


def gerar_filtros_adaptativos(config, width, height, nivel_qualidade="alta"):
    """
    Gera filtros de qualidade ADAPTATIVOS à resolução alvo.
    nlmeans só é viável até 1080p — para 4K/8K usa hqdn3d (muito mais leve).

    nível_qualidade: "alta" | "media" | "basica" (fallback progressivo)
    """
    filtros = []

    # Redução de ruído adaptativa por resolução
    if config.get("denoise", True):
        megapixels = (width * height) / 1_000_000
        forca = config.get("denoise_force", 4)

        if megapixels <= 2:   # ≤ 1080p → nlmeans (melhor qualidade, aceitável)
            filtros.append(f"nlmeans=s={forca}:p=7:r=3")
        elif megapixels <= 8: # até 4K → hqdn3d (NM leve ~30x mais rápido)
            strength = min(6.0, forca * 1.5)
            filtros.append(f"hqdn3d={strength}:{strength}:6:6")
        else:                 # 8K → hqdn3d mais leve ainda
            filtros.append("hqdn3d=3.0:3.0:4:4")

    # Nitidez (escala força pela resolução para evitar artefatos)
    if config.get("sharpen", True) and nivel_qualidade != "basica":
        megapixels = (width * height) / 1_000_000
        if megapixels <= 2:
            filtros.append("unsharp=5:5:1.5:5:5:0.8")
        elif megapixels <= 8:
            filtros.append("unsharp=5:5:1.0:5:5:0.5")
        else:
            filtros.append("unsharp=3:3:0.6:3:3:0.3")

    if config.get("sharpen_post", True) and nivel_qualidade != "basica":
        filtros.append("unsharp=3:3:0.5:3:3:0.25")

    # Equalização
    brilho = config.get("brightness", 0.03)
    contraste = config.get("contrast", 1.25)
    saturacao = config.get("saturation", 1.5)
    gamma = config.get("gamma", 0.95)
    filtros.append(f"eq=brightness={brilho}:contrast={contraste}:saturation={saturacao}:gamma={gamma}")

    # Balanceamento de cores
    if config.get("color_balance", True):
        filtros.append("colorbalance=rs=0.05:gs=-0.02:bs=-0.05:rm=0.03:gm=0.0:bm=-0.03")

    # Curvas (memória pesada — LUT) → só em resoluções até 4K e não no básico
    curva = config.get("curves", "cross_process")
    megapixels = (width * height) / 1_000_000
    if (curva and curva != "none"
            and nivel_qualidade != "basica"
            and megapixels <= 8):
        filtros.append(f"curves=preset={curva}")

    # Temperatura (LUT leve) → não no básico
    temp = config.get("temperature", 5500)
    if (temp and temp != 6500 and nivel_qualidade != "basica"):
        filtros.append(f"colortemperature=temperature={temp}")

    # Vinheta
    if config.get("vignette", False):
        filtros.append("vignette=PI/5")

    return filtros


def parse_progresso_ffmpeg(linha, duracao):
    """Extrai progresso das linhas de progresso do ffmpeg"""
    if "time=" in linha and duracao > 0:
        try:
            parte = linha.split("time=")[1].split(" ")[0].strip()
            h, m, s = parte.split(":")
            tempo = int(h) * 3600 + int(m) * 60 + float(s)
            return min(99, round((tempo / duracao) * 100))
        except Exception:
            pass
    return None


def video_valido(path):
    """
    Valida se o arquivo de vídeo é legível (ffprobe encontra stream de vídeo).
    IMPORTANTE: em alguns ambientes o ffmpeg sai com código ≠ 0 mesmo tendo
    produzido um arquivo válido (ex.: SIGTERM no flush final). A validação
    REAL é feita pelo ffprobe.
    """
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return False
    try:
        info = get_video_info(path)
        for s in info.get("streams", []):
            if s.get("codec_type") == "video" and int(s.get("width", 0)) > 0:
                return True
    except Exception:
        pass
    return False


def processar_video_web(video_path, output_path, config, job_id):
    """Processa vídeo com pipeline adaptativo + fallback progressivo"""
    try:
        with jobs_lock:
            jobs[job_id]["status"] = "processando"
            jobs[job_id]["progresso"] = 0
            jobs[job_id]["mensagem"] = "Iniciando processamento..."

        # Obter info do vídeo
        info = get_video_info(video_path)
        orientacao, width, height = detectar_orientacao(info)
        duracao = float(info.get("format", {}).get("duration", 0))

        # Número de threads limitadas (memória segura em CPUs pequenos)
        n_threads = min(4, max(1, (os.cpu_count() or 2) // 2))

        # 1. CROP (se story)
        if config.get("modo") == "story":
            ratio = 9 / 16
            if width / height < ratio:
                nh = height
                nw = int(height * ratio)
            else:
                nw = width
                nh = int(width / ratio)
            nw = nw if nw % 2 == 0 else nw + 1
            nh = nh if nh % 2 == 0 else nh + 1
            xo = (width - nw) // 2
            yo = (height - nh) // 2
            filtros_base = [f"crop={nw}:{nh}:{xo}:{yo}"]
            width, height = nw, nh
        else:
            filtros_base = []

        # 2. UPSCALE
        resolucao = config.get("resolucao", "4k")
        orientacao = "vertical" if height > width else "horizontal"

        RES_MAP = {
            "8k_h": (7680, 4320), "8k_v": (4320, 7680),
            "4k_h": (3840, 2160), "4k_v": (2160, 3840),
            "2k_h": (2560, 1440), "2k_v": (1440, 2560),
        }

        if resolucao in ["4k", "8k", "2k"]:
            key = f"{resolucao}_v" if orientacao == "vertical" else f"{resolucao}_h"
            tw, th = RES_MAP.get(key, (width, height))
            if tw * th > width * height:
                filtros_base.append(f"scale={tw}:{th}:flags=lanczos")
                width, height = tw, th

        # ==========================================
        # Estratégia de fallback progressivo
        # ==========================================
        codec = config.get("codec", "libx265")
        crf = config.get("crf", 18)
        fps_out = config.get("fps", 60)

        tentativas = [
            # 1. Qualidade máxima (como pedido)
            {"nivel": "alta", "codec": codec, "preset": "slow",
             "crf": crf,
             "pix_fmt": "yuv420p10le" if codec == "libx265" else "yuv420p"},
            # 2. Fallback: libx264 8-bit
            {"nivel": "alta", "codec": "libx264", "preset": "medium",
             "crf": crf, "pix_fmt": "yuv420p"},
            # 3. Fallback: menos filtros + encode mais leve
            {"nivel": "media", "codec": "libx264", "preset": "medium",
             "crf": crf + 2, "pix_fmt": "yuv420p"},
            # 4. Fallback mínimo: só upscale + eq (memória mínima)
            {"nivel": "basica", "codec": "libx264", "preset": "fast",
             "crf": crf + 4, "pix_fmt": "yuv420p"},
        ]

        ultimo_erro = ""

        for tentativa in tentativas:
            try:
                with jobs_lock:
                    jobs[job_id]["progresso"] = 0
                    jobs[job_id]["mensagem"] = (
                        f"Nível {tentativa['nivel']}: "
                        f"{tentativa['codec']} / {tentativa['preset']} / CRF {tentativa['crf']}"
                    )

                # Gerar filtros adaptativos para esta tentativa
                filtros = list(filtros_base)
                filtros.extend(gerar_filtros_adaptativos(
                    config, width, height, tentativa["nivel"]))

                vf = ",".join(filtros) if filtros else "null"

                cmd = [
                    "ffmpeg", "-y",
                    "-nostdin",
                    "-threads", str(n_threads),
                    "-i", video_path,
                    "-vf", vf,
                    "-c:v", tentativa["codec"],
                    "-preset", tentativa["preset"],
                    "-crf", str(tentativa["crf"]),
                    "-pix_fmt", tentativa["pix_fmt"],
                    "-movflags", "+faststart",
                    "-r", str(fps_out),
                ]

                if tentativa["codec"] == "libx265":
                    cmd.extend(["-tag:v", "hvc1"])
                    cmd.extend(["-x265-params", "qp=20:aq-mode=3:aq-strength=1.0"])

                cmd.extend([
                    "-c:a", "aac",
                    "-b:a", "256k",
                    "-ar", "48000",
                    output_path
                ])

                with jobs_lock:
                    jobs[job_id]["comando"] = tentativa["nivel"] + ": " + " ".join(cmd[:12]) + "..."

                # Executar lendo stderr em tempo real para progresso
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1,
                )

                for linha in process.stderr:
                    pct = parse_progresso_ffmpeg(linha, duracao)
                    if pct is not None:
                        with jobs_lock:
                            jobs[job_id]["progresso"] = pct
                            jobs[job_id]["mensagem"] = f"{tentativa['nivel']}: processando ({pct}%)"

                process.wait()

                # CRÍTICO: validar o ARQUIVO REAL, não o exit code
                if video_valido(output_path):
                    return finalizar_job_sucesso(
                        job_id, output_path, duracao,
                        tentativa["codec"], tentativa["crf"], fps_out)

                ultimo_erro = f"saída inválida (code {process.returncode})"
                if os.path.exists(output_path):
                    os.remove(output_path)

            except Exception as e:
                ultimo_erro = str(e)
                if os.path.exists(output_path):
                    os.remove(output_path)

        # Todas as tentativas falharam
        with jobs_lock:
            jobs[job_id]["status"] = "erro"
            jobs[job_id]["mensagem"] = f"Erro ao processar: {ultimo_erro}"
        return False

    except Exception as e:
        with jobs_lock:
            jobs[job_id]["status"] = "erro"
            jobs[job_id]["mensagem"] = str(e)
        return False


def finalizar_job_sucesso(job_id, output_path, duracao, codec, crf, fps_out):
    """Registra o sucesso do processamento"""
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    out_info = get_video_info(output_path)
    out_w, out_h = 0, 0
    for s in out_info.get("streams", []):
        if s.get("codec_type") == "video":
            out_w, out_h = int(s["width"]), int(s["height"])
            break

    with jobs_lock:
        jobs[job_id]["status"] = "concluido"
        jobs[job_id]["progresso"] = 100
        jobs[job_id]["mensagem"] = "Processamento concluído!"
        jobs[job_id]["resultado"] = {
            "arquivo_saida": os.path.basename(output_path),
            "tamanho_mb": round(size_mb, 2),
            "resolucao": f"{out_w}x{out_h}",
            "largura": out_w,
            "altura": out_h,
            "codec": codec,
            "crf": crf,
            "fps": fps_out,
            "duracao": formatar_duracao(duracao),
        }
    return True


# ========================================
# ROTAS DA API
# ========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload de vídeo"""
    if 'video' not in request.files:
        return jsonify({"erro": "Nenhum arquivo enviado"}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"erro": "Nenhum arquivo selecionado"}), 400

    # Verificar extensão
    extensoes = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.mxf', '.prores', '.ts'}
    ext = Path(file.filename).suffix.lower()
    if ext not in extensoes:
        return jsonify({"erro": f"Formato não suportado: {ext}"}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(filepath)

    # Obter info
    info = get_video_info(filepath)
    orientacao, w, h = detectar_orientacao(info)
    duracao = float(info.get("format", {}).get("duration", 0))
    mp = (w * h) / 1_000_000

    return jsonify({
        "sucesso": True,
        "arquivo": unique_name,
        "nome_original": file.filename,
        "info": {
            "resolucao": f"{w}x{h}",
            "largura": w,
            "altura": h,
            "orientacao": orientacao,
            "megapixels": round(mp, 2),
            "duracao_seg": round(duracao, 2),
            "duracao_formatada": formatar_duracao(duracao),
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    """Análise IA do vídeo"""
    data = request.json
    filename = data.get("arquivo")
    if not filename:
        return jsonify({"erro": "Arquivo não especificado"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({"erro": "Arquivo não encontrado"}), 404

    job_id = uuid.uuid4().hex[:12]
    with jobs_lock:
        jobs[job_id] = {"status": "analisando", "mensagem": "Analisando vídeo..."}

    resultado = analise_ia_completa(filepath, job_id)

    with jobs_lock:
        jobs[job_id]["status"] = "analise_concluida"
        jobs[job_id]["resultado_analise"] = resultado

    return jsonify({"sucesso": True, "job_id": job_id, "analise": resultado})

@app.route('/api/process', methods=['POST'])
def process_video():
    """Processar vídeo com configuração"""
    data = request.json
    filename = data.get("arquivo")
    config = data.get("config", {})

    if not filename:
        return jsonify({"erro": "Arquivo não especificado"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({"erro": "Arquivo não encontrado"}), 404

    job_id = uuid.uuid4().hex[:12]
    nome_base = Path(filename).stem
    resolucao = config.get("resolucao", "4k")
    modo = config.get("modo", "original")
    output_name = f"{nome_base}_{modo}_{resolucao}_{job_id}.mp4"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_name)

    with jobs_lock:
        jobs[job_id] = {
            "status": "iniciando",
            "mensagem": "Preparando processamento...",
            "progresso": 0,
            "arquivo_entrada": filename,
            "arquivo_saida": output_name,
            "config": config,
            "criado_em": datetime.now().isoformat(),
        }

    # Processar em thread separada
    thread = threading.Thread(
        target=processar_video_web,
        args=(filepath, output_path, config, job_id),
        daemon=True
    )
    thread.start()

    return jsonify({"sucesso": True, "job_id": job_id})

@app.route('/api/status/<job_id>')
def job_status(job_id):
    """Verificar status de um job"""
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"erro": "Job não encontrado"}), 404
    return jsonify(job)

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download do vídeo processado"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({"erro": "Arquivo não encontrado"}), 404
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/api/video/<folder>/<filename>')
def serve_video(folder, filename):
    """Servir vídeo para preview"""
    if folder == "uploads":
        base = app.config['UPLOAD_FOLDER']
    elif folder == "processed":
        base = app.config['OUTPUT_FOLDER']
    else:
        return jsonify({"erro": "Pasta inválida"}), 404

    filepath = os.path.join(base, filename)
    if not os.path.exists(filepath):
        return jsonify({"erro": "Arquivo não encontrado"}), 404

    return send_file(filepath, mimetype='video/mp4')

@app.route('/api/presets')
def get_presets():
    """Retorna presets de processamento"""
    presets = {
        "cinematico_4k": {
            "nome": "🎬 Cinematográfico 4K",
            "descricao": "Look cinematográfico profissional em 4K",
            "config": {
                "resolucao": "4k", "modo": "original", "codec": "libx265",
                "crf": 18, "fps": 60,
                "brightness": 0.02, "contrast": 1.2, "saturation": 1.3, "gamma": 0.95,
                "denoise": True, "denoise_force": 3, "sharpen": True, "sharpen_post": True,
                "color_balance": True, "curves": "cross_process", "temperature": 5600,
                "vignette": False,
            }
        },
        "ultra_8k": {
            "nome": "🏆 Ultra 8K",
            "descricao": "Qualidade máxima em 8K, quase lossless",
            "config": {
                "resolucao": "8k", "modo": "original", "codec": "libx265",
                "crf": 15, "fps": 60,
                "brightness": 0.03, "contrast": 1.25, "saturation": 1.5, "gamma": 0.95,
                "denoise": True, "denoise_force": 4, "sharpen": True, "sharpen_post": True,
                "color_balance": True, "curves": "cross_process", "temperature": 5500,
                "vignette": False,
            }
        },
        "story_4k": {
            "nome": "📱 Story 4K (9:16)",
            "descricao": "Formato Story/Reels em 4K",
            "config": {
                "resolucao": "4k", "modo": "story", "codec": "libx265",
                "crf": 18, "fps": 60,
                "brightness": 0.04, "contrast": 1.3, "saturation": 1.6, "gamma": 0.95,
                "denoise": True, "denoise_force": 4, "sharpen": True, "sharpen_post": True,
                "color_balance": True, "curves": "cross_process", "temperature": 5500,
                "vignette": False,
            }
        },
        "vibrante": {
            "nome": "🌈 Vibrante",
            "descricao": "Cores vivas e saturadas",
            "config": {
                "resolucao": "4k", "modo": "original", "codec": "libx265",
                "crf": 18, "fps": 60,
                "brightness": 0.05, "contrast": 1.35, "saturation": 2.0, "gamma": 0.92,
                "denoise": True, "denoise_force": 3, "sharpen": True, "sharpen_post": True,
                "color_balance": True, "curves": "cross_process", "temperature": 5800,
                "vignette": False,
            }
        },
        "noturno": {
            "nome": "🌙 Noturno",
            "descricao": "Otimizado para cenas escuras",
            "config": {
                "resolucao": "4k", "modo": "original", "codec": "libx265",
                "crf": 18, "fps": 60,
                "brightness": 0.08, "contrast": 1.4, "saturation": 1.3, "gamma": 0.85,
                "denoise": True, "denoise_force": 6, "sharpen": True, "sharpen_post": True,
                "color_balance": True, "curves": "cross_process", "temperature": 4500,
                "vignette": True,
            }
        },
        "suave": {
            "nome": "🎨 Suave",
            "descricao": "Look suave e natural",
            "config": {
                "resolucao": "4k", "modo": "original", "codec": "libx265",
                "crf": 20, "fps": 60,
                "brightness": 0.03, "contrast": 1.1, "saturation": 1.2, "gamma": 0.98,
                "denoise": True, "denoise_force": 5, "sharpen": False, "sharpen_post": True,
                "color_balance": False, "curves": "none", "temperature": 5500,
                "vignette": False,
            }
        },
        "dramatico": {
            "nome": "🎭 Dramático",
            "descricao": "Alto contraste e tons escuros",
            "config": {
                "resolucao": "4k", "modo": "original", "codec": "libx265",
                "crf": 16, "fps": 60,
                "brightness": -0.02, "contrast": 1.5, "saturation": 1.1, "gamma": 0.88,
                "denoise": True, "denoise_force": 3, "sharpen": True, "sharpen_post": True,
                "color_balance": True, "curves": "cross_process", "temperature": 5200,
                "vignette": True,
            }
        },
        "retro": {
            "nome": "📷 Retro",
            "descricao": "Look vintage e retrô",
            "config": {
                "resolucao": "4k", "modo": "original", "codec": "libx265",
                "crf": 18, "fps": 30,
                "brightness": 0.05, "contrast": 1.15, "saturation": 0.8, "gamma": 1.05,
                "denoise": True, "denoise_force": 2, "sharpen": True, "sharpen_post": False,
                "color_balance": True, "curves": "cross_process", "temperature": 6200,
                "vignette": True,
            }
        },
    }
    return jsonify(presets)

@app.route('/api/health')
def health():
    """Health check"""
    # Verificar FFmpeg
    ffmpeg_ok = shutil.which("ffmpeg") is not None
    ffprobe_ok = shutil.which("ffprobe") is not None

    try:
        import cv2
        cv2_ok = True
    except ImportError:
        cv2_ok = False

    return jsonify({
        "status": "ok",
        "ffmpeg": ffmpeg_ok,
        "ffprobe": ffprobe_ok,
        "opencv": cv2_ok,
        "versao": "2.0.0",
    })


# ========================================
# MAIN
# ========================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="🎬 NANDALIN PRO — App de Melhoria de Vídeo")
    parser.add_argument("--port", "-p", type=int, default=5000, help="Porta do servidor")
    parser.add_argument("--host", default="0.0.0.0", help="Host do servidor")
    parser.add_argument("--debug", "-d", action="store_true", help="Modo debug")
    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════╗
║  🎬 NANDALIN PRO — Aplicativo de Melhoria de Vídeo  ║
║  🌐 Interface Web Profissional com IA                ║
║  📍 http://localhost:{args.port}                           ║
╚══════════════════════════════════════════════════════╝
    """)

    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
