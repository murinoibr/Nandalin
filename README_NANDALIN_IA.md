# 🤖 NANDALIN AI — Cérebro de Criação de Reels & Stories

> **Um programa profissional que analisa o que está em alta, entende o
> algoritmo do Instagram e cria os vídeos POR VOCÊ — sem você precisar
> fazer quase nada. Ele pensa, cria, avalia e aprimora.**

```
python nandalin_ia.py --video input_video.mp4
```

---

## 🧠 O que o programa faz (5 fases)

| Fase | Nome | O que acontece |
|------|------|----------------|
| 0 | **ASSISTIR** | O programa assiste seu vídeo e enxerga: cenas, rostos (foco humano), movimento, energia do áudio, BPM |
| 1 | **PENSAR** | Busca o que está em alta (Google Trends Brasil em tempo real) e escolhe tema + hook + estratégia |
| 2 | **CRIAR** | Monta o Reel automaticamente: cortes nos melhores momentos, zoom cinematográfico, hook em texto, legendas |
| 3 | **AVALIAR** | Mede o potencial de engajamento (0–100) contra as regras do algoritmo |
| 4 | **APRIMORAR** | Gera várias variantes (A/B test) com hooks e efeitos diferentes e escolhe a melhor |

No final, ele entrega **o vídeo pronto + a legenda pronta + hashtags + o melhor
horário para postar + o plano estratégico**. Você só publica.

---

## 🚀 Instalação

```bash
pip install requests opencv-python numpy
```

Requisitos de sistema: **ffmpeg** e **ffprobe** (completos), Python 3.9+.

O modelo de detecção de rosto já vem incluído em `nandalin_ai/data/`.

---

## ⚡ Uso rápido

### 1. Tudo automático (menu interativo)

```bash
python nandalin_ia.py
```

Escolha a opção **1 — Assistente IA COMPLETO**.

### 2. Linha de comando

```bash
# Assistente completo com o vídeo
python nandalin_ia.py --video video.mp4

# Criar 5 variantes em 4K
python nandalin_ia.py --video video.mp4 --variantes 5 --resolucao 4k

# Para conteúdo viral (hook forte, 12s)
python nandalin_ia.py --video video.mp4 --objetivo viral

# Focar em um nicho
python nandalin_ia.py --video video.mp4 --nicho fitness

# Sem internet (usa banco local de tendências)
python nandalin_ia.py --video video.mp4 --offline

# Com tema/alerta manual
python nandalin_ia.py --video video.mp4 --tema "Segredo do algoritmo"

# Com música de fundo
python nandalin_ia.py --video video.mp4 --musica minha_musica.mp3

# Apenas ver o que está em alta
python nandalin_ia.py --trends

# Apenas relatório do algoritmo
python nandalin_ia.py --algoritmo

# Apenas analisar um vídeo
python nandalin_ia.py --analise --video video.mp4
```

### 3. Comandos do menu

```
[1] 🤖 Assistente IA COMPLETO (tudo automático)
[2] 📈 O que está em ALTA (tendências)
[3] 🎬 Analisar um vídeo (foco e melhores momentos)
[4] 🧠 Entender o algoritmo do Instagram
[5] ✂️  Criar Reel/Story de um vídeo (com variantes)
[6] ⚙️  Configurações (objetivo, nicho, geo, resolução, variantes, música)
[7] 🚀 Finalizar em 8K (pipeline premium)
[0] 🚪 Sair
```

---

## 📁 Estrutura

```
nandalin_ia.py            ← lançador (use isso)
nandalin_ai/              ← motor do programa
├── algoritmo.py          ← 🧠 conhecimento do algoritmo + pontuação
├── tendencias.py         ← 📈 Google Trends + banco local + hooks
├── analise.py            ← 🔍 visão do vídeo (foco, cenas, energia, BPM)
├── montagem.py           ← ✂️ editor automático (zoom, textos, cortes)
├── cerebro.py            ← 🤖 orquestrador: pensar→criar→avaliar→aprimorar
├── cli.py                ← 🖥️ menu + linha de comando
├── util.py / cores.py    ← infraestrutura
└── data/                 ← modelo de detecção de rosto
saidas_ia/                ← 📦 Reels criados pelo programa
temp_ia/                  ← arquivos temporários (limpos automaticamente)
```

