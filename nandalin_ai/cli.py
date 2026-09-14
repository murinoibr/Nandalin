# -*- coding: utf-8 -*-
"""
🖥️ INTERFACE DO NANDALIN AI
=============================
Menu interativo + linha de comando.

Uso:
    python nandalin_ia.py                      # menu interativo
    python nandalin_ia.py --video video.mp4    # assistente completo
    python nandalin_ia.py --trends             # tendências
    python nandalin_ia.py --algoritmo          # relatório do algoritmo
    python nandalin_ia.py --analise video.mp4  # análise do vídeo
    python nandalin_ia.py --video video.mp4 --variantes 5 --resolucao 4k
"""

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from . import algoritmo, tendencias, analise, cerebro, montagem
from .cores import Cores, cabecalho, mensagem, info, ok, aviso, erro, titulo, linha
from .util import (criar_pastas, listar_videos_locais, get_video_info,
                   resumir_info, PASTA_IA)

# ========================================
# ESTADO DA CONFIGURAÇÃO
# ========================================
CONFIG = {
    "objetivo": "alcance",
    "nicho": "geral",
    "geo": "BR",
    "resolucao": "hd",
    "variantes": 3,
    "musica_fundo": None,
    "internet": True,
    "efeito_zoom": "auto",
}

def _mostrar_config():
    print(f"\n  {Cores.NEGRITO}⚙️  CONFIGURAÇÃO ATUAL:{Cores.RESET}")
    print(f"  {'─' * 50}")
    plano_obj = algoritmo.OBJETIVOS[CONFIG["objetivo"]]
    print(f"  🎯 Objetivo:      {plano_obj['nome']}")
    print(f"  🏷️  Nicho:         {CONFIG['nicho']}")
    print(f"  🌍 Região:        {CONFIG['geo']}")
    print(f"  📐 Resolução:     {CONFIG['resolucao']}")
    print(f"  🔁 Variantes:     {CONFIG['variantes']}")
    print(f"  🌐 Internet:      {'Ativa' if CONFIG['internet'] else 'Offline'}")
    print(f"  🎵 Música fundo:  {CONFIG['musica_fundo'] or 'nenhuma'}")
    print(f"  {'─' * 50}")

def _configurar():
    from .montagem import RESOLUCOES
    while True:
        _mostrar_config()
        print(f"\n  Opções:")
        print(f"   [1] Objetivo")
        print(f"   [2] Nicho")
        print(f"   [3] Região (geo)")
        print(f"   [4] Resolução")
        print(f"   [5] Nº de variantes")
        print(f"   [6] Música de fundo")
        print(f"   [7] Internet on/off")
        print(f"   [0] Voltar")
        r = input(f"\n  {Cores.AMARELO}Escolha: {Cores.RESET}").strip()

        if r == "1":
            print(f"\n  Objetivos:")
            for i, (k, v) in enumerate(algoritmo.OBJETIVOS.items(), 1):
                print(f"   [{i}] {v['nome']} — {v['desc']}")
            try:
                i = int(input(f"  {Cores.AMARELO}Escolha: {Cores.RESET}").strip())
                CONFIG["objetivo"] = list(algoritmo.OBJETIVOS.keys())[i - 1]
            except (ValueError, IndexError):
                aviso("Opção inválida")
        elif r == "2":
            print(f"\n  Nichos: {', '.join(tendencias.CATEGORIAS)}")
            n = input(f"  {Cores.AMARELO}Nicho: {Cores.RESET}").strip().lower()
            if n in tendencias.CATEGORIAS:
                CONFIG["nicho"] = n
        elif r == "3":
            g = input(f"  {Cores.AMARELO}Código do país (BR, US, PT...): {Cores.RESET}").strip().upper()
            if g:
                CONFIG["geo"] = g
        elif r == "4":
            print(f"  Resoluções: {' | '.join(RESOLUCOES.keys())}")
            res = input(f"  {Cores.AMARELO}Resolução (Enter=hd): {Cores.RESET}").strip().lower()
            if res:
                CONFIG["resolucao"] = res
        elif r == "5":
            try:
                CONFIG["variantes"] = max(1, min(9, int(input(f"  {Cores.AMARELO}Variantes (1-9): {Cores.RESET}").strip())))
            except ValueError:
                aviso("Número inválido")
        elif r == "6":
            m = input(f"  {Cores.AMARELO}Caminho da música (ou Enter para limpar): {Cores.RESET}").strip()
            CONFIG["musica_fundo"] = m if m and Path(m).exists() else (None if not m else CONFIG["musica_fundo"])
            if m and not Path(m).exists():
                aviso("Arquivo de música não encontrado")
        elif r == "7":
            CONFIG["internet"] = not CONFIG["internet"]
        elif r == "0":
            return
        else:
            aviso("Opção inválida")

