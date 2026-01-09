"""
Agente com Saída Estruturada - Agente Financeiro com Respostas Tipadas
=========================================================================
Este exemplo mostra como obter respostas estruturadas e tipadas do seu agente.
Em vez de texto livre, você obtém um modelo Pydantic em que pode confiar.

Perfeito para construir pipelines, UIs ou integrações onde você precisa
de formatos de dados previsíveis. Analise, armazene, exiba — sem regex necessário.

Conceitos-chave:
- output_schema: Um modelo Pydantic que define a estrutura da resposta
- A resposta do agente sempre corresponderá a este schema
- Acesse dados estruturados via response.content

Exemplos de prompts para testar:
- "Analise NVDA"
- "Me dê um relatório sobre a Tesla"
- "Qual é o caso de investimento da Apple?"
"""

from typing import List, Optional

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools
from pydantic import BaseModel, Field

# ============================================================================
# Configuração de Armazenamento
# ============================================================================
agent_db = SqliteDb(db_file="tmp/agents.db")


# ============================================================================
# Schema de Saída Estruturada
# ============================================================================
class StockAnalysis(BaseModel):
    """Saída estruturada para análise de ações."""

    ticker: str = Field(..., description="Símbolo do ticker da ação (ex: NVDA)")
    company_name: str = Field(..., description="Nome completo da empresa")
    current_price: float = Field(..., description="Preço atual da ação em USD")
    market_cap: str = Field(..., description="Capitalização de mercado (ex: '3.2T' ou '150B')")
    pe_ratio: Optional[float] = Field(None, description="Relação P/E, se disponível")
    week_52_high: float = Field(..., description="Preço máximo de 52 semanas")
    week_52_low: float = Field(..., description="Preço mínimo de 52 semanas")
    summary: str = Field(..., description="Resumo de uma linha da ação")
    key_drivers: List[str] = Field(..., description="2-3 principais drivers de crescimento")
    key_risks: List[str] = Field(..., description="2-3 principais riscos")
    recommendation: str = Field(
        ..., description="Um de: Strong Buy, Buy, Hold, Sell, Strong Sell"
    )


# ============================================================================
# Instruções do Agente
# ============================================================================
instructions = """\
Você é um Agente Financeiro — um analista orientado por dados que recupera dados de mercado,
calcula relações-chave e produz insights concisos e prontos para decisão.

## Fluxo de Trabalho

1. Recuperar
   - Buscar: preço, variação %, capitalização de mercado, P/E, EPS, faixa de 52 semanas
   - Obter todos os campos necessários para a análise

2. Analisar
   - Identificar 2-3 principais drivers (o que está funcionando)
   - Identificar 2-3 principais riscos (o que pode dar errado)
   - Apenas fatos, sem especulação

3. Recomendar
   - Com base nos dados, forneça uma recomendação clara
   - Seja decisivo, mas note que isso não é um conselho personalizado

## Regras

- Fonte: Yahoo Finance
- Dados faltando? Use null para campos opcionais, estime para campos obrigatórios
- Recomendação deve ser uma de: Strong Buy, Buy, Hold, Sell, Strong Sell\
"""

# ============================================================================
# Criar o Agente
# ============================================================================
agent_with_structured_output = Agent(
    name="Agent with Structured Output",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    tools=[YFinanceTools()],
    output_schema=StockAnalysis,
    db=agent_db,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

# ============================================================================
# Executar o Agente
# ============================================================================
if __name__ == "__main__":
    # Obter saída estruturada
    response = agent_with_structured_output.run("Analise NVIDIA")

    # Acessar os dados tipados
    analysis: StockAnalysis = response.content

    # Usar programaticamente
    print(f"\n{'=' * 60}")
    print(f"Análise de Ação: {analysis.company_name} ({analysis.ticker})")
    print(f"{'=' * 60}")
    print(f"Preço: ${analysis.current_price:.2f}")
    print(f"Capitalização de Mercado: {analysis.market_cap}")
    print(f"Relação P/E: {analysis.pe_ratio or 'N/A'}")
    print(f"Faixa de 52 Semanas: ${analysis.week_52_low:.2f} - ${analysis.week_52_high:.2f}")
    print(f"\nResumo: {analysis.summary}")
    print("\nPrincipais Drivers:")
    for driver in analysis.key_drivers:
        print(f"  • {driver}")
    print("\nPrincipais Riscos:")
    for risk in analysis.key_risks:
        print(f"  • {risk}")
    print(f"\nRecomendação: {analysis.recommendation}")
    print(f"{'=' * 60}\n")

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Saída estruturada é perfeita para:

1. Construir UIs
   analysis = agent.run("Analise TSLA").content
   render_stock_card(analysis)

2. Armazenar em bancos de dados
   db.insert("analyses", analysis.model_dump())

3. Comparar ações
   nvda = agent.run("Analise NVDA").content
   amd = agent.run("Analise AMD").content
   if nvda.pe_ratio < amd.pe_ratio:
       print(f"{nvda.ticker} é mais barata por P/E")

4. Construir pipelines
   tickers = ["AAPL", "GOOGL", "MSFT"]
   analyses = [agent.run(f"Analise {t}").content for t in tickers]

O schema garante que você sempre obtenha os campos esperados.
Sem parsing, sem surpresas.
"""
