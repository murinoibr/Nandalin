# -*- coding: utf-8 -*-
"""
🔍 ANÁLISE DE VÍDEO — O programa que "enxerga"
==================================================
Percebe o FOCO do vídeo e encontra os MELHORES MOMENTOS:

- Detecção de cenas (cortes de câmera)
- Presença humana (rostos → o "foco" real do conteúdo)
- Movimento dinâmico e nitidez (qualidade visual)
- Energia do áudio + estimativa de BPM (ritmo)
- Classificação de cada segundo: quão assistível ele é
- Seleção dos trechos que viram o Reel
"""

import os
import subprocess
from pathlib import Path

import numpy as np

from .util import get_video_info, duracao, fonte_disponivel, PASTA_TEMP

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None

# ========================================
# DETECÇÃO DE ROSTOS (o "foco" humano)
# ========================================
_CASCADE = None
_CAMINHO_CASCADE = str(Path(__file__).parent / "data" / "haarcascade_frontalface_default.xml")

def _carregar_cascade():
    global _CASCADE
    if _CASCADE is None and HAS_CV2 and os.path.exists(_CAMINHO_CASCADE):
        try:
            _CASCADE = cv2.CascadeClassifier(_CAMINHO_CASCADE)
        except Exception:
            _CASCADE = None
    return _CASCADE

def tem_deteccao_rosto():
    return _carregar_cascade() is not None

