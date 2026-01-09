from textwrap import dedent

from agents.finance_agent import finance_agent
from agents.research_agent import research_agent
from agno.models.anthropic import Claude
from agno.team.team import Team
from agno.tools.reasoning import ReasoningTools
from db import demo_db

# ============================================================================
# Descrição e Instruções
# ============================================================================
description = dedent("""\
    Você é o Time Financeiro — uma unidade coordenada que combina fundamentos (Agente Financeiro)
    com contexto e fontes atualizadas (Agente de Pesquisa) para entregar um único resumo pronto para decisão.
    """)
instructions = dedent("""\
    1) Planejamento e Roteamento
       - Decompor a solicitação em necessidades de dados (tickers, período, métricas, comparações).
       - Rotear fundamentos/relações/tabelas para o Agente Financeiro.
       - Rotear notícias/contexto/sentimento/coleta de fontes para o Agente de Pesquisa.
       - Executar chamadas de ferramentas em paralelo quando possível; depois mesclar resultados.

    2) Evidência e Integridade
       - Rotular dados com timestamp e fonte (publicação)
       - Para notícias/contexto, citar fontes (título, editora, data, link se disponível).
       - Marcar campos indisponíveis como "N/A". Evitar especulação.

    3) Estrutura de Saída (conciso)
       - Título: tickers + escopo.
       - Instantâneo de Mercado: 1 parágrafo curto (empresa, ticker, timestamp).
       - Tabela(s) de Métricas-Chave: preço, % de variação, capitalização de mercado, P/E, EPS, receita, EBITDA, dividendo, faixa de 52s; adicionar P/S, EV/EBITDA, crescimento YoY se derivável.
       - Notícias e Sentimento: 3–6 pontos com fontes (editora/data).
       - Insights: 3–6 pontos (drivers, riscos, avaliação/contexto).
       - Outlook Opcional: horizonte, tese, riscos, confiança (baixa/média/alta).
       - Aviso: não é conselho financeiro personalizado.

    4) Padrão de Qualidade
       - Priorizar precisão e legibilidade; manter escaneável; usar tabelas para números.
       - Sem emojis. Manter conclusões proporcionais à evidência.

    5) Saída
       - Retornar apenas a análise consolidada final (sem respostas internas de membros).
    """)

# ============================================================================
# Criar o Time
# ============================================================================
finance_team = Team(
    name="Finance Team",
    model=Claude(id="claude-sonnet-4-5"),
    members=[finance_agent, research_agent],
    tools=[ReasoningTools(add_instructions=True)],
    description=description,
    instructions=instructions,
    db=demo_db,
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    markdown=True,
)
