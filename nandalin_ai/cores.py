# -*- coding: utf-8 -*-
"""Cores e utilitários visuais do NANDALIN AI."""

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

def ok(texto):
    mensagem(f"✅ {texto}", Cores.VERDE)

def aviso(texto):
    mensagem(f"⚠️  {texto}", Cores.AMARELO)

def erro(texto):
    mensagem(f"❌ {texto}", Cores.VERMELHO)

def info(texto):
    mensagem(texto, Cores.CIANO)

def titulo(texto, largura=58):
    print()
    print(f"{Cores.NEGRITO}{Cores.BG_AZUL}{Cores.BRANCO}{'═' * (largura + 8)}")
    print(f"{Cores.NEGRITO}{Cores.BG_AZUL}{Cores.BRANCO}{'  '}{texto}{'  '}")
    print(f"{Cores.NEGRITO}{Cores.BG_AZUL}{Cores.BRANCO}{'═' * (largura + 8)}{Cores.RESET}")
    print()

def linha(caractere="─", n=54, cor=Cores.CIANO):
    print(f"{cor}{caractere * n}{Cores.RESET}")

def cabecalho():
    print()
    print(f"{Cores.NEGRITO}{Cores.BG_AZUL}{Cores.BRANCO}{'═' * 66}")
    print("  🎬 NANDALIN AI — CÉREBRO DE REELS & STORIES")
    print("  🤖 Analisa • Pensa • Cria • Avalia • Aprimora")
    print("  📈 Algoritmo do Instagram + Tendências em alta")
    print(f"{'═' * 66}{Cores.RESET}")
    print()