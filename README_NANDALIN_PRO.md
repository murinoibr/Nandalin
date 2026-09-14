# 🎬 NANDALIN PRO — Melhoria de Vídeo com IA

Aplicativo web profissional para **melhorar a qualidade de vídeos para 4K e 8K** com **edição inteligente automatizada** por IA.

![Pipeline: Upload → Análise IA → Configuração → Processamento → Download](https://img.shields.io/badge/Flask-WebApp-blue) ![FFmpeg](https://img.shields.io/badge/FFmpeg-Video-green) ![IA](https://img.shields.io/badge/IA-OpenCV-purple)

---

## ✨ Funcionalidades

### 🧠 Análise Inteligente com IA
- Detecta automaticamente **cenas** e **mudanças de cena**
- Avalia **qualidade visual** de cada segmento (nitidez, contraste, brilho)
- Encontra os **melhores momentos** do vídeo
- Gera **recomendações personalizadas** (upscale, nitidez, contraste, cortes)

### ⬆️ Upscaling Profissional 4K / 8K
- **4K Ultra HD** (3840×2160)
- **8K Ultra HD** (7680×4320)
- Algoritmo **Lanczos** (melhor qualidade de interpolação)
- Codec **HEVC (libx265)** 10-bit com CRF 15 (quase lossless)
- Suporte a 60 FPS e áudio AAC 320kbps

### 🎛️ Edição Profissional Automatizada
- **8 presets profissionais** prontos (Cinematográfico, Ultra 8K, Story, Vibrante, Noturno, Suave, Dramático, Vintage)
- Controle total de **cor & tons**: brilho, contraste, saturação, gamma, temperatura
- **Redução de ruído** avançada (NLMeans)
- **Nitidez** cinematográfica dupla (unsharp mask)
- **Balanceamento de cores** profissional
- **Curvas cinematográficas** (cross-process, vintage, alto contraste)
- **Vinheta** para look premium
- Modo **Story 9:16** para Instagram/TikTok/YouTube Shorts

---

## 🚀 Instalação

```bash
# 1. Dependências Python
pip install flask opencv-python numpy

# 2. FFmpeg (necessário para processamento)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg
# Windows: https://ffmpeg.org/download.html

# 3. Iniciar
python app.py
```

Acesse: **http://localhost:5000**

---

## 📖 Como Usar

### 1. Carregar Vídeo
Arraste o vídeo para a área de upload (até 4GB) — MP4, AVI, MOV, MKV, WebM.

### 2. Analisar com IA
O sistema analisa cenas, qualidade e gera recomendações personalizadas.

### 3. Escolher Preset ou Configurar
Selecione um preset profissional (ex: **Ultra 8K**) ou ajuste manualmente cada parâmetro.

### 4. Processar
Clique em **Iniciar Processamento**. Acompanhe o progresso em tempo real e baixe o resultado em 4K/8K.

---

## ⚙️ Parâmetros Configuráveis

| Parâmetro | Faixa | Padrão | Descrição |
|-----------|-------|--------|-----------|
| **Resolução** | 2K / 4K / 8K | 4K | Resolução alvo de upscale |
| **Modo** | Original / Story | Original | 16:9 ou 9:16 para Reels/Stories |
| **Codec** | HEVC / AVC | HEVC | HEVC = melhor qualidade, AVC = compatibilidade |
| **CRF** | 0–51 | 18 | Menor = melhor qualidade (15 = quase lossless) |
| **FPS** | 24/30/60 | 60 | Frame rate da saída |
| **Brilho** | -50% a +50% | +3% | Correção de exposição |
| **Contraste** | -100% a +100% | +25% | Contraste de imagem |
| **Saturação** | -100% a +200% | +50% | Intensidade de cores |
| **Gamma** | 0.5–1.5 | 0.95 | Curva de tons (menor = mais claro) |
| **Temperatura** | 2000K–10000K | 5500K | Balanço de branco |
| **Denoise** | 1–7 | 4 | Força da redução de ruído |
| **Nitidez** | Ligado/Desligado | Ligado | Unsharp mask profissional |
| **Curvas** | Várias opções | Cross-process | Look cinematográfico |

---

## 🎨 Presets Incluídos

| Preset | Uso Ideal |
|--------|-----------|
| 🎬 **Cinematográfico 4K** | Vídeos com look de cinema profissional |
| 🏆 **Ultra 8K** | Qualidade máxima absoluta em 8K |
| 📱 **Story 4K** | Reels, Stories, TikTok e Shorts |
| 🌈 **Vibrante** | Vídeos de produto, conteúdo colorido |
| 🌙 **Noturno** | Cenas escuras, shows, casas noturnas |
| 🎨 **Suave** | Retratos, conteúdo natural |
| 🎭 **Dramático** | Trailer, vídeos de impacto |
| 📷 **Retro** | Look vintage/analógico |

---

## 🧠 Como a IA Funciona

1. **Detecção de Cenas**: Compara frames consecutivos com OpenCV para detectar mudanças de cena.
2. **Análise de Qualidade**: Avalia nitidez (Laplacian), contraste (desvio padrão) e exposição (brilho médio) de cada porção do vídeo.
3. **Recomendações**: Com base na análise, sugere configurações ideais:
   - Resolução baixa → sugere upscale 4K/8K
   - Nitidez baixa → sugere unsharp mask
   - Contraste baixo → sugere curvas cinematográficas
   - Muitas cenas → sugere cortes inteligentes
4. **Processamento**: Pipeline FFmpeg otimizado: Crop → Upscale Lanczos → Denoise → Nitidez → Cores → Encode HEVC 10-bit.

---

## 🗂️ Estrutura

```
Nandalin/
├── app.py                  # Backend Flask (API + processamento)
├── templates/
│   └── index.html          # Interface web
├── static/
│   ├── style.css           # Estilos profissionais
│   └── app.js              # Lógica do frontend
├── uploads/                # Vídeos enviados
├── processed/              # Vídeos processados
└── temp_web/               # Arquivos temporários
```

---

## 📋 Requisitos

- Python 3.8+
- FFmpeg (com libx265 e libx264)
- Flask, OpenCV, NumPy

---
**NANDALIN PRO** — Conteúdo premium para público premium. 🎬✨