#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 NANDALIN AI — Cérebro profissional de criação de Reels & Stories.

Análise o que está em alta, entende o algoritmo do Instagram e cria
vídeos automaticamente: pensa, cria, avalia e aprimora.

Uso:
    python nandalin_ia.py                      # menu interativo
    python nandalin_ia.py --video video.mp4    # assistente completo
"""

import sys
from nandalin_ai.cli import main

if __name__ == "__main__":
    sys.exit(main())