# ========================================
# EXTRAÇÃO DE ÁUDIO PARA ANÁLISE
# ========================================
def extrair_audio_pcm(path, sr=8000):
    """Extrai áudio mono PCM (s16le) para análise de energia/BPM."""
    cmd = ["ffmpeg", "-v", "error", "-i", str(path),
           "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        dados = proc.stdout.read()
        proc.wait()
        return np.frombuffer(dados, dtype=np.int16).astype(np.float32) / 32768.0
    except Exception:
        return np.array([], dtype=np.float32)

def analisar_audio(samples, sr=8000, janela_seg=0.5):
    """
    Energia RMS por janela + detecção de batidas (BPM estimado).
    Retorna: perfil (lista por segundo), beats, bpm.
    """
    if samples.size == 0:
        return [0.5] * 10, [], 0

    n_janela = max(1, int(sr * janela_seg))
    n_jan = samples.size // n_janela
    if n_jan == 0:
        return [0.5] * 10, [], 0

    frames = samples[: n_jan * n_janela].reshape(n_jan, n_janela)
    energia_jan = np.sqrt(np.mean(np.square(frames), axis=1))
    if energia_jan.max() > 0:
        energia_jan = energia_jan / energia_jan.max()

    # Perfil por segundo
    segundos = int(n_jan * janela_seg)
    perfil = []
    for s in range(segundos):
        ini = int(s / janela_seg)
        fim = max(ini + 1, int((s + 1) / janela_seg))
        chunk = energia_jan[ini:fim]
        perfil.append(float(chunk.mean()) if chunk.size else 0.5)

    # Batidas (picos de energia acima da média local)
    beats = []
    jan_beat = max(4, int(0.35 / janela_seg))
    gap_min = int(0.22 / janela_seg)
    ultimo = -gap_min
    acumulador = []
    media_corrente = 0.0
    for i in range(energia_jan.size):
        acumulador.append(energia_jan[i])
        if len(acumulador) > 30:
            acumulador.pop(0)
        media_corrente = float(np.mean(acumulador)) or 1e-6
        if energia_jan[i] > 1.35 * media_corrente and energia_jan[i] > 0.25:
            if i - ultimo >= gap_min:
                beats.append(i * janela_seg)
                ultimo = i

    # BPM estimado
    bpm = 0
    if len(beats) >= 4:
        intervalos = np.diff(beats)
        mediana = float(np.median(intervalos))
        if mediana > 0.2:
            bpm = round(60 / mediana)

    return perfil, beats, bpm

# ========================================
# ANÁLISE DE FRAMES E CENAS
# ========================================
def analisar_video(path, usar_rosto=True, max_amostras=12000, com_audio=True):
    """
    Pipeline completo de análise visual + auditiva.
    Retorna dicionário com toda a análise.
    """
    info = get_video_info(path)
    d = duracao(info)
    fps = 0
    w, h = 0, 0
    for s in info["streams"]:
        if s["codec_type"] == "video":
            w, h = int(s["width"]), int(s["height"])
            try:
                a, b = s.get("avg_frame_rate", "0/1").split("/")
                fps = float(a) / float(b) if float(b) else 0
            except Exception:
                fps = 0
            break

    analise = {
        "arquivo": str(path),
        "duracao": d,
        "fps": fps,
        "largura": w,
        "altura": h,
        "cenas": [],
        "por_segundo": [],
        "perfil_energia": [],
        "beats": [],
        "bpm": 0,
        "tem_rosto": False,
        "total_rostos": 0,
        "foco": "paisagem",
        "resumo": {},
    }

    # ---------- ÁUDIO ----------
    if com_audio:
        samples = extrair_audio_pcm(path)
        perfil, beats, bpm = analisar_audio(samples)
        analise["perfil_energia"] = perfil
        analise["beats"] = beats
        analise["bpm"] = bpm
        if not perfil:
            analise["perfil_energia"] = [0.5] * max(1, int(d)) 

    # ---------- VISUAL ----------
    if not HAS_CV2 or d <= 0:
        return analise

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        cap.release()
        return analise

    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or d * (fps or 30))
    amostras_alvo = min(n_frames, max_amostras)
    intervalo = max(1, round(n_frames / max(amostras_alvo, 1)))
    intervalo = max(1, intervalo)

    cascade = _carregar_cascade() if usar_rosto else None
    face_intervalo = max(1, intervalo * 5)

    largura_proc = 320
    if w > 0:
        escala = largura_proc / w
        altura_proc = max(1, int(h * escala))
    else:
        escala, altura_proc = 1.0, h

    prev_peq = None
    frame_idx = 0
    n_lido = 0
    rosto_por_seg = {}
    stats_por_seg = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % intervalo != 0:
            frame_idx += 1
            continue

        # Redimensionar para processamento rápido
        if escala != 1.0:
            pequeno = cv2.resize(frame, (largura_proc, altura_proc), interpolation=cv2.INTER_AREA)
        else:
            pequeno = frame
        gray = cv2.cvtColor(pequeno, cv2.COLOR_BGR2GRAY)

        seg = frame_idx / (fps or 30)
        seg_key = int(seg)

        # Movimento (diff temporal)
        movimento = 0.0
        if prev_peq is not None:
            diff = cv2.absdiff(prev_peq, gray)
            movimento = float(diff.mean() / 255.0)
        else:
            movimento = 0.0
        prev_peq = gray

        # Nitidez
        nitidez = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # Contraste e brilho
        contraste = float(gray.std())
        brilho = float(gray.mean())

        # Foco central (movimento no centro vs bordas)
        h2, w2 = gray.shape
        cx, cy = w2 // 2, h2 // 2
        centro = gray[cy - h2 // 4: cy + h2 // 4, cx - w2 // 4: cx + w2 // 4]
        central = 0.0
        if prev_peq is not None:
            dc = cv2.absdiff(prev_peq[cy - h2 // 4: cy + h2 // 4, cx - w2 // 4: cx + w2 // 4], centro)
            central = float(dc.mean() / 255.0)

        s = stats_por_seg.setdefault(seg_key, {
            "movimento": [], "nitidez": [], "contraste": [], "brilho": [], "central": [], "rosto": False
        })
        s["movimento"].append(movimento)
        s["nitidez"].append(nitidez)
        s["contraste"].append(contraste)
        s["brilho"].append(brilho)
        s["central"].append(central)

        # Detecção de rosto (a cada quelques frames)
        if cascade is not None and frame_idx % face_intervalo == 0:
            rostos = cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5,
                minSize=(max(12, altura_proc // 16), max(12, altura_proc // 16))
            )
            if len(rostos) > 0:
                s["rosto"] = True
                rosto_por_seg[seg_key] = len(rostos)

        n_lido += 1
        frame_idx += 1

    cap.release()

    # ---------- DETECÇÃO DE CENAS (boundaries por queda de similaridade) ----------
    cenas = _detectar_cenas_por_seg(stats_por_seg)
    analise["cenas"] = cenas

    # ---------- AGREGAR POR SEGUNDO ----------
    por_seg = []
    todas_nitidez = [np.mean(v["nitidez"]) for v in stats_por_seg.values() if v["nitidez"]]
    todas_contraste = [np.mean(v["contraste"]) for v in stats_por_seg.values() if v["contraste"]]
    max_nit = max(todas_nitidez) if todas_nitidez else 1
    max_cont = max(todas_contraste) if todas_contraste else 1
    medio_energia = analise["perfil_energia"]

    for k in sorted(stats_por_seg.keys()):
        v = stats_por_seg[k]
        nit = (np.mean(v["nitidez"]) / max_nit) if max_nit else 0
        cont = (np.mean(v["contraste"]) / max_cont) if max_cont else 0
        mov = min(1.0, np.mean(v["movimento"]) * 4) if v["movimento"] else 0
        cent = min(1.0, np.mean(v["central"]) * 4) if v["central"] else 0
        energia = medio_energia[k] if k < len(medio_energia) else 0.4
        rosto = 1.0 if v["rosto"] else 0.0
        # Ponderação: foco humano é o sinal nº1
        score = 0.30 * rosto + 0.22 * cent + 0.18 * mov + 0.15 * energia + 0.10 * nit + 0.05 * cont
        por_seg.append({
            "segundo": int(k),
            "movimento": float(np.float64(mov)),
            "nitidez": float(nit),
            "contraste": float(cont),
            "energia": float(energia),
            "central": float(cent),
            "rosto": bool(v["rosto"]),
            "score": float(score),
        })

    analise["por_segundo"] = por_seg
    analise["tem_rosto"] = any(x["rosto"] for x in por_seg)
    analise["total_rostos"] = sum(1 for x in por_seg if x["rosto"])
    analise["foco"] = "pessoas" if analise["tem_rosto"] else ("acao" if (por_seg and np.mean([x["movimento"] for x in por_seg]) > 0.25) else "paisagem")

    # ---------- RESUMO ----------
    analise["resumo"] = {
        "frames_analisados": n_lido,
        "amostras_por_segundo": round(n_lido / max(d, 1), 1),
        "foco_detectado": analise["foco"],
        "segundos_com_rosto": analise["total_rostos"],
        "cenas_detectadas": len(cenas),
        "bpm_estimado": analise["bpm"],
    }

    return analise

def _detectar_cenas_por_seg(stats_por_seg):
    """Detecta mudanças de cena pela variação de brilho/movimento entre segundos."""
    chaves = sorted(stats_por_seg.keys())
    if len(chaves) < 2:
        return [{"inicio": 0.0, "fim": float(len(stats_por_seg) or 1), "score": 0.2}]

    cenas = []
    inicio = 0.0
    brilho_anterior = np.mean(stats_por_seg[chaves[0]]["brilho"]) if stats_por_seg[chaves[0]]["brilho"] else 127
    score_acum = 0.2

    for i, k in enumerate(chaves[:-1]):
        v_atual = stats_por_seg[k]
        v_prox_raw = stats_por_seg[chaves[i + 1]]
        brilho_atual = np.mean(v_atual["brilho"]) if v_atual["brilho"] else 127
        brilho_prox = np.mean(v_prox_raw["brilho"]) if v_prox_raw["brilho"] else 127
        salto = abs(brilho_prox - brilho_atual) / 255.0
        corte = salto > 0.22
        if corte:
            cenas.append({"inicio": inicio, "fim": float(k + 1), "score": max(0.1, score_acum)})
            inicio = float(k + 1)
            score_acum = 0.2
        else:
            score_acum += salto * 0.5
        brilho_anterior = brilho_prox

    cenas.append({"inicio": inicio, "fim": float(chaves[-1] + 1), "score": max(0.1, score_acum)})
    return cenas

# ========================================
# SCORE DOS SEGMENTOS (cenas)
# ========================================
def pontuar_segmentos(analise):
    """Atribui nota (0-1) e metadados a cada cena do vídeo."""
    por_seg = analise.get("por_segundo", [])
    sem = {x["segundo"]: x for x in por_seg}
    segmentos = []
    for c in analise.get("cenas", []):
        ini, fim = int(c["inicio"]), max(int(c["fim"]), int(c["inicio"]) + 1)
        scores = [sem[s] for s in range(ini, min(fim, max(sem.keys()) + 1)) if s in sem]
        if not scores:
            scores = [{"movimento": 0.1, "energia": 0.3, "score": 0.15, "rosto": False,
                       "central": 0.1, "nitidez": 0.2}]
        segmentos.append({
            "inicio": c["inicio"],
            "fim": c["fim"],
            "duracao": c["fim"] - c["inicio"],
            "score_cena": round(float(np.mean([s["score"] for s in scores])), 3),
            "energia": round(float(np.mean([s["energia"] for s in scores])), 3),
            "tem_rosto": any(s.get("rosto") for s in scores),
            "foco_humano": round(float(np.mean([s["score"] if s.get("rosto") else 0 for s in scores])), 3),
        })
    return segmentos

# ========================================
# SELEÇÃO AUTOMÁTICA DE CENAS PARA O REEL
# ========================================
def _norm(v):
    """Converte numerics numpy para float/int puro."""
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, (bool, int, float)):
        return v
    return v

def selecionar_cenas(analise, duracao_alvo, max_shots=7, janela_por_cena=None):
    """
    Escolhe os melhores CORTES para montar o Reel.

    Funciona mesmo em vídeos de uma única cena longa:
    gera janelas candidatas a cada 0.5s, pontua pela relevância
    (foco humano + energia + movimento) e escolhe as melhores sem
    sobreposição — criando ritmo de edição automaticamente.
    """
    por_seg = analise.get("por_segundo", [])
    dur = analise.get("duracao", 0) or max(por_seg[-1]["segundo"] + 1 if por_seg else 1, 1)

    if not por_seg:
        return [{"inicio": 0.0, "fim": min(duracao_alvo, dur),
                 "score": 0.2, "tem_rosto": False, "energia": 0.4}]

    # Janela de cada corte
    janela = janela_por_cena or max(1.5, min(4.0, duracao_alvo / max_shots))

    # Candidatos: janelas deslizantes de 0.5s
    candidatos = []
    passos = 0.5
    inicio_max = max(dur - janela, 0.01)
    inicio = 0.0
    while inicio <= inicio_max and len(candidatos) < 400:
        vals = [x for x in por_seg if inicio <= x["segundo"] < inicio + janela]
        if vals:
            rosto = any(x["rosto"] for x in vals)
            energia = float(np.mean([x["energia"] for x in vals]))
            movimento = float(np.mean([x["movimento"] for x in vals]))
            base = float(np.mean([x["score"] for x in vals]))
            bonus_foco = 0.18 if rosto else 0.06
            bonus_energia = energia * 0.12
            bonus_mov = min(movimento, 0.3) * 0.15
            candidatos.append({
                "inicio": inicio,
                "fim": min(inicio + janela, dur),
                "score": base + bonus_foco + bonus_energia + bonus_mov,
                "tem_rosto": rosto,
                "energia": energia,
            })
        inicio += passos

    candidatos.sort(key=lambda x: x["score"], reverse=True)

    # Seleção gulosa sem sobreposição
    escolhidos = []
    for c in candidatos:
        if any(c["inicio"] < e["fim"] and c["fim"] > e["inicio"] for e in escolhidos):
            continue
        if c["fim"] - c["inicio"] < 0.6:
            continue
        escolhidos.append(c)
        if len(escolhidos) >= max_shots:
            break

    if not escolhidos:
        escolhidos = [{"inicio": 0.0, "fim": min(duracao_alvo, dur),
                       "score": 0.2, "tem_rosto": False, "energia": 0.4}]

    # Ordenar cronologicamente (fluidez de edição)
    escolhidos.sort(key=lambda x: x["inicio"])

    # Ajustar duração total ao alvo (expandir/encolher proporcionalmente)
    total = sum(x["fim"] - x["inicio"] for x in escolhidos)
    if total > duracao_alvo:
        prop = duracao_alvo / total
        escolhidos = [{**x, "fim": x["inicio"] + (x["fim"] - x["inicio"]) * prop}
                      for x in escolhidos]
    elif total < duracao_alvo and escolhidos:
        # esticar suavemente: distribuir o tempo extra nos cortes ao redor dos melhores
        falta = duracao_alvo - total
        # crescer a janela de cada corte (sem passar do fim do vídeo)
        novo = []
        for x in escolhidos:
            extra = falta / len(escolhidos)
            x = dict(x)
            x["fim"] = min(dur, x["fim"] + extra)
            novo.append(x)
        escolhidos = novo

    return [{**x, "score": x["score"]} for x in escolhidos]

# ========================================
# EXIBIÇÃO AMIGÁVEL
# ========================================
def resumo_analise(analise, top=8):
    """Gera texto resumido da análise para exibição."""
    from .cores import Cores
    C = Cores
    r = analise["resumo"]
    linhas = []
    linhas.append(f"\n{C.NEGRITO}{C.CIANO}{'═' * 58}{C.RESET}")
    linhas.append(f"{C.NEGRITO}🔍 ANÁLISE DO VÍDEO — O QUE O PROGRAMA ENXERGA{C.RESET}")
    linhas.append(f"{C.CIANO}{'═' * 58}{C.RESET}")
    linhas.append(f"   🎯 Foco detectado: {C.NEGRITO}{r['foco_detectado']}{C.RESET}")
    linhas.append(f"   🎞️  Cenas detectadas: {r['cenas_detectadas']}")
    linhas.append(f"   👤 Segundos com rosto: {r['segundos_com_rosto']}")
    linhas.append(f"   🎵 BPM estimado: {analise['bpm'] or 'n/d'}")
    linhas.append(f"   ⏱️  Duração: {analise['duracao']:.1f}s")

    melhores = sorted(analise.get("por_segundo", []), key=lambda x: x["score"], reverse=True)[:top]
    if melhores:
        linhas.append(f"\n   🏆 {C.NEGRITO}Top momentos (segundos):{C.RESET}")
        for m in melhores:
            rosto = "👤" if m["rosto"] else "  "
            linhas.append(f"      {rosto} {m['segundo']:>5}s  score {m['score']:.2f}  "
                          f"mov {m['movimento']:.2f}  energia {m['energia']:.2f}")
    return "\n".join(linhas)