---

## ⚙️ Configurações disponíveis

| Config | Valores | Padrão |
|--------|---------|--------|
| Objetivo | `alcance`, `viral`, `engajamento`, `autoridade`, `vendas` | `alcance` |
| Nicho | `geral`, `fitness`, `receitas`, `financeiro`, `viagem`, `tech`, `moda`, `humor`, `educacao`, `marketing`, `beleza`, `familia`, `games`, `animais` | `geral` |
| Resolução | `hd` (1080x1920), `4k`, `8k` | `hd` |
| Variantes | 1–9 (A/B test) | 3 |
| Região | `BR`, `US`, `PT`... | `BR` |
| Música | caminho de arquivo | nenhuma |
| Internet | on/off | on |

---

## 🧠 Como o algoritmo do Instagram é usado

O programa carrega o conhecimento atual de como o IG ranqueia Reels:

1. **Sinais de ranking** — tempo de exibição, re-exibição, conclusão,
   compartilhamento, salvamento, comentário.
2. **Regras de ouro** — hook nos 1–2 primeiros segundos, duração 7–15s,
   formato vertical 9:16, legibilidade sem som, áudio em alta, sem marca
   d'água de outras plataformas.
3. **Estrutura de retenção** — Hook → Contexto → Desenvolvimento → CTA.
4. **Pontuação do vídeo criado** — duração vs ideal, ritmo de cortes, energia,
   presença humana, dinamismo, completude.

⚠️ *O algoritmo muda constantemente. Este relatório usa padrões públicos de
engenharia do Instagram; suas métricas reais de perfil são o melhor guia.*

> 💾 **Memória para alta resolução:** o modo `hd` (1080x1920) roda em qualquer
> máquina. Os modos `4k` e `8k` exigem **16 GB+ de RAM** (o zoom cinematográfico
> processa frames enormes). Em máquinas modestas, use `hd` e depois finalize
> em 8K pela opção 7 do menu (pipeline separado).

---

## 📈 Como as tendências funcionam

- **Com internet:** busca as tendências reais do dia no **Google Trends**
  (Brasil por padrão) e classifica a categoria de cada uma.
- **Sem internet:** usa o **banco local curado** de tendências por nicho.
- O tema escolhido vira **6 hooks prontos**, **3 ângulos criativos**,
  **legenda completa** e **hashtags estratégicas**.

---

## ✂️ Como o vídeo é criado

1. O programa **assiste** cada segundo do vídeo e pontua:
   - presença de rosto (foco humano) — o sinal mais forte
   - movimento dinâmico
   - nitidez e contraste
   - energia do áudio (volume real) e BPM
2. Escolhe os **melhores cortes** espalhados no vídeo.
3. Monta o Reel: **hook em texto grande** no primeiro corte, **zoom
   cinematográfico** (in/out) alternado, **fades**, **legendas dinâmicas**.
4. Cria **variantes** com hooks e efeitos diferentes.
5. **Avalia cada uma** e mostra o ranking com o potencial de engajamento.

---

## 🚀 Integração com o pipeline 8K

Use o menu **opção 7** para finalizar o Reel vencedor em **8K premium**
(reutiliza o `baixar_e_processar.py` do projeto: upscale Lanczos, HEVC 10-bit,
CRF 15, 60fps).

Ou direto:

```bash
python baixar_e_processar.py --arquivo "saidas_ia/seu_reel.mp4" --modo story --resolucao 8k
```

---

## 🧪 Testes rápidos

```bash
# Teste de importação e lógica
python3 -c "from nandalin_ai import algoritmo, tendencias, analise, montagem, cerebro"

# Teste completo de ponta a ponta (offline)
python nandalin_ia.py --video input_video.mp4 --offline --variantes 2
```

---

**NANDALIN AI** — Conteúdo premium para público premium. 🎬✨