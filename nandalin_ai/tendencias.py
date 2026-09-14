# -*- coding: utf-8 -*-
"""
📈 TENDÊNCIAS — Análise do que está em alta
=============================================
Fontes:
1. Google Trends (RSS de tendências diárias) — dados reais de busca no Brasil.
2. Banco curado de tendências por nicho (funciona 100% offline).
3. Geração de hooks/ângulos criativos a partir do tema.

O programa usa o Google Trends quando há internet; caso contrário,
usa o banco local sem interromper o fluxo.
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus

from .cores import Cores, info, aviso

# ========================================
# BANCO CURADO DE TENDÊNCIAS POR NICHO
# ========================================
BANCO_TENDENCIAS = {
    "geral": [
        {"tema": "Rotina matinal produtiva", "categoria": "geral", "virilidade": 78,
         "momento": "perene", "angulo": ["mostre sua rotina real", "compare antes/depois", "3 erros que você comete"]},
        {"tema": "Resposta a uma polêmica ou debate do momento", "categoria": "geral", "virilidade": 88,
         "momento": "timing", "angulo": ["reaja com argumentos", "dê sua opinião honesta", "desminta um mito"]},
        {"tema": "Fato curioso que poucos sabem", "categoria": "educacao", "virilidade": 82,
         "momento": "perene", "angulo": ["mito vs verdade", "teste você mesmo", "'pouca gente sabe que…'"]},
    ],
    "fitness": [
        {"tema": "Treino de 10 minutos em casa", "categoria": "fitness", "virilidade": 85,
         "momento": "perene", "angulo": ["demo em tempo real", "desafio de 30 dias", "erros que matam o treino"]},
        {"tema": "Transformação corporal com método", "categoria": "fitness", "virilidade": 92,
         "momento": "perene", "angulo": ["antes/depois", "o método completo", "o que eu teria feito antes"]},
        {"tema": "Refeição fitness rápida e barata", "categoria": "fitness", "virilidade": 80,
         "momento": "perene", "angulo": ["receita em 60s", "quanto custa cada receita", "montagem do prato"]},
    ],
    "receitas": [
        {"tema": "Receita de 3 ingredientes", "categoria": "receitas", "virilidade": 87,
         "momento": "perene", "angulo": ["passo a passo completo", "teste de verdade", "erro comum no preparo"]},
        {"tema": "Mistura inusitada que funciona", "categoria": "receitas", "virilidade": 90,
         "momento": "timing", "angulo": ["prove e reaja", "desafie a cozinhar junto", "faça em casa e me conte"]},
        {"tema": "Marmita fit da semana", "categoria": "receitas", "virilidade": 79,
         "momento": "perene", "angulo": ["monte tudo rápido", "lista de compras barata", "conservação correta"]},
    ],
    "financeiro": [
        {"tema": "Erros financeiros que custam caro", "categoria": "financeiro", "virilidade": 86,
         "momento": "perene", "angulo": ["os 3 maiores erros", "o que eu faria diferente", "armadilhas silenciosas"]},
        {"tema": "Como começar a investir do zero", "categoria": "financeiro", "virilidade": 84,
         "momento": "perene", "angulo": ["passo a passo real", "quanto precisa para começar", "exemplos com valores"]},
        {"tema": "Renda extra com o que você já tem", "categoria": "financeiro", "virilidade": 83,
         "momento": "perene", "angulo": ["3 jeitos reais", "resultados em 30 dias", "ferramentas gratuitas"]},
    ],
    "viagem": [
        {"tema": "Destino barato e incrível no Brasil", "categoria": "viagem", "virilidade": 81,
         "momento": "perene", "angulo": ["quanto custou a viagem", "roteiro de 3 dias", "erros que cometi"]},
        {"tema": "Checklist de viagem perfeita", "categoria": "viagem", "virilidade": 78,
         "momento": "perene", "angulo": ["montagem da mala", "itens que salvam", "o que nunca levar"]},
        {"tema": "Um lugar secreto aos olhos dos turistas", "categoria": "viagem", "virilidade": 87,
         "momento": "perene", "angulo": ["mostre o lugar", "como chegar", "melhor época para ir"]},
    ],
    "tech": [
        {"tema": "Dica de IA que muda a rotina", "categoria": "tech", "virilidade": 89,
         "momento": "perene", "angulo": ["demonstração real", "comparação antes/depois", "prompts que funcionam"]},
        {"tema": "Atalhos escondidos do celular", "categoria": "tech", "virilidade": 76,
         "momento": "perene", "angulo": ["5 atalhos que ninguém usa", "teste agora mesmo", "essas configs mudam tudo"]},
        {"tema": "Vale a pena comprar agora ou esperar?", "categoria": "tech", "virilidade": 74,
         "momento": "timing", "angulo": ["análise honesta", "o preço certo", "alternativa mais barata"]},
    ],
    "moda": [
        {"tema": "Look barato que parece caro", "categoria": "moda", "virilidade": 82,
         "momento": "perene", "angulo": ["montagem do look", "onde comprar barato", "comparação de preços"]},
        {"tema": "O que está em alta nesta estação", "categoria": "moda", "virilidade": 80,
         "momento": "sazonal", "angulo": ["tendências principais", "como usar na rotina", "o que evitar"]},
        {"tema": "Transformação de look com peças básicas", "categoria": "moda", "virilidade": 77,
         "momento": "perene", "angulo": ["antes/depois", "5 combinações", "erros de estilo"]},
    ],
    "humor": [
        {"tema": "Situações que todo mundo já viveu", "categoria": "humor", "virilidade": 85,
         "momento": "perene", "angulo": ["dramatização", "POV", "reação exagerada"]},
        {"tema": "Reagindo a comentário polêmico", "categoria": "humor", "virilidade": 83,
         "momento": "timing", "angulo": ["resposta inteligente", "ironia controlada", "desmontando argumento"]},
    ],
    "educacao": [
        {"tema": "Explique algo complexo em 30 segundos", "categoria": "educacao", "virilidade": 84,
         "momento": "perene", "angulo": ["analogia do dia a dia", "exemplo prático", "erro de entendimento comum"]},
        {"tema": "Dica de estudo que funciona", "categoria": "educacao", "virilidade": 79,
         "momento": "perene", "angulo": ["o método completo", "resultados reais", "o erro de quem reprova"]},
    ],
    "marketing": [
        {"tema": "Como vender mais no Instagram", "categoria": "marketing", "virilidade": 82,
         "momento": "perene", "angulo": ["estratégia real", "exemplo de perfil", "erros que matam vendas"]},
        {"tema": "Crescimento no Instagram com conteúdo", "categoria": "marketing", "virilidade": 81,
         "momento": "perene", "angulo": ["o que funcionou", "números reais", "checklist de 7 dias"]},
    ],
}

# ========================================
# CATEGORIAS
# ========================================
CATEGORIAS = [
    "geral", "fitness", "receitas", "financeiro", "viagem", "tech",
    "moda", "humor", "educacao", "marketing", "beleza", "familia", "games", "animais",
]

sinonimos_categoria = {
    "fitness": ["treino", "academia", "gym", "musculação", "saúde", "exercício", "corpo"],
    "receitas": ["receita", "food", "comida", "culinária", "cozinha", "sobremesa", "prato"],
    "financeiro": ["dinheiro", "investimento", "financeira", "renda", "economia", "fatura", "pix"],
    "viagem": ["viagem", "turismo", "destino", "praia", "hotel", "roteiro", "viajar"],
    "tech": ["tecnologia", "celular", "app", "ia", "computador", "digital", "software", "internet"],
    "moda": ["moda", "roupa", "estilo", "look", "tendência", "cabelo", "make"],
    "humor": ["engraçado", "risada", "piada", "humor", "comédia"],
    "educacao": ["estudo", "escola", "curso", "aprender", "dica", "língua", "concurso"],
    "marketing": ["marketing", "vendas", "negócio", "empreender", "loja", "ecommerce", "instagram"],
    "beleza": ["beleza", "skincare", "maquiagem", "perfume", "estética", "pele"],
    "familia": ["mãe", "filho", "família", "bebê", "casa", "rotina", "esposa", "marido"],
    "games": ["jogo", "games", "gamer", "console", "playstation", "xbox", "jogar"],
    "animais": ["cachorro", "gato", "animal", "pets", "dog", "cat"],
}

def inferir_categoria(tema):
    t = str(tema).lower()
    melhor, melhor_pont = "geral", 0
    for cat, palavras in sinonimos_categoria.items():
        pont = sum(1 for p in palavras if p in t)
        if pont > melhor_pont:
            melhor, melhor_pont = cat, pont
    return melhor

# ========================================
# GOOGLE TRENDS (RSS público)
# ========================================
URL_TRENDS = "https://trends.google.com/trending/rss?geo={geo}"

def _fetch_trends(geo="BR", max_itens=12, timeout=12):
    """Busca tendências reais no Google Trends. Retorna [] se offline."""
    import requests
    url = URL_TRENDS.format(geo=geo)
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items = []
    for item in root.iter("item"):
        titulo = item.findtext("title", "").strip()
        tentativas = item.findtext("ht:approx_traffic", "")
        if titulo:
            items.append({"titulo": titulo, "trafego": tentativas, "fonte": "google-trends"})
        if len(items) >= max_itens:
            break
    return items

def obter_tendencias(geo="BR", max_itens=12, usar_internet=True):
    """
    Retorna lista de tendências. Prioriza internet (Google Trends).
    """
    resultado = []
    if usar_internet:
        try:
            info(f"📡 Buscando tendências reais em {geo} no Google Trends...")
            dados = _fetch_trends(geo=geo, max_itens=max_itens)
            for d in dados:
                cat = inferir_categoria(d["titulo"])
                resultado.append({
                    "tema": d["titulo"],
                    "categoria": cat,
                    "virilidade": 90 if d["trafego"] else 75,
                    "momento": "agora",
                    "fonte": "google-trends",
                })
            if resultado:
                return resultado
            aviso("Google Trends não retornou dados; usando banco local.")
        except Exception as e:
            aviso(f"Sem acesso ao Google Trends ({e}). Usando banco local de tendências.")
    return _tendencias_do_banco(max_itens)

def _tendencias_do_banco(max_itens=12):
    resultado = []
    for cat, lista in BANCO_TENDENCIAS.items():
        for t in lista:
            resultado.append({**t, "fonte": "banco-local"})
    resultado.sort(key=lambda x: x["virilidade"], reverse=True)
    return resultado[:max_itens]

# ========================================
# TEMPLATES DE HOOKS (GANCHOS)
# ========================================
TEMPLATES_HOOK = [
    "PARA DE FAZER ISSO AGORA! {tema}!",
    "Ninguém te contou isso sobre {tema}.",
    "Os 3 maiores erros sobre {tema}.",
    "{tema} — o que eu queria saber antes.",
    "Isso vale OURO: {tema} explicado na prática.",
    "Se você faz {tema} assim, pare AGORA.",
    "{tema} | Testei para você descobrir a verdade.",
    "Você está falando de {tema} do jeito errado.",
    "O segredo por trás de {tema} que ninguém mostra.",
    "{tema}: comece hoje e mude seu resultado em 7 dias.",
]

def gerar_hooks(tema, max_hooks=6):
    """Gera hooks variados a partir do tema."""
    hooks = [t.format(tema=tema) if "{tema}" in t else f"{t} {tema}." for t in TEMPLATES_HOOK[:max_hooks]]
    return hooks

# ========================================
# ÂNGULOS CRIATIVOS
# ========================================
ANGULOS_GERAIS = [
    "Antes/depois com resultados reais",
    "Passo a passo em tempo real",
    "Mito ou verdade (teste na prática)",
    "Os 3 erros mais comuns",
    "O que eu faria diferente",
    "Comparação de custo X benefício",
    "Demonstração ao vivo",
    "Desafio: faça junto e me conte",
]

def gerar_angulo(tendencia):
    """Escolhe o ângulo criativo para a tendência."""
    if tendencia.get("angulo"):
        return tendencia["angulo"][:3]
    return ANGULOS_GERAIS[:3]

# ========================================
# LEGENDA PRONTA
# ========================================
def gerar_legenda(tema, hooks, categorias_tags):
    """Gera uma legenda pronta para postar."""
    hook = hooks[0] if hooks else tema
    tags = " ".join(categorias_tags)
    legenda = (
        f"{hook}\n\n"
        f"💡 Salva esse Reel para não perder!\n"
        f"🤝 Compartilha com aquela pessoa que precisa ver isso.\n"
        f"👇 Comenta o que você acha — vou responder todos!\n\n"
        f"{tags}"
    )
    return legenda

# ========================================
# RELATÓRIO DE TENDÊNCIAS
# ========================================
def relatorio_tendencias(tendencias):
    C = Cores
    linhas = []
    linhas.append(f"\n{C.NEGRITO}{C.MAGENTA}{'═' * 58}{C.RESET}")
    linhas.append(f"{C.NEGRITO}📈 O QUE ESTÁ EM ALTA AGORA{C.RESET}")
    linhas.append(f"{C.MAGENTA}{'═' * 58}{C.RESET}")
    for i, t in enumerate(tendencias[:10], 1):
        fonte = "🌐 Google Trends" if t.get("fonte") == "google-trends" else "📚 Banco local"
        linha = f"  {i}. {t['tema']}"
        linhas.append(linha)
        linhas.append(f"      🏷️  {t['categoria'].capitalize()}  •  🔥 virilidade "
                      f"{t['virilidade']}/100  •  {fonte}")
    return "\n".join(linhas)