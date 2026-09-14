# -*- coding: utf-8 -*-
"""
🤖 CÉREBRO NANDALIN — Think → Create → Evaluate → Improve
============================================================
O programa que trabalha sozinho:

1. PENSAR   → analisa tendências e o algoritmo, escolhe tema/hook/estratégia
2. CRIAR    → monta o Reel/Story automaticamente
3. AVALIAR  → mede se o vídeo criado atende às regras do algoritmo
4. APRIMORAR→ gera variantes com ajustes e mantém a melhor
"""

import os
import random
from pathlib import Path

from . import algoritmo, tendencias
from . import analise as analise_mod
from . import montagem
from .cores import Cores, mensagem, info, ok, aviso, erro, titulo, linha

def pensar(objetivo="alcance", nicho="geral", geo="BR", usar_internet=True, tema_manual=None):
    """
    FASE 1 — O programa decide O QUE criar.
    Retorna o "conceito criativo" + relatório de algoritmo.
    """
    info("\n🧠 FASE 1: PENSANDO... (tendências + algoritmo)")

    # 1. O que está em alta
    tendencias_lista = tendencias.obter_tendencias(geo=geo, usar_internet=usar_internet)
    print(tendencias.relatorio_tendencias(tendencias_lista))

    # 2. Escolher o tema
    tema = tema_manual
    tendencia_escolhida = None
    if not tema:
        # prioriza tendências do nicho
        for t in tendencias_lista:
            if t["categoria"] == nicho:
                tendencia_escolhida = t
                break
        if not tendencia_escolhida and tendencias_lista:
            tendencia_escolhida = tendencias_lista[0]
        if tendencia_escolhida:
            tema = tendencia_escolhida["tema"]
    else:
        tendencia_escolhida = {"tema": tema, "categoria": tendencias.inferir_categoria(tema),
                               "virilidade": 80, "momento": "manual"}

    cat = (tendencia_escolhida or {}).get("categoria", nicho)
    info(f"\n💡 Tema escolhido: {Cores.NEGRITO}{tema}{Cores.RESET}")
    info(f"   Categoria: {cat} • Virilidade: {(tendencia_escolhida or {}).get('virilidade', 'n/d')}")

    # 3. Hooks (ganchos) gerados
    hooks = tendencias.gerar_hooks(tema)
    angulos = tendencias.gerar_angulo(tendencia_escolhida or {"tema": tema})
    info(f"\n   🪝 Hooks gerados:")
    for i, h in enumerate(hooks, 1):
        print(f"      {i}. {h}")

    # 4. Plano do algoritmo
    plano = algoritmo.gerar_plano(objetivo=objetivo, nicho=cat, tema=tema)

    conceito = {
        "tema": tema,
        "categoria": cat,
        "trend": tendencia_escolhida,
        "hooks": hooks,
        "angulos": angulos,
        "plano": plano,
        "legendas": _gerar_caption_dinamico(tema, angulos),
    }
    return conceito

def _gerar_caption_dinamico(tema, angulos):
    """Gera legendas dinâmicas por cena a partir do tema/ângulos."""
    caps = [f"✨ {tema}"]
    for a in angulos[:3]:
        caps.append(a if len(a) < 46 else a[:44] + "...")
    while len(caps) < 3:
        caps.append("assista até o fim 👀")
    return caps

def criar(conceito, path_video, selecao, variante="0", resolucao="hd",
          efeito_zoom="auto", musica_fundo=None, nome_base=None):
    """
    FASE 2 — O programa CRIA a montagem do vídeo.
    """
    hook = conceito["hooks"][0]
    plano = conceito["plano"]
    duracao_alvo = plano["duracao_alvo"]

    if not selecao:
        from .analise import selecionar_cenas as sel
        # análise precisa existir; quem chama cria
        selecao = sel({}, duracao_alvo)
        return None, None

    # alternar hooks por variante para gerar conteúdo diferente
    if variante and variante != "0":
        idx = int(variante) % len(conceito["hooks"])
        hook = conceito["hooks"][idx]

    # variar o efeito de zoom nas variantes
    zooms_fixos = ["auto", "in", "out", "suave"]
    if efeito_zoom == "auto" and variante != "0":
        efeito_zoom = zooms_fixos[int(variante) % len(zooms_fixos)]

    conceito_edit = {**conceito, "hook": hook}

    if not nome_base:
        nome_base = f"{Path(path_video).stem[:24]}_{conceito['categoria']}_v{variante}"

    saida, metricas = montagem.montar_reel(
        path_video, selecao, conceito_edit,
        resolucao=resolucao, efeito_zoom=efeito_zoom,
        musica_fundo=musica_fundo, nome_base=nome_base,
    )
    return saida, metricas

def avaliar(path_video_criado, metricas, plano):
    """
    FASE 3 — O programa AVALIA o vídeo gerado contra o algoritmo.
    """
    pontuacao, detalhe = algoritmo.pontuar_plano(metricas, plano)
    return pontuacao, detalhe

def aprimorar(path_video, conceito, selecao, n_variantes=3, resolucao="hd",
              musica_fundo=None, objetivo="alcance"):
    """
    FASE 4 — Loop completo: criar → avaliar → manter a melhor.
    """
    titulo(f"🤖 FASE 4: APRIMORANDO — {n_variantes} VARIANTES (A/B TEST)")
    plano = conceito["plano"]
    resultados = []

    for v in range(n_variantes):
        info(f"\n▶️  Variante {v + 1}/{n_variantes}...")
        saida, metricas = criar(conceito, path_video, selecao, variante=str(v),
                                resolucao=resolucao, musica_fundo=musica_fundo)
        if saida and metricas:
            pont, detalhe = avaliar(saida, metricas, plano)
            resultados.append({"arquivo": saida, "metricas": metricas, "pontuacao": pont,
                               "detalhe": detalhe, "variante": v + 1})
            ok(f"   Variante {v + 1} gerada: {Path(saida).name}")
            ok(f"   Potencial de engajamento: {pont:.0f}/100")
            info(f"   Hook: {conceito['hooks'][v % len(conceito['hooks'])]}")
        else:
            erro(f"   Variante {v + 1} falhou.")

    if not resultados:
        return None

    resultados.sort(key=lambda x: x["pontuacao"], reverse=True)
    return resultados

