# 🎬 NANDALIN — Processador de Vídeos Premium 8K

## 🤖 NOVO: NANDALIN AI (Reels & Stories automáticos)

> **Analisa o que está em alta, entende o algoritmo do Instagram e cria
> Reels/Stories sozinho — pensa, cria, avalia e aprimora.**

```bash
python nandalin_ia.py --video input_video.mp4
```

Documentação completa: [README_NANDALIN_IA.md](README_NANDALIN_IA.md)

## 🎯 Prioridade #1: Qualidade Máxima 8K

Todos os scripts processam vídeos com **qualidade máxima** até **8K (7680x4320)** usando:

| Parâmetro | Configuração |
|-----------|-------------|
| **Upscaling** | Lanczos (melhor algoritmo de interpolação) |
| **Codec** | HEVC (libx265) 10-bit |
| **CRF** | 15 (quase lossless) |
| **FPS** | 60fps |
| **Áudio** | AAC 320kbps 48kHz |
| **Nitidez** | Unsharp mask dupla (pós-upscale) |
| **Denoise** | NLMeans s=4 |
| **Saturação** | +50% |
| **Contraste** | +25% |
| **Gamma** | 0.95 |
| **Curvas** | Cinematográficas |
| **Balanceamento** | Cores profissional |

## 📦 Instalação

```bash
pip install gdown opencv-python numpy
```

## 🚀 Uso Rápido

### Opção 1: Menu Interativo (recomendado)
```bash
python baixar_e_processar.py
```
→ Menu com opções para baixar do Drive, processar 8K, configurar, etc.

### Opção 2: Linha de Comando
```bash
# Baixar todos os vídeos do Drive
python baixar_e_processar.py --baixar-todos

# Processar vídeo em Story 8K (9:16)
python baixar_e_processar.py --arquivo "video.mp4" --modo story

# Processar em Original 8K (mantém ratio)
python baixar_e_processar.py --arquivo "video.mp4" --modo original

# Listar vídeos baixados
python baixar_e_processar.py --listar

# Configurações avançadas
python baixar_e_processar.py --arquivo "video.mp4" --resolucao 4k --codec libx264 --crf 18 --fps 30
```

### Opção 3: Processamento com Edição Inteligente
```bash
python edicao_inteligente.py "video.mp4"
```
→ Analisa cenas, encontra melhores momentos, faz cortes inteligentes e processa em 8K.

### Opção 4: Script Simples
```bash
python processar_video.py "video.mp4"
```
→ Processamento rápido com pipeline 8K completo.

## 📁 Estrutura

```
Nandalin/
├── baixar_e_processar.py    # Script principal (menu + Drive + 8K)
├── processar_video.py       # Processador 8K direto
├── edicao_inteligente.py    # Edição com IA + 8K
├── criar_pasta_google_drive.py  # Organizar Drive
├── nandalin_ia.py           # 🤖 NANDALIN AI (Reels/Stories automáticos)
├── nandalin_ai/             # Motor do NANDALIN AI (algoritmo, tendências, análise, montagem)
├── landing_page.html        # Página de vendas premium
├── roteiro_video_vendas.md  # Roteiro de vendas
├── plano_marketing.md       # Plano de marketing
├── videos_originais/        # Vídeos baixados do Drive
├── videos_stories_8k/       # Vídeos processados Story 9:16
├── videos_processados_8k/   # Vídeos processados Original
└── saidas_ia/               # 🤖 Reels criados pelo NANDALIN AI
```

## ⚙️ Resoluções Suportadas

| Resolução | Dimensões (16:9) | Dimensões (9:16) |
|-----------|------------------|------------------|
| **8K** | 7680 × 4320 | 4320 × 7680 |
| **4K** | 3840 × 2160 | 2160 × 3840 |
| **2K** | 2560 × 1440 | 1440 × 2560 |

## 🔧 Configurações Disponíveis

| Parâmetro | Comando | Valores |
|-----------|---------|---------|
| Modo | `--modo` | `story`, `original`, `fit-8k` |
| Resolução | `--resolucao` | `8k`, `4k`, `2k`, `auto` |
| Codec | `--codec` | `libx265`, `libx264` |
| Qualidade | `--crf` | `0-51` (menor = melhor) |
| FPS | `--fps` | `24`, `30`, `60`, `120` |

## 🔗 Google Drive

Vídeos são baixados automaticamente da pasta compartilhada:
https://drive.google.com/drive/folders/1f2xZSV4YjFIrYHw8I89NNUcS6GpO0V_e

---

**NANDALIN** — Conteúdo premium para público premium. 🎬✨
