"""
Agente com Ferramentas - Agente Financeiro
===========================================
Seu primeiro agente Agno: um analista financeiro orientado por dados que recupera
dados de mercado, calcula métricas-chave e entrega insights concisos.

Este exemplo mostra como dar a um agente ferramentas para interagir com fontes
de dados externas. O agente usa YFinanceTools para buscar dados de mercado em tempo real.

Exemplos de prompts para testar:
- "Qual é o preço atual da AAPL?"
- "Compare NVDA e AMD — qual parece mais forte?"
- "Me dê um resumo rápido de investimento sobre a Microsoft"
- "Qual é a relação P/E da Tesla e como ela se compara à indústria?"
- "Mostre-me as métricas-chave para as ações FAANG"
"""

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools

# ============================================================================
# Instruções do Agente
# ============================================================================
instructions = """\
Você é um Agente Financeiro — um analista orientado por dados que recupera dados de mercado,
calcula relações-chave e produz insights concisos e prontos para decisão.

## Fluxo de Trabalho

1. Esclarecer
   - Identificar tickers a partir de nomes de empresas (ex: Apple → AAPL)
   - Se ambíguo, perguntar

2. Recuperar
   - Buscar: preço, variação %, capitalização de mercado, P/E, EPS, faixa de 52 semanas
   - Para comparações, buscar os mesmos campos para cada ticker

3. Analisar
   - Calcular relações (P/E, P/S, margens) quando não fornecidas
   - Principais drivers e riscos — máximo de 2-3 pontos
   - Apenas fatos, sem especulação

4. Apresentar
   - Começar com um resumo de uma linha
   - Usar tabelas para comparações de múltiplas ações
   - Manter conciso

## Regras

- Fonte: Yahoo Finance. Sempre anotar o timestamp.
- Dados faltando? Diga "N/A" e continue.
- Sem conselhos personalizados — adicione aviso quando relevante.
- Sem emojis.\
"""

# ============================================================================
# Criar o Agente
# ============================================================================
agent_with_tools = Agent(
    name="Agent with Tools",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    tools=[YFinanceTools()],
    add_datetime_to_context=True,
    markdown=True,
)

# ============================================================================
# Executar o Agente
# ============================================================================
if __name__ == "__main__":
    agent_with_tools.print_response(
        "Me dê um resumo rápido de investimento sobre a NVIDIA", stream=True
    )

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Teste estes prompts:

1. Análise de Ação Única
   "Qual é a avaliação atual da Apple? Está cara?"

2. Comparação
   "Compare Google e Microsoft como investimentos"

3. Visão Geral do Setor
   "Mostre-me as métricas-chave para as principais ações de IA: NVDA, AMD, GOOGL, MSFT"

4. Verificação Rápida
   "A que preço a Tesla está negociando hoje?"

5. Análise Profunda
   "Detalhe as finanças da Amazon — receita, margens e crescimento"
"""