def relatorio_final(resultados, conceito, objetivo="alcance"):
    """Relatório final com ranking das variantes e estratégia de postagem."""
    plano = conceito["plano"]
    melhor = resultados[0]
    C = Cores

    linhas = []
    linhas.append(f"\n{C.NEGRITO}{C.BG_VERDE}{C.BRANCO}{'═' * 58}{C.RESET}")
    linhas.append(f"{C.NEGRITO}{C.BG_VERDE}{C.BRANCO}  🏆 RESULTADO FINAL — O MELHOR VÍDEO ESCOLHIDO{C.RESET}")
    linhas.append(f"{C.NEGRITO}{C.BG_VERDE}{C.BRANCO}{'═' * 58}{C.RESET}")

    linhas.append(f"\n🥇 VENCEDOR: {Path(melhor['arquivo']).name}")
    linhas.append(f"   📊 Potencial de engajamento: {melhor['pontuacao']:.0f}/100")
    for d in melhor["detalhe"]:
        linhas.append(f"   {d}")

    linhas.append(f"\n📋 RANKING DAS VARIANTES:")
    for i, r in enumerate(resultados, 1):
        medalha = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        linhas.append(f"   {medalha} v{r['variante']} — {Path(r['arquivo']).name} — {r['pontuacao']:.0f}/100")

    linhas.append(f"\n{C.NEGRITO}📝 LEGENDA PRONTA PARA POSTAR:{C.RESET}")
    legenda = tendencias.gerar_legenda(conceito["tema"], conceito["hooks"],
                                       plano["hashtags"])
    linhas.append(legenda)

    linhas.append(f"\n{C.NEGRITO}🕐 MELHORES MOMENTOS PARA PUBLICAR:{C.RESET}")
    for k, h in plano["horarios"].items():
        linhas.append(f"   • {h['hora']:<18} {h['desc']}")

    linhas.append(f"\n{C.NEGRITO}🚀 PRÓXIMOS PASSOS DA ESTRATÉGIA:{C.RESET}")
    linhas.append(f"   1. Publique o vencedor no melhor horário do seu público.")
    linhas.append(f"   2. Coloque 1–2 hashtags também no PRIMEIRO COMENTÁRIO.")
    linhas.append(f"   3. Responda comentários na 1ª hora (destrava 2ª onda).")
    linhas.append(f"   4. Guarde os vídeos das outras variantes para dias seguintes.")

    return "\n".join(linhas)

def assistente_completo(path_video, objetivo="alcance", nicho="geral", geo="BR",
                        n_variantes=3, resolucao="hd", musica_fundo=None,
                        usar_internet=True, tema_manual=None):
    """
    🚀 EXECUÇÃO COMPLETA: analisar → pensar → criar → avaliar → aprimorar.
    """
    titulo("🤖 NANDALIN AI — ASSISTENTE COMPLETO DE CRIAÇÃO")

    from .util import criar_pastas, get_video_info, resumir_info
    criar_pastas()

    # 0. Validar vídeo
    if not Path(path_video).exists():
        erro(f"Vídeo não encontrado: {path_video}")
        return None
    info(f"📹 Vídeo de entrada: {path_video}")
    info(f"   {resumir_info(get_video_info(path_video))}")

    # 1. Pensar
    conceito = pensar(objetivo=objetivo, nicho=nicho, geo=geo,
                      usar_internet=usar_internet, tema_manual=tema_manual)
    plano = conceito["plano"]

    # Relatório do algoritmo
    print(algoritmo.relatorio_estrategia(plano, tema=conceito["tema"]))

    # 2. Analisar vídeo (o programa "enxerga")
    titulo("🔍 FASE 2: O PROGRAMA ESTÁ ASSISTINDO O SEU VÍDEO")
    analise_dados = analise_mod.analisar_video(path_video)
    print(analise_mod.resumo_analise(analise_dados))

    # 3. Selecionar cenas conforme a estratégia
    selecao = analise_mod.selecionar_cenas(
        analise_dados, duracao_alvo=plano["duracao_alvo"],
        max_shots=max(4, int(plano["duracao_alvo"] / 2)),
    )
    # liberar memória da análise antes de renderizar (importante em 4K/8K)
    del analise_dados
    import gc
    gc.collect()
    info(f"\n✂️ {len(selecao)} cenas escolhidas pelo cérebro:")
    for i, s in enumerate(selecao, 1):
        rosto = "👤" if s.get("tem_rosto") else "  "
        print(f"   {i}. {rosto} {s['inicio']:.1f}s → {s['fim']:.1f}s  "
              f"score {s['score']:.2f}  energia {s.get('energia', 0):.2f}")

    # 4. Criar variantes e aprimorar
    resultados = aprimorar(path_video, conceito, selecao, n_variantes=n_variantes,
                           resolucao=resolucao, musica_fundo=musica_fundo,
                           objetivo=objetivo)
    if not resultados:
        erro("Nenhuma variante foi criada com sucesso.")
        return None

    # 5. Relatório final (ranking + legenda + estratégia)
    print(relatorio_final(resultados, conceito, objetivo))
    montagem.limpar_temp()

    return resultados[0]