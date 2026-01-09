"""
Agente com Entrada e Saída Tipadas - Segurança de Tipos Completa
==================================================================
Este exemplo mostra como definir schemas de entrada e saída para seu agente.
Você obtém segurança de tipos de ponta a ponta: valida o que entra, garante o que sai.

Perfeito para construir pipelines robustos onde você precisa de contratos em ambas as extremidades.
O agente valida entradas e garante a estrutura de saída.

Conceitos-chave:
- input_schema: Um modelo Pydantic que define o que o agente aceita
- output_schema: Um modelo Pydantic que define o que o agente retorna
- Passe entrada como dict ou modelo Pydantic — ambos funcionam

Exemplos de entradas para testar:
- {"ticker": "NVDA", "analysis_type": "quick", "include_risks": True}
- {"ticker": "TSLA", "analysis_type": "deep", "include_risks": True}
"""

from typing import List, Literal, Optional

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
# Schema de Entrada — o que o agente aceita
# ============================================================================
class AnalysisRequest(BaseModel):
    """Entrada estruturada para solicitar uma análise de ação."""

    ticker: str = Field(..., description="Símbolo do ticker da ação (ex: NVDA, AAPL)")
    analysis_type: Literal["quick", "deep"] = Field(
        default="quick",
        description="quick = apenas resumo, deep = análise completa com drivers/riscos",
    )
    include_risks: bool = Field(
        default=True, description="Se deve incluir análise de riscos"
    )


# ============================================================================
# Schema de Saída — o que o agente retorna
# ============================================================================
class StockAnalysis(BaseModel):
    """Saída estruturada para análise de ações."""

    ticker: str = Field(..., description="Símbolo do ticker da ação")
    company_name: str = Field(..., description="Nome completo da empresa")
    current_price: float = Field(..., description="Preço atual da ação em USD")
    summary: str = Field(..., description="Resumo de uma linha da ação")
    key_drivers: Optional[List[str]] = Field(
        None, description="Principais drivers de crescimento (se análise profunda)"
    )
    key_risks: Optional[List[str]] = Field(
        None, description="Principais riscos (se include_risks=True)"
    )
    recommendation: str = Field(
        ..., description="Um de: Strong Buy, Buy, Hold, Sell, Strong Sell"
    )


# ============================================================================
# Instruções do Agente
# ============================================================================
instructions = """\
Você é um Agente Financeiro que produz análises estruturadas de ações.

## Parâmetros de Entrada

Você recebe solicitações estruturadas com:
- ticker: A ação a analisar
- analysis_type: "quick" (apenas resumo) ou "deep" (análise completa)
- include_risks: Se deve incluir análise de riscos

## Fluxo de Trabalho

1. Buscar dados para o ticker solicitado
2. Se analysis_type for "deep", identificar principais drivers
3. Se include_risks for True, identificar principais riscos
4. Fornecer uma recomendação clara

## Regras

- Fonte: Yahoo Finance
- Corresponder saída aos parâmetros de entrada — não incluir drivers para análise "quick"
- Recomendação deve ser uma de: Strong Buy, Buy, Hold, Sell, Strong Sell\
"""

# ============================================================================
# Criar o Agente
# ============================================================================
agent_with_typed_input_output = Agent(
    name="Agent with Typed Input Output",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    tools=[YFinanceTools()],
    input_schema=AnalysisRequest,
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
    # Opção 1: Passar entrada como dict
    response_1 = agent_with_typed_input_output.run(
        input={
            "ticker": "NVDA",
            "analysis_type": "deep",
            "include_risks": True,
        }
    )

    # Acessar a saída tipada
    analysis_1: StockAnalysis = response_1.content

    print(f"\n{'=' * 60}")
    print(f"Análise de Ação: {analysis_1.company_name} ({analysis_1.ticker})")
    print(f"{'=' * 60}")
    print(f"Preço: ${analysis_1.current_price:.2f}")
    print(f"Resumo: {analysis_1.summary}")
    if analysis_1.key_drivers:
        print("\nPrincipais Drivers:")
        for driver in analysis_1.key_drivers:
            print(f"  • {driver}")
    if analysis_1.key_risks:
        print("\nPrincipais Riscos:")
        for risk in analysis_1.key_risks:
            print(f"  • {risk}")
    print(f"\nRecomendação: {analysis_1.recommendation}")
    print(f"{'=' * 60}\n")

    # Opção 2: Passar entrada como modelo Pydantic
    request = AnalysisRequest(
        ticker="AAPL",
        analysis_type="quick",
        include_risks=False,
    )
    response_2 = agent_with_typed_input_output.run(input=request)

    # Acessar a saída tipada
    analysis_2: StockAnalysis = response_2.content

    print(f"\n{'=' * 60}")
    print(f"Análise de Ação: {analysis_2.company_name} ({analysis_2.ticker})")
    print(f"{'=' * 60}")
    print(f"Preço: ${analysis_2.current_price:.2f}")
    print(f"Resumo: {analysis_2.summary}")
    if analysis_2.key_drivers:
        print("\nPrincipais Drivers:")
        for driver in analysis_2.key_drivers:
            print(f"  • {driver}")
    if analysis_2.key_risks:
        print("\nPrincipais Riscos:")
        for risk in analysis_2.key_risks:
            print(f"  • {risk}")
    print(f"\nRecomendação: {analysis_2.recommendation}")
    print(f"{'=' * 60}\n")

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Entrada + saída tipadas são perfeitas para:

1. Endpoints de API
   @app.post("/analyze")
   def analyze(request: AnalysisRequest) -> StockAnalysis:
       return agent.run(input=request).content

2. Processamento em lote
   requests = [
       AnalysisRequest(ticker="NVDA", analysis_type="quick"),
       AnalysisRequest(ticker="AMD", analysis_type="quick"),
       AnalysisRequest(ticker="INTC", analysis_type="quick"),
   ]
   results = [agent.run(input=r).content for r in requests]

3. Composição de pipeline
   # Agente 1 produz o que o Agente 2 espera como entrada
   screening_result = screener_agent.run(input=criteria).content
   analysis_result = analysis_agent.run(input=screening_result).content

Segurança de tipos em ambas as extremidades = menos bugs, melhor ferramentaria, contratos mais claros.
"""