def _escolher_video():
    videos = listar_videos_locais()
    if not videos:
        aviso("Nenhum vídeo encontrado. Coloque vídeos em videos_originais/ ou na raiz.")
        return None
    print(f"\n  VÍDEOS DISPONÍVEIS:")
    for i, v in enumerate(videos, 1):
        try:
            ri = resumir_info(get_video_info(v))
            mp = ri["megapixels"]
            tam = os.path.getsize(v) / (1024 * 1024)
            print(f"   {i}. {Path(v).name} — {ri['width']}x{ri['height']} "
                  f"({mp:.1f} MP) {ri['duracao']:.0f}s ({tam:.0f} MB)")
        except Exception:
            print(f"   {i}. {Path(v).name}")
    try:
        idx = int(input(f"\n  {Cores.AMARELO}Escolha o vídeo: {Cores.RESET}").strip()) - 1
        if 0 <= idx < len(videos):
            return videos[idx]
    except (ValueError, EOFError):
        pass
    aviso("Opção inválida")
    return None

def _rodar_assistente():
    video = _escolher_video()
    if not video:
        return
    tema = input(f"  {Cores.AMARELO}Tema/alerta manual (Enter = automático das tendências): {Cores.RESET}").strip() or None
    melhor = cerebro.assistente_completo(
        video,
        objetivo=CONFIG["objetivo"],
        nicho=CONFIG["nicho"],
        geo=CONFIG["geo"],
        n_variantes=CONFIG["variantes"],
        resolucao=CONFIG["resolucao"],
        musica_fundo=CONFIG["musica_fundo"],
        usar_internet=CONFIG["internet"],
        tema_manual=tema,
    )
    if melhor:
        ok(f"\n🏆 Melhor vídeo criado: {melhor['arquivo']}")
        ok(f"   Abra a pasta saidas_ia/ para publicar!")

def _rodar_tendencias():
    lista = tendencias.obter_tendencias(geo=CONFIG["geo"], usar_internet=CONFIG["internet"])
    print(tendencias.relatorio_tendencias(lista))

def _rodar_algoritmo():
    plano = algoritmo.gerar_plano(objetivo=CONFIG["objetivo"], nicho=CONFIG["nicho"])
    print(algoritmo.relatorio_estrategia(plano))

def _rodar_analise():
    video = _escolher_video()
    if not video:
        return
    info(f"\n🔍 Analisando {video}...")
    dados = analise.analisar_video(video)
    print(analise.resumo_analise(dados))

def _escolher_reel_gerado():
    """Escolhe um Reel da pasta saidas_ia/."""
    pasta = Path(PASTA_IA)
    if not pasta.exists():
        return None
    reels = sorted(pasta.glob("*.mp4"))
    if not reels:
        return None
    print(f"\n  REELS JÁ CRIADOS PELO NANDALIN AI:")
    for i, r in enumerate(reels, 1):
        tam = os.path.getsize(r) / (1024 * 1024)
        print(f"   {i}. {r.name} ({tam:.1f} MB)")
    try:
        idx = int(input(f"\n  {Cores.AMARELO}Escolha: {Cores.RESET}").strip()) - 1
        if 0 <= idx < len(reels):
            return str(reels[idx])
    except (ValueError, EOFError):
        pass
    return None

def _rodar_finalizar_8k():
    """Upscale do Reel em 8K usando o pipeline premium do projeto."""
    video = _escolher_reel_gerado() or _escolher_video()
    if not video:
        aviso("Nenhum vídeo disponível para finalizar.")
        return
    try:
        import baixar_e_processar as b8k
    except ImportError:
        aviso("Módulo baixar_e_processar.py não encontrado.")
        return

    info(f"\n🚀 Finalizando {Path(video).name} em 8K premium...")
    config = b8k.CONFIG_PROCESSAMENTO.copy()
    config["modo_saida"] = "story"
    config["resolucao_alvo"] = "8k"
    nome = Path(video).stem
    output = Path("videos_stories_8k") / f"{nome}_story_8k.mp4"
    ok(b8k.processar_video(video, str(output), config))
    ok(f"Vídeo 8K final: {output}")

def menu():
    cabecalho()
    criar_pastas()
    while True:
        print(f"\n{Cores.CIANO}{'═' * 60}{Cores.RESET}")
        print(f"{Cores.NEGRITO}  📋 MENU PRINCIPAL — NANDALIN AI{Cores.RESET}")
        print(f"{Cores.CIANO}{'═' * 60}{Cores.RESET}")
        print()
        print(f"  {Cores.VERDE}[1]{Cores.RESET} 🤖 Assistente IA COMPLETO (tudo automático)")
        print(f"  {Cores.VERDE}[2]{Cores.RESET} 📈 O que está em ALTA (tendências)")
        print(f"  {Cores.VERDE}[3]{Cores.RESET} 🎬 Analisar um vídeo (foco e melhores momentos)")
        print(f"  {Cores.VERDE}[4]{Cores.RESET} 🧠 Entender o algoritmo do Instagram")
        print(f"  {Cores.VERDE}[5]{Cores.RESET} ✂️  Criar Reel/Story de um vídeo (com variantes)")
        print(f"  {Cores.VERDE}[6]{Cores.RESET} ⚙️  Configurações")
        print(f"  {Cores.VERDE}[7]{Cores.RESET} 🚀 Finalizar em 8K (pipeline premium)")
        print(f"  {Cores.VERDE}[0]{Cores.RESET} 🚪 Sair")
        print()

        opcao = input(f"  {Cores.AMARELO}Escolha: {Cores.RESET}").strip()
        if opcao == "1":
            _rodar_assistente()
        elif opcao == "2":
            _rodar_tendencias()
        elif opcao == "3":
            _rodar_analise()
        elif opcao == "4":
            _rodar_algoritmo()
        elif opcao == "5":
            _rodar_assistente()
        elif opcao == "6":
            _configurar()
        elif opcao == "7":
            _rodar_finalizar_8k()
        elif opcao == "0":
            mensagem("\n👋 Até logo! Produza conteúdo premium! 🎬\n")
            break
        else:
            aviso("Opção inválida")

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="nandalin_ia",
        description="🤖 NANDALIN AI — Cérebro profissional de criação de Reels & Stories",
    )
    parser.add_argument("--video", "-v", help="Vídeo de entrada para criar Reels")
    parser.add_argument("--trends", action="store_true", help="Mostrar o que está em alta")
    parser.add_argument("--algoritmo", action="store_true", help="Relatório do algoritmo do IG")
    parser.add_argument("--analise", action="store_true", help="Analisar o vídeo em detalhe")
    parser.add_argument("--objetivo", default=CONFIG["objetivo"],
                        choices=list(algoritmo.OBJETIVOS.keys()),
                        help="Objetivo do conteúdo")
    parser.add_argument("--nicho", default=CONFIG["nicho"], help="Nicho do conteúdo")
    parser.add_argument("--geo", default=CONFIG["geo"], help="Código da região (BR, US...)")
    parser.add_argument("--variantes", type=int, default=CONFIG["variantes"],
                        help="Nº de variantes (A/B test)")
    parser.add_argument("--resolucao", default=CONFIG["resolucao"],
                        choices=["hd", "fullhd", "4k", "8k"], help="Resolução do Reel")
    parser.add_argument("--musica", default=None, help="Música de fundo")
    parser.add_argument("--offline", action="store_true", help="Não usar internet")
    parser.add_argument("--tema", default=None, help="Tema manual para o conteúdo")
    parser.add_argument("--versao", action="version", version=f"NANDALIN AI v{__version__}")

    args = parser.parse_args(argv)

    CONFIG["objetivo"] = args.objetivo
    CONFIG["nicho"] = args.nicho
    CONFIG["geo"] = args.geo
    CONFIG["variantes"] = args.variantes
    CONFIG["resolucao"] = args.resolucao
    CONFIG["musica_fundo"] = args.musica
    CONFIG["internet"] = not args.offline

    if args.trends:
        _rodar_tendencias()
    elif args.algoritmo:
        _rodar_algoritmo()
    elif args.analise:
        if not args.video:
            aviso("Use --analise junto com --video")
            return 1
        dados = analise.analisar_video(args.video)
        print(analise.resumo_analise(dados))
    elif args.video:
        melhor = cerebro.assistente_completo(
            args.video,
            objetivo=args.objetivo, nicho=args.nicho, geo=args.geo,
            n_variantes=args.variantes, resolucao=args.resolucao,
            musica_fundo=args.musica, usar_internet=CONFIG["internet"],
            tema_manual=args.tema,
        )
        if melhor:
            ok(f"\n🏆 Melhor vídeo criado: {melhor['arquivo']}")
    else:
        menu()

    return 0

if __name__ == "__main__":
    sys.exit(main())