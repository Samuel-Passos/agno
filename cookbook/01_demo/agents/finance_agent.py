from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from db import demo_db

# ============================================================================
# Descrição e Instruções
# ============================================================================
description = dedent("""\
   Você é um Agente Financeiro — um analista orientado por dados que recupera dados de mercado e fundamentos,
   calcula relações-chave e produz insights concisos e prontos para decisão.
   """)
instructions = dedent("""\
   1) Escopo e Tickers
      - Detectar e confirmar nomes de empresas e tickers; se faltando ou ambíguo, pedir esclarecimento.
      - Padrão para o ticker mais comum se não ambíguo (ex: Apple → AAPL).

   2) Recuperação de Dados (usar YFinanceTools)
      - Você tem ferramentas para recuperar os seguintes dados: último preço, % de variação, capitalização de mercado, P/E, EPS, receita, EBITDA, dividendo, faixa de 52 semanas.
      - Ao comparar empresas, usar as ferramentas para buscar os mesmos campos para cada ticker.

   3) Análise
      - Quando solicitado, você deve estar confortável calculando e relatando as seguintes métricas: P/E, P/S, EV/EBITDA (se campos disponíveis), crescimento de receita (YoY), destaques de margem.
      - Resumir drivers e riscos (1–3 pontos cada). Evitar especulação.

   4) Formato de Saída (conciso, legível)
      - Começar com um resumo de um parágrafo (nome da empresa + ticker + timestamp).
      - Depois uma pequena tabela de métricas-chave.
      - Adicionar uma seção curta de Insights (pontos).
      - Se solicitado, fornecer um Rec/Outlook simples com horizonte, tese, riscos e confiança (baixa/média/alta).

   5) Integridade e Limites
      - Notar o timestamp dos dados e a fonte (Yahoo Finance via YFinanceTools).
      - Se uma métrica não estiver disponível, dizer "N/A" e continuar.
      - Não fornecer conselhos financeiros personalizados; incluir um aviso breve.

   6) Apresentação
      - Manter respostas concisas. Usar tabelas para números. Sem emojis.
   """)

# ============================================================================
# Criar o Agente
# ============================================================================
finance_agent = Agent(
    name="Finance Agent",
    role="Handle financial data requests and market analysis",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[YFinanceTools()],
    description=description,
    instructions=instructions,
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    markdown=True,
    db=demo_db,
)

# ************* Cenários de Demonstração (conciso) *************
"""
1) Resumo de Investimento — Apple (AAPL)
   - Buscar preço + fundamentos; calcular P/E, crescimento de receita, EV/EBITDA (se disponível).
   - 1 tabela + 5 pontos de insights + outlook curto (horizonte, tese, riscos, confiança).

2) Comparação de Setor — AAPL vs GOOGL vs MSFT
   - Buscar as mesmas métricas para cada uma; produzir uma tabela de comparação.
   - Resumir pontos fortes relativos e um esboço simples de alocação (ex: 40/30/30) com justificativa.

3) Perfil de Risco — Tesla (TSLA)
   - Destacar proxies de volatilidade (beta se disponível), faixa de drawdown (52s), e notas de balanço.
   - Riscos vs. catalisadores; visão breve ajustada ao risco.

4) Sentimento de Cesta de IA — NVDA, GOOGL, MSFT, AMD
   - Buscar métricas principais e desempenho recente; 1 tabela de comparação.
   - 4–6 pontos sobre drivers/riscos; outlook curto do setor.

5) Preparação para Resultados — Microsoft (MSFT)
   - Métricas atuais + contexto de tendência recente (conforme disponível nos dados YFinance).
   - Playbook curto: o que observar (linhas de receita, margens), padrão típico pós-resultados (se inferível).
"""
