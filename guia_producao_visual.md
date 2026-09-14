# 🎨 GUIA DE PRODUÇÃO VISUAL — Story Premium NANDALIN
## Storyboard Executivo + Direção de Arte

---

## 📐 ESPECIFICAÇÕES TÉCNICAS

```
Formato:          9:16 (vertical)
Resolução:        4320 x 7680 (8K vertical)
FPS:              60fps
Codec:            HEVC (libx265) 10-bit
CRF:              15 (quase lossless)
Pixel Format:     yuv420p10le
Duração:          30s (curta) / 60s (completa)
Áudio:            AAC 320kbps / 48kHz
```

---

## 🎬 STORYBOARD VISUAL — CENA A CENA

### CENA 1: O GANCHO SILENCIOSO
** Tempo: 0:00 — 0:03 | Duração: 3 segundos**

```
┌─────────────────────┐
│                     │
│     [PRETO]         │
│                     │
│   Toda lona de      │
│   caminhão tem      │
│   uma história.     │
│                     │
│                     │
│  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ │  ← Gradiente dourado sutil no fundo
│                     │
└─────────────────────┘
```

**Direção de Fotografia:**
- Fundo: Preto absoluto (#0A0A0A)
- Texto: Dourado (#C9A962), fonte serif (Playfair Display)
- Animação: Texto aparece letterSpacing por letterSpacing (efeito máquina de escrever elegante)
- Iluminação: Nenhuma (texto brilhante sobre fundo escuro)
- Transição para próxima cena: Fade through black (0.5s)

**Comando FFmpeg para-processamento:**
```bash
# Texto com fade in
-vf "drawtext=text='Toda lona de caminhão tem':fontcolor=0xC9A962:fontsize=60:x=(w-text_w)/2:y=h/2-60:enable='between(t,0.5,3)':alpha='if(lt(t,1),(t-0.5)*2,1)'"
```

---

### CENA 2: O DESPERTAR
**Tempo: 0:03 — 0:08 | Duração: 5 segundos**

```
┌─────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░ │
│ ░░ CÉU NUBLADO ░░░ │  ← Luz natural, tons cinza/azul
│ ░░░░░░░░░░░░░░░░░░░ │
│                     │
│   ╔═════════════╗   │
│   ║  LONA SUJA  ║   │  ← Close-up: textura da lona rasgada
│   ║  RASGADA    ║   │     Filtro terroso, desaturado
│   ║  ABANDONADA ║   │
│   ╚═════════════╝   │
│                     │
│ "Descartada.        │
│  Esquecida.         │
│  Sem valor."        │
│                     │
│ 🌿 (mato crescendo) │  ← Elemento visual: natureza reagindo
└─────────────────────┘
```

**Direção de Fotografia:**
- Local: Estrada ou área rural com lona de caminhão velha
- Iluminação: Natural, nublada (difusa), tons frios
- Câmera: Tripé, zoom in lento (keyframe: 100% → 105% em 5s)
- Profundidade de campo: Foco na textura da lona, fundo desfocado
- Correção de cor: Desaturar 30%, adicionar tom azulado, reduzir brilho
- Elemento de composição: Mato ou ferrugem visível (natureza vs. industrial)

**Refência visual:** Fotografia de Edward Weston (detalhe de texturas)

---

### CENA 3: A TRANSFORMAÇÃO (3-4 shots)
**Tempo: 0:08 — 0:15 | Duração: 7 segundos**

**Shot 3A: O CORTE (0:08 — 0:10)**
```
┌─────────────────────┐
│                     │
│    MÃOS de          │
│    artesão          │
│    cortando         │
│    ┌───────────┐    │
│    │ LONA NOVA │    │  ← Lona limpa, diferente da Cena 2
│    │ ✂️ TESOURA│    │
│    └───────────┘    │
│                     │
│  (Close-up extremo) │
│                     │
└─────────────────────┘
```

**Shot 3B: A COSTURA (0:10 — 0:12)**
```
┌─────────────────────┐
│                     │
│   ⚙️ MÁQUINA DE     │
│      COSTURA        │
│                     │
│   ╔═══════════╗     │
│   ║ Needle ═══╬══►  │  ← Macro da agulha entrando na lona
│   ║     ↓↓↓↓  ║     │     Costura perfeita, linha dourada
│   ╚═══════════╝     │
│                     │
│  (Macro lens)       │
│                     │
└─────────────────────┘
```

**Shot 3C: O ACABAMENTO (0:12 — 0:14)**
```
┌─────────────────────┐
│                     │
│   Detalhe da        │
│   FIVELA DOURADA    │
│                     │
│      ╔═══╗         │
│      ║ ◆ ║         │  ← Close-up: fivela dourada brilhando
│      ╚═══╝         │     Alça costurada perfeitamente
│   ▓▓▓▓▓▓▓▓▓▓▓▓▓   │  ← Textura da lona premium
│                     │
│  (Depth of field    │
│   extremamente      │
│   raso)             │
└─────────────────────┘
```

**Shot 3D: O POLIMENTO (0:14 — 0:15)**
```
┌─────────────────────┐
│                     │
│   Mãos passando     │
│   pano suave na     │
│   bolsa pronta      │
│                     │
│   ✨ BRILHO ✨     │  ← Efeito de brilho sutil
│                     │
│  (Close-up, mãos   │
│   femininas eleg.)  │
└─────────────────────┘
```

**Direção de Fotografia para todas shots:**
- Iluminação: Quente (3200K), luz lateral dramatica
- Câmera: Estável (gimbal ou tripod), movimentos suaves
- Correção: Tons quentes, saturação aumentando gradualmente (20% → 40%)
- Texto: "Mãos que transformam o descartável em arte." (aparece em Shot 3B)
- Áudio: Sons reais da oficina mixados com piano

---

### CENA 4: O REVEAL
**Tempo: 0:15 — 0:22 | Duração: 7 segundos**

**Shot 4A: A REVELAÇÃO (0:15 — 0:18)**
```
┌─────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░ │
│ ░ FUNDO ESCURO ░░░ │  ← Preto premium, leve haze dourado
│ ░░░░░░░░░░░░░░░░░░░ │
│                     │
│     ╔═════════╗     │
│     ║         ║     │
│     ║ BOLSA   ║     │  ← Produto central, iluminação dramática
│     ║ NANDALIN║     │     Chiaroscuro (luz/sombra contrastante)
│     ║         ║     │
│     ╚═════════╝     │
│                     │
│     3/4 VIEW        │  ← Ângulo mais favorecedor
│     Leve giro       │     Câmera orbital (90° em 3s)
│                     │
└─────────────────────┘
```

**Shot 4B: DETALHE DO MATERIAL (0:18 — 0:20)**
```
┌─────────────────────┐
│                     │
│  Textura da lona    │
│  premium vista de   │
│  pertinho:          │
│                     │
│  ▓▓▓▒▒▒▓▓▓▒▒▒▓▓▓  │  ← Macro da textura
│  ▓▓▓▒▒▒▓▓▓▒▒▒▓▓▓  │     Cada fio visível
│  ▓▓▓▒▒▒▓▓▓▒▒▒▓▓▓  │     Qualidade 8K brilha aqui
│                     │
│  "Feito para quem   │
│  não aceita menos"  │
│                     │
└─────────────────────┘
```

**Shot 4C: DETALHE DA ALÇA (0:20 — 0:22)**
```
┌─────────────────────┐
│                     │
│   Close-up da alça  │
│   e fivela:         │
│                     │
│   ◆═══════════◆    │  ← Fivela dourada
│   ║ ALÇA ═════║    │     Alça com costura perfeita
│   ◆═══════════◆    │     Brilho metálico sutil
│                     │
│  "Arte na Lona."    │
│                     │
│  (Foco se move da  │
│   fivela para alça) │
└─────────────────────┘
```

**Direção de Fotografia:**
- Fundo: Preto (#0A0A0A) com leve haze dourado no fundo
- Iluminação: KEY light lateral direita (quente), FILL light suave esquerda
- Profundidade de campo: Muito rasa (f/1.4 — f/2.0)
- Movimento: Orbital suave (gimbal), nunca estático
- Correção: Tons quentes premium, alto contraste, sombras profundas
- Texto: "Arte na Lona." aparece e some → "NANDALIN" fica

**Refência visual:** Fotografia de produto Apple (clean, premium, dramática)

---

### CENA 5: PROVA SOCIAL SILENCIOSA
**Tempo: 0:22 — 0:27 | Duração: 5 segundos**

```
┌─────────────────────┐
│                     │
│   PESSOA            │
│   sofisticada       │
│   de costas/lado    │
│                     │
│   ╔═══╗             │
│   ║ B ║ ← Bolsa     │  ← Pessoa usando a bolsa naturalmente
│   ║ O ║   Nandalin  │     Ambiente: galeria ou café premium
│   ║ L ║             │     Estilo: elegante, não ostentação
│   ╚═══╝             │
│                     │
│   ████████████████  │  ← Ambiente sofisticado ao fundo
│                     │
│  "Para quem entende │
│   a diferença."     │
│                     │
│   (Slow motion)     │
└─────────────────────┘
```

**Direção de Fotografia:**
- Local: Galeria de arte, café sofisticado, ou escritório moderno
- Pessoa: Estilo street fashion elegante (não modelo — pessoa real)
- Câmera: Plano médio, pessoa se afastando (slow motion 120fps → 60fps)
- Iluminação: Natural com fill light
- Correção: Tons naturais, levemente dourados
- Texto: "Para quem entende a diferença."

---

### CENA 6: ESCASSEZ ELEGANTE
**Tempo: 0:27 — 0:29 | Duração: 2 segundos**

```
┌─────────────────────┐
│                     │
│                     │
│   Edição Limitada   │  ← Dourado, serif, elegante
│                     │
│   Produzido à mão.  │  ← Fonte menor, branca
│   Em séries         │
│   numeradas.        │
│                     │
│                     │
│   ─────── ◆ ────── │  ← Separador dourado
│                     │
└─────────────────────┘
```

**Direção de Fotografia:**
- Fundo: Preto puro
- Texto: Dourado (#C9A962) para título, branco (#F5F5F5) para subtítulo
- Animação: Fade in (0.3s) → Hold (1.4s) → Fade out (0.3s)
- Sem efeitos extras — elegância é simplicidade

---

### CENA 7: O CTA
**Tempo: 0:29 — 0:30 | Duração: 1 segundo**

```
┌─────────────────────┐
│                     │
│                     │
│      N A N         │
│      D A L I N     │  ← Logo Nandalin
│                     │
│   ✦ Arte na Lona ✦ │  ← Tagline
│                     │
│   nandalin.com.br   │  ← Link discreto
│                     │
│                     │
└─────────────────────┘
```

**Direção de Fotografia:**
- Fundo: Preto
- Logo: Dourado, fonte display, letter-spacing amplo
- Animação: Logo aparece com leve brilho (glow effect)
- Áudio: Nota final do piano + fade out

---

## 🎨 PALETA DE CORES COMPLETA

### Cores Primárias:
```css
PRETO PREMIUM:    #0A0A0A  /* Fundos, contrastes */
OURO NANDALIN:    #C9A962  /* Textos principais, destaques */
BRANCO QUEBRADO:  #F5F5F5  /* Textos secundários */
```

### Cores Secundárias:
```css
TERRA COTA:       #8B6914  /* Tons de lona, naturalidade */
BEGE CLARO:       #D4C5A9  /* Transições, suavidade */
CINZA ESCURO:     #2A2A2A  /* Fundos alternativos */
CINZA MÉDIO:      #888888  /* Textos sutis */
```

### Cores de Apoio (correção de cor):
```css
SOMBRA QUENTE:    #2D1B00  /* Sombras com tom dourado */
HIGHLIGHT FRIO:   #E8F0FF  /* Realces com tom azulado */
```

---

## 📸 REFERÊNCIAS VISUAIS

### Estilo de Fotografia:
1. **Produtos Apple** — Clean, minimalista, fundo escuro
2. **Campanhas Hermès** — Artisanal, mãos, processo
3. **Estilo editorial Vogue** — Lifestyle, pessoas reais, elegância natural
4. **Fotografia de rua japonesa** — Composição, luz natural, storytelling

### Referências de Cor:
1. **Dourado + Preto** — Cartier, Rolex, Chanel
2. **Tons terrosos** — Patagonia (sustentabilidade)
3. **Alto contraste** — Campanhas Nike premium

---

## 🔧 PROCESSAMENTO FINAL 8K

Após gravar todas as cenas, processe com:

```bash
# Opção 1: Edição Inteligente (recomendado)
python edicao_inteligente.py "story_gravado.mp4"

# Opção 2: Processamento direto
python processar_video.py "story_gravado.mp4"

# Opção 3: Menu interativo com opções
python baixar_e_processar.py
# → Opção [4] Processar em modo STORY 8K (9:16)
```

### Configuração Ideal para Story Premium:
```python
CONFIG = {
    "modo_saida": "story",          # 9:16
    "upscaling_8k": True,           # Lanczos
    "codec": "libx265",             # HEVC
    "crf_qualidade": 15,            # Quase lossless
    "fps_saida": 60,                # 60fps
    "pixel_format": "yuv420p10le",  # 10-bit
    "saturacao": 1.4,               # Levemente menos que padrão (mais elegante)
    "contraste": 1.3,               # Alto contraste cinematográfico
    "nitidez": True,                # Unsharp mask
}
```

---

## 📱 ESPECIFICAÇÕES POR PLATAFORMA

### Instagram Stories/Reels:
```
Resolução:  1080 x 1920 (mínimo) / 2160 x 3840 (recomendado)
FPS:        30 ou 60
Formato:    MP4 (H.264 ou H.265)
Tamanho máx: 4GB (Reels) / 250MB (Stories)
Duração:    15s (Stories) / 90s (Reels)
```

### TikTok:
```
Resolução:  1080 x 1920 (mínimo) / 2160 x 3840 (recomendado)
FPS:        30 ou 60
Formato:    MP4 ou MOV
Tamanho máx: 287MB
Duração:    15s, 60s, 3min
```

### YouTube Shorts:
```
Resolução:  1080 x 1920 (mínimo) / 3840 x 2160 (recomendado)
FPS:        30 ou 60
Formato:    MP4 (H.264)
Tamanho máx: 256GB
Duração:    até 60s
```

### Google Drive (link compartilhado):
```
Resolução:  4320 x 7680 (8K vertical)
FPS:        60
Codec:      HEVC 10-bit
CRF:        15
Tamanho:    ~200-500MB estimado
```

---

## ✅ CHECKLIST FINAL DE PUBLICAÇÃO

- [ ] Todas as 7 cenas gravadas
- [ ] Depoimento gravado (se versão completa)
- [ ] Unboxing gravado (se versão completa)
- [ ] Áudio mixado (piano + ambiente + voz)
- [ ] Textos adicionados com animação
- [ ] Processado em 8K com scripts Python
- [ ] Exportado em formato correto para cada plataforma
- [ ] Thumbnail/frame de capa definido
- [ ] Legenda do post escrita
- [ ] Hashtags definidas
- [ ] Link de compra verificado
- [ ] Google Drive atualizado com vídeo final
- [ ] Landing page atualizada com embed

---

## 💡 DICAS FINAIS

### O segredo de um Story premium:
1. **Menos é mais** — Remova tudo que não agrega
2. **Silêncio é poderoso** — Pausas criam tensão
3. **Textura >_face** — Mostrar detalhes do material é mais poderoso que mostrar rosto
4. **Velocidade** — Lento = premium. Rápido = desespero
5. **Consistência** — Use a mesma paleta em TODAS as cenas
6. **Qualidade 8K** — Resolução alta transmite profissionalismo

### Erros comuns (e como evitar):
- ❌ Muitos textos na tela → ✅ Máximo 8 palavras
- ❌ Transições baratas (wipe, spin) → ✅ Fade ou dissolve
- ❌ Música alta demais → ✅ Música sutil, quase subliminar
- ❌ Cores vibrantes → ✅ Tons sóbrios e elegantes
- ❌ Pressa no produto → ✅ Deixe o público QUERER antes de mostrar

---

> **Este guia é seu mapa de produção. Siga cada cena, cada especificação, e o resultado será um Story à altura da marca NANDALIN.** 🎬✨
