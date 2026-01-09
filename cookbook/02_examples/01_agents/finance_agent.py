"""🗞️ Finance Agent - Seu Analista de Mercado Pessoal!

Este exemplo mostra como criar um analista financeiro sofisticado que fornece
insights abrangentes de mercado usando dados em tempo real. O agente combina dados do mercado de ações,
recomendações de analistas, informações da empresa e últimas notícias para entregar análise
financeira de nível profissional.

Exemplos de prompts para tentar:
- "What's the latest news and financial performance of Apple (AAPL)?"
- "Give me a detailed analysis of Tesla's (TSLA) current market position"
- "How are Microsoft's (MSFT) financials looking? Include analyst recommendations"
- "Analyze NVIDIA's (NVDA) stock performance and future outlook"
- "What's the market saying about Amazon's (AMZN) latest quarter?"

Execute: `pip install openai yfinance agno` para instalar as dependências
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

finance_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        YFinanceTools(),
    ],
    instructions=dedent("""\
        Você é um analista experiente de Wall Street com profunda expertise em análise de mercado! 📊

        Siga estes passos para análise financeira abrangente:
        1. Visão Geral do Mercado
           - Preço da ação mais recente
           - Máxima e mínima de 52 semanas
        2. Análise Profunda Financeira
           - Métricas-chave (P/E, Market Cap, EPS)
        3. Insights Profissionais
           - Detalhamento de recomendações de analistas
           - Mudanças recentes de classificação

        4. Contexto de Mercado
           - Tendências e posicionamento da indústria
           - Análise competitiva
           - Indicadores de sentimento do mercado

        Seu estilo de relatório:
        - Comece com um resumo executivo
        - Use tabelas para apresentação de dados
        - Inclua cabeçalhos de seção claros
        - Adicione indicadores de emoji para tendências (📈 📉)
        - Destaque insights-chave com marcadores
        - Compare métricas com médias da indústria
        - Inclua explicações de termos técnicos
        - Termine com uma análise prospectiva

        Divulgação de Riscos:
        - Sempre destaque fatores de risco potenciais
        - Observe incertezas do mercado
        - Mencione preocupações regulatórias relevantes
    """),
    add_datetime_to_context=True,
    markdown=True,
)

# Exemplo de uso com solicitação de análise de mercado detalhada
finance_agent.print_response(
    "What's the latest news and financial performance of Apple (AAPL)?", stream=True
)

# Exemplo de análise de mercado de semicondutores
finance_agent.print_response(
    dedent("""\
    Analyze the semiconductor market performance focusing on:
    - NVIDIA (NVDA)
    - AMD (AMD)
    - Intel (INTC)
    - Taiwan Semiconductor (TSM)
    Compare their market positions, growth metrics, and future outlook."""),
    stream=True,
)

# Exemplo de análise de mercado automotivo
finance_agent.print_response(
    dedent("""\
    Evaluate the automotive industry's current state:
    - Tesla (TSLA)
    - Ford (F)
    - General Motors (GM)
    - Toyota (TM)
    Include EV transition progress and traditional auto metrics."""),
    stream=True,
)

# Mais exemplos de prompts para explorar:
"""
Consultas de análise avançadas:
1. "Compare Tesla's valuation metrics with traditional automakers"
2. "Analyze the impact of recent product launches on AMD's stock performance"
3. "How do Meta's financial metrics compare to its social media peers?"
4. "Evaluate Netflix's subscriber growth impact on financial metrics"
5. "Break down Amazon's revenue streams and segment performance"

Análises específicas da indústria:
Semiconductor Market:
1. "How is the chip shortage affecting TSMC's market position?"
2. "Compare NVIDIA's AI chip revenue growth with competitors"
3. "Analyze Intel's foundry strategy impact on stock performance"
4. "Evaluate semiconductor equipment makers like ASML and Applied Materials"

Automotive Industry:
1. "Compare EV manufacturers' production metrics and margins"
2. "Analyze traditional automakers' EV transition progress"
3. "How are rising interest rates impacting auto sales and stock performance?"
4. "Compare Tesla's profitability metrics with traditional auto manufacturers"
"""
