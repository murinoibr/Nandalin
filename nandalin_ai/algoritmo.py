# -*- coding: utf-8 -*-
"""
🧠 ALGORITMO DO INSTAGRAM — Módulo de estratégia
=================================================
Encoda o conhecimento atual sobre como o algoritmo do Instagram ranqueia
Reels e Stories, e gera planos de otimização por vídeo.

Fonte de conhecimento (curado, atualizado em 2025/2026):
- O algoritmo prioriza SINAIS DE QUALIDADE: tempo de exibição, re-exibições
  (rewatch), conclusão, compartilhamentos, salvamentos e comentários.
- Reels curtos (< 15s) têm mais chance de entrar no "Explorar" (descoberta).
- O HOOK (primeiros 1–2 segundos) decide se o usuário continua assistindo.
- Áudios em alta e efeitos tendência recebem boost temporário.
- Consistência + horário em que o público está ativo > quantidade.
- Estrutura "Se–Então" (if-then) melhora a permanência.
"""

from .cores import Cores

ALGORITMO_VERSAO = "2026"

# ========================================
# SINAIS DE RANKING (fontes públicas de engenheiros do IG)
# ========================================
SINAIS_RANKING = [
    {"sinal": "Tempo de exibição (watch time)", "peso": 90,
     "desc": "Quanto mais tempo as pessoas assistem, mais o IG mostra seu Reel."},
    {"sinal": "Tempo de re-exibição (rewatch)", "peso": 85,
     "desc": "Trechos assistidos de novo = sinal forte de conteúdo envolvente."},
    {"sinal": "Taxa de conclusão", "peso": 75,
     "desc": "Percentual de quem assiste até o fim. Por isso vídeos curtos vencem."},
    {"sinal": "Compartilhamentos (mensagens diretas)", "peso": 80,
     "desc": "Compartilhar = declaração pública de valor. Sinal mais forte de todos."},
    {"sinal": "Salvamentos", "peso": 70,
     "desc": "Mostra intenção de voltar. Conteúdo útil/educativo salva mais."},
    {"sinal": "Comentários", "peso": 60,
     "desc": "A discussão prolonga o tempo de permanência na plataforma."},
    {"sinal": "Curtidas", "peso": 40,
     "desc": "Sinal clássico mas de peso menor que compartilhamentos e salvamentos."},
    {"sinal": "Respostas a Stories / interações de proximidade", "peso": 55,
     "desc": "Relacionamento: quem interage sempre vê seu conteúdo primeiro."},
    {"sinal": "Curtir, seguir e favoritar depois", "peso": 45,
     "desc": "Fechar, voltar e publicar depois são comportamentos assistidos pelo IG."},
    {"sinal": "'Não interessado' / pular no primeiro segundo", "peso": -90,
     "desc": "O IG te pune quando o público rejeita rápido. Hook é obrigatório."},
]

# ========================================
# MELHORES PRÁTICAS PARA REELS
# ========================================
MELHORES_PRATICAS = [
    {"regra": "Hook nos primeiros 1–2 segundos", "peso": 95,
     "desc": "A primeira frase/ação decide 80% da permanência. Comece com o impacto."},
    {"regra": "Duração de 7 a 15 segundos", "peso": 85,
     "desc": "Curto = maior conclusão. 12s é o ponto ótimo para descoberta."},
    {"regra": "Vídeo 100% vertical 9:16", "peso": 70,
     "desc": "Formato nativo do Reels ocupa a tela toda e retém mais."},
    {"regra": "Legenda e texto legível dentro do vídeo", "peso": 65,
     "desc": "80% assiste sem som. Texto grande e contrastado mantém a atenção."},
    {"regra": "Áudio em alta ou original", "peso": 60,
     "desc": "Áudios tendência recebem boost; áudios originais criam marca."},
    {"regra": "Estrutura de 'promessa-cumprida' (se-então)", "peso": 75,
     "desc": "Prometa um resultado no hook e entregue ao final — gera rewatch."},
    {"regra": "3 a 5 hashtags relevantes", "peso": 45,
     "desc": "Qualidade > quantidade. Muitas hashtags não aumentam alcance."},
    {"regra": "Sem marca d'água de outras plataformas", "peso": 55,
     "desc": "Vídeos reutilizados de TikTok são despriorizados pelo IG."},
    {"regra": "Postar quando o público está ativo", "peso": 50,
     "desc": "Interação inicial rápida destrava a distribuição em ondas."},
    {"regra": "Primeiro comentário estratégico", "peso": 35,
     "desc": "Um comentário instigante no 1º minuto aumenta a interação."},
    {"regra": "Transições e cortes rápidos", "peso": 65,
     "desc": "Ritmo visual acelerado mantém o cérebro engajado."},
    {"regra": "Call-to-action leve (compartilhe/salve)", "peso": 55,
     "desc": "Compartilhe/salve/comente gera os sinais fortes do ranking."},
]

# ========================================
# TEMPOS IDEIAS POR OBJETIVO
# ========================================
OBJETIVOS = {
    "alcance": {
        "nome": "Alcance/Explorar",
        "duracao_alvo": 8,
        "faixa": (6, 12),
        "desc": "Vídeo curto, gancho forte, final com re-exibição em mente.",
    },
    "viral": {
        "nome": "Viralização",
        "duracao_alvo": 12,
        "faixa": (8, 15),
        "desc": "Tema em alta + tensão crescente + compartilhamento induzido.",
    },
    "engajamento": {
        "nome": "Engajamento",
        "duracao_alvo": 15,
        "faixa": (10, 20),
        "desc": "Perguntas, enquetes e opinião do público ao final.",
    },
    "autoridade": {
        "nome": "Autoridade",
        "duracao_alvo": 20,
        "faixa": (12, 30),
        "desc": "Conteúdo educativo/processo, valor percebido alto, salvamentos.",
    },
    "vendas": {
        "nome": "Vendas",
        "duracao_alvo": 30,
        "faixa": (15, 45),
        "desc": "Prova social + oferta clara + urgência ao final.",
    },
}

# ========================================
# NICHO → HASHTAGS
# ========================================
HASHTAGS_NICHO = {
    "geral": ["#reels", "#viral", "#explore", "#brasil"],
    "fitness": ["#fitness", "#treino", "#healthy", "#gymlife", "#motivation"],
    "receitas": ["#receitas", "#food", "#comida", "#cozinha", "#receitasfaceis"],
    "financeiro": ["#financas", "#dinheiro", "#investimentos", "#rendaextra", "#mindset"],
    "viagem": ["#viagem", "#travel", "#destinos", "#turismo", "#brasilviajens"],
    "moda": ["#moda", "#look", "#estilo", "#outfit", "#trend"],
    "tech": ["#tecnologia", "#inteligenciaartificial", "#ia", "#inovacao", "#ficadica"],
    "humor": ["#comedia", "#humor", "#memes", "#risada", "#divertido"],
    "educacao": ["#aprenda", "#educacao", "#dicas", "#estudo", "#conhecimento"],
    "marketing": ["#marketingdigital", "#vendas", "#empreendedorismo", "#negocios", "#estrategia"],
    "beleza": ["#beleza", "#make", "#skincare", "#cabelo", "#penteado"],
    "familia": ["#familia", "#maternidade", "#rotina", "#casa", "#filhos"],
    "games": ["#games", "#gamer", "#playstation", "#fps", "#gameplay"],
    "animais": ["#animais", "#pets", "#cachorro", "#gato", "#fofura"],
}

def _categoria_para_hashtags(categoria):
    if categoria in HASHTAGS_NICHO:
        return HASHTAGS_NICHO[categoria]
    return HASHTAGS_NICHO["geral"]

def _tokenizar(tema):
    tokens = []
    for p in tema.lower().replace(",", " ").split():
        p = "".join(c for c in p if c.isalnum())
        if len(p) >= 3 and p not in ("com", "para", "quando", "como", "porque", "que"):
            tokens.append(p)
    return tokens[:4]

def montar_hashtags(categoria, tema, total=5):
    """Monta mix de hashtags: 1 ampla + nicho + palavras-chave do tema."""
    tags = list(_categoria_para_hashtags(categoria))
    for t in _tokenizar(tema):
        tags.append(f"#{t}")
    # deduplicar preservando ordem
    vistos = set()
    unicas = []
    for t in tags:
        t = t.lstrip("#")
        if t not in vistos:
            vistos.add(t)
            unicas.append(f"#{t}")
    return unicas[:total]

# ========================================
# HORÁRIOS DE POSTAGEM POR NICHO
# ========================================
HORARIOS = {
    "manha": {"hora": "07h–09h", "desc": "Início do dia: público lendo e engajando."},
    "almoco": {"hora": "12h–13h30", "desc": "Pausa do almoço: scroll intenso."},
    "tarde": {"hora": "16h–17h", "desc": "Fim da tarde: retomada de atenção."},
    "noite": {"hora": "19h–21h30", "desc": "Pico principal de uso dos Reels."},
    "sexta": {"hora": "Sex 15h–19h", "desc": "Sexta: ânimo social, mais compartilhamentos."},
    "domingo": {"hora": "Dom 08h–11h", "desc": "Domingo de manhã: tempo livre, alta retenção."},
}

def gerar_plano(objetivo="alcance", nicho="geral", tema=None):
    """Gera o plano de otimização do vídeo segundo o algoritmo."""
    obj = OBJETIVOS.get(objetivo, OBJETIVOS["alcance"])
    return {
        "objetivo": obj["nome"],
        "duracao_alvo": obj["duracao_alvo"],
        "faixa_duracao": obj["faixa"],
        "descricao": obj["desc"],
        "estrutura": [
            {"etapa": "1. Hook", "tempo_faixa": "0s–2s",
             "acao": "Afirmação impactante ou cena forte; prometa o resultado."},
            {"etapa": "2. Contexto", "tempo_faixa": "2s–40%",
             "acao": "Mostre o porquê/contexto de forma rápida e visual."},
            {"etapa": "3. Desenvolvimento", "tempo_faixa": "40%–80%",
             "acao": "Entregue o valor prometido; ritmo de cortes acelerando."},
            {"etapa": "4. Resolução + CTA", "tempo_faixa": "80%–fim",
             "acao": "Conclua e peça leve: 'salve para depois' / 'compartilhe'."},
        ],
        "checklist_melhores_praticas": MELHORES_PRATICAS,
        "hashtags": montar_hashtags(nicho, tema or ""),
        "horarios": HORARIOS,
    }

# ========================================
# PONTUAÇÃO DE UM VÍDEO CRIADO (POTENCIAL DE ENGAJAMENTO)
# ========================================
def pontuar_plano(metricas, plano=None):
    """
    Calcula (0–100) o potencial de engajamento de um vídeo gerado.
    metricas esperadas: duracao, n_cortes, energia_media (0-1),
    tem_rosto (bool), variacao_cena (0-1), taxa_completude (0-1).
    """
    pontos = 0
    detalhe = []

    alvo = (plano or {}).get("duracao_alvo", 10)
    faixa_min, faixa_max = (plano or {}).get("faixa_duracao", (6, 30))

    # 1. Duração dentro da faixa ideal (até 25 pts)
    dur = metricas.get("duracao", 0)
    if faixa_min <= dur <= faixa_max:
        pts = 25 * (1 - abs(dur - alvo) / max(faixa_max, 1))
    elif dur < faixa_min:
        pts = 15 * (dur / max(faixa_min, 1))
    else:
        pts = 10 * max(0, 1 - (dur - faixa_max) / 30)
    pontos += max(0, min(25, pts))
    detalhe.append(f"⏱️  Duração ({dur:.1f}s vs alvo {alvo}s): {max(0, min(25, pts)):.0f}/25")

    # 2. Ritmo/cortes: 4+ cortes em 12s = bom (até 20 pts)
    cortes = metricas.get("n_cortes", 1)
    ritmo = max(0, min(1, cortes / max(6, alvo / 2)))
    pts = 20 * ritmo
    pontos += pts
    detalhe.append(f"✂️  Ritmo ({cortes} cenas): {pts:.0f}/20")

    # 3. Energia do áudio (até 15 pts)
    energia = metricas.get("energia_media", 0.5)
    pts = 15 * max(0, min(1, energia))
    pontos += pts
    detalhe.append(f"🔊 Energia do áudio ({energia:.2f}): {pts:.0f}/15")

    # 4. Foco (rosto/presença humana) (até 15 pts)
    tem_rosto = metricas.get("tem_rosto", False)
    pts = 15 if tem_rosto else 6
    pontos += pts
    detalhe.append(f"👤 Foco humano: {pts}/15")

    # 5. Variação de cena / dinamismo (até 15 pts)
    var = metricas.get("variacao_cena", 0.5)
    pts = 15 * max(0, min(1, var))
    pontos += pts
    detalhe.append(f"🎞️  Dinamismo visual ({var:.2f}): {pts:.0f}/15")

    # 6. Completude (bônus, até 10 pts)
    comp = metricas.get("taxa_completude", 1.0)
    pts = 10 * max(0, min(1, comp))
    pontos += pts
    detalhe.append(f"🎯 Completude da promessa ({comp:.2f}): {pts:.0f}/10")

    return round(max(0, min(100, pontos)), 1), detalhe

# ========================================
# RELATÓRIO FORMATADO
# ========================================
def relatorio_estrategia(plano, pontuacao=None, detalhe=None, tema=None):
    C = Cores
    linhas = []
    linhas.append(f"\n{C.NEGRITO}{C.CIANO}{'═' * 58}{C.RESET}")
    linhas.append(f"{C.NEGRITO}🧠 RELATÓRIO DO ALGORITMO DO INSTAGRAM{C.RESET}")
    linhas.append(f"{C.CIANO}{'═' * 58}{C.RESET}")
    linhas.append(f"🎯 Objetivo: {C.NEGRITO}{plano['objetivo']}{C.RESET}")
    if tema:
        linhas.append(f"💡 Tema central: {tema}")
    linhas.append(f"⏱️  Duração ideal: {C.NEGRITO}{plano['duracao_alvo']}s{C.RESET} "
                  f"(faixa {plano['faixa_duracao'][0]}–{plano['faixa_duracao'][1]}s)")
    linhas.append(f"📝 Estratégia: {plano['descricao']}")

    linhas.append(f"\n{C.NEGRITO}📐 ESTRUTURA DE RETENÇÃO:{C.RESET}")
    for e in plano["estrutura"]:
        linhas.append(f"   {e['etapa']:.<32} {e['tempo_faixa']}")
        linhas.append(f"        → {e['acao']}")

    if pontuacao is not None:
        cor_pont = C.VERDE if pontuacao >= 70 else (C.AMARELO if pontuacao >= 45 else C.VERMELHO)
        linhas.append(f"\n{C.NEGRITO}📊 POTENCIAL DE ENGAJAMENTO: {cor_pont}"
                      f"{pontuacao:.0f}/100{C.RESET}")
        if detalhe:
            for d in detalhe:
                linhas.append(f"   {d}")

    linhas.append(f"\n{C.NEGRITO}🏷️  HASHTAGS ESTRATÉGICAS ({len(plano['hashtags'])}):{C.RESET}")
    linhas.append(f"   {' '.join(plano['hashtags'])}")
    linhas.append(f"   💬 Use 1–2 dessas no PRIMEIRO COMENTÁRIO do Reel.")

    linhas.append(f"\n{C.NEGRITO}🕐 MELHORES HORÁRIOS PARA POSTAR:{C.RESET}")
    for k, h in plano["horarios"].items():
        linhas.append(f"   • {h['hora']:<18} {h['desc']}")

    linhas.append(f"\n{C.NEGRITO}✅ CHECKLIST DO ALGORITMO:{C.RESET}")
    for p in plano["checklist_melhores_praticas"][:8]:
        linhas.append(f"   ✓ {p['regra']}")

    linhas.append(f"\n⚠️  Observação: o algoritmo muda constantemente. Este relatório usa "
                  f"padrões públicos de engenharia do IG ({ALGORITMO_VERSAO}), "
                  f"mas métricas reais do seu perfil são o melhor guia.")
    return "\n".join(linhas)