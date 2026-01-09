"""💰 Gerador de Relatório de Investimento - Seu Estúdio de Análise Financeira de IA!

Este exemplo avançado demonstra como construir um sistema sofisticado de análise de investimento que combina
pesquisa de mercado, análise financeira e gerenciamento de portfólio. O workflow usa uma abordagem de três estágios:
1. Análise abrangente de ações e pesquisa de mercado
2. Avaliação e classificação de potencial de investimento
3. Recomendações estratégicas de alocação de portfólio

Capacidades principais:
- Análise de dados de mercado em tempo real
- Pesquisa financeira profissional
- Avaliação de risco de investimento
- Estratégia de alocação de portfólio
- Racional de investimento detalhado

Exemplos de empresas para analisar:
- "AAPL, MSFT, GOOGL" (Gigantes da Tecnologia)
- "NVDA, AMD, INTC" (Líderes de Semicondutores)
- "TSLA, F, GM" (Inovação Automotiva)
- "JPM, BAC, GS" (Setor Bancário)
- "AMZN, WMT, TGT" (Competição de Varejo)
- "PFE, JNJ, MRNA" (Foco em Saúde)
- "XOM, CVX, BP" (Setor de Energia)

Executar `pip install openai yfinance agno` para instalar dependências.
"""

import asyncio
import random
from pathlib import Path
from shutil import rmtree
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from agno.utils.pprint import pprint_run_response
from agno.workflow.types import WorkflowExecutionInput
from agno.workflow.workflow import Workflow
from pydantic import BaseModel


# --- Modelos de Resposta ---
class StockAnalysisResult(BaseModel):
    company_symbols: str
    market_analysis: str
    financial_metrics: str
    risk_assessment: str
    recommendations: str


class InvestmentRanking(BaseModel):
    ranked_companies: str
    investment_rationale: str
    risk_evaluation: str
    growth_potential: str


class PortfolioAllocation(BaseModel):
    allocation_strategy: str
    investment_thesis: str
    risk_management: str
    final_recommendations: str


# --- Gerenciamento de Arquivos ---
reports_dir = Path(__file__).parent.joinpath("reports", "investment")
if reports_dir.is_dir():
    rmtree(path=reports_dir, ignore_errors=True)
reports_dir.mkdir(parents=True, exist_ok=True)

stock_analyst_report = str(reports_dir.joinpath("stock_analyst_report.md"))
research_analyst_report = str(reports_dir.joinpath("research_analyst_report.md"))
investment_report = str(reports_dir.joinpath("investment_report.md"))


# --- Agentes ---
stock_analyst = Agent(
    name="Stock Analyst",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        YFinanceTools(
            company_info=True, analyst_recommendations=True, company_news=True
        )
    ],
    description=dedent("""\
    Você é MarketMaster-X, um Analista de Investimentos Sênior de elite no Goldman Sachs com expertise em:

    - Análise abrangente de mercado
    - Avaliação de demonstrações financeiras
    - Identificação de tendências da indústria
    - Avaliação de impacto de notícias
    - Análise de fatores de risco
    - Avaliação de potencial de crescimento\
    """),
    instructions=dedent("""\
    1. Pesquisa de Mercado 📊
       - Analisar fundamentos e métricas da empresa
       - Revisar desempenho recente do mercado
       - Avaliar posicionamento competitivo
       - Avaliar tendências e dinâmicas da indústria
    2. Análise Financeira 💹
       - Examinar índices financeiros-chave
       - Revisar recomendações de analistas
       - Analisar impacto de notícias recentes
       - Identificar catalisadores de crescimento
    3. Avaliação de Risco 🎯
       - Avaliar riscos de mercado
       - Avaliar desafios específicos da empresa
       - Considerar fatores macroeconômicos
       - Identificar possíveis sinais de alerta
    Nota: Esta análise é apenas para fins educacionais.\
    """),
    output_schema=StockAnalysisResult,
)

research_analyst = Agent(
    name="Research Analyst",
    model=OpenAIChat(id="gpt-4o"),
    description=dedent("""\
    Você é ValuePro-X, um Analista de Pesquisa Sênior de elite no Goldman Sachs especializado em:

    - Avaliação de oportunidades de investimento
    - Análise comparativa
    - Avaliação risco-recompensa
    - Classificação de potencial de crescimento
    - Recomendações estratégicas\
    """),
    instructions=dedent("""\
    1. Análise de Investimento 🔍
       - Avaliar o potencial de cada empresa
       - Comparar avaliações relativas
       - Avaliar vantagens competitivas
       - Considerar posicionamento de mercado
    2. Avaliação de Risco 📈
       - Analisar fatores de risco
       - Considerar condições de mercado
       - Avaliar sustentabilidade do crescimento
       - Avaliar capacidade de gestão
    3. Classificação de Empresas 🏆
       - Classificar com base no potencial de investimento
       - Fornecer racional detalhado
       - Considerar retornos ajustados ao risco
       - Explicar vantagens competitivas\
    """),
    output_schema=InvestmentRanking,
)

investment_lead = Agent(
    name="Investment Lead",
    model=OpenAIChat(id="gpt-4o"),
    description=dedent("""\
    Você é PortfolioSage-X, um Líder de Investimentos Sênior distinto no Goldman Sachs especialista em:

    - Desenvolvimento de estratégia de portfólio
    - Otimização de alocação de ativos
    - Gerenciamento de risco
    - Articulação de racional de investimento
    - Entrega de recomendações ao cliente\
    """),
    instructions=dedent("""\
    1. Estratégia de Portfólio 💼
       - Desenvolver estratégia de alocação
       - Otimizar equilíbrio risco-recompensa
       - Considerar diversificação
       - Definir prazos de investimento
    2. Racional de Investimento 📝
       - Explicar decisões de alocação
       - Apoiar com análise
       - Abordar preocupações potenciais
       - Destacar catalisadores de crescimento
    3. Entrega de Recomendações 📊
       - Apresentar alocações claras
       - Explicar tese de investimento
       - Fornecer insights acionáveis
       - Incluir considerações de risco\
    """),
    output_schema=PortfolioAllocation,
)


# --- Função de Execução ---
async def investment_analysis_execution(
    execution_input: WorkflowExecutionInput,
    companies: str,
) -> str:
    """Executar o workflow completo de análise de investimento"""

    # Obter entradas
    message: str = execution_input.input
    company_symbols: str = companies

    if not company_symbols:
        return "❌ Nenhum símbolo de empresa fornecido"

    print(f"🚀 Iniciando análise de investimento para empresas: {company_symbols}")
    print(f"💼 Solicitação de análise: {message}")

    # Fase 1: Análise de Ações
    print("\n📊 FASE 1: ANÁLISE ABRANGENTE DE AÇÕES")
    print("=" * 60)

    analysis_prompt = f"""
    {message}

    Please conduct a comprehensive analysis of the following companies: {company_symbols}

    For each company, provide:
    1. Current market position and financial metrics
    2. Recent performance and analyst recommendations
    3. Industry trends and competitive landscape
    4. Risk factors and growth potential
    5. News impact and market sentiment
    Companies to analyze: {company_symbols}
    """

    print("🔍 Analisando dados de mercado e fundamentos...")
    stock_analysis_result = await stock_analyst.arun(analysis_prompt)
    stock_analysis = stock_analysis_result.content

    # Salvar em arquivo
    with open(stock_analyst_report, "w") as f:
        f.write("# Relatório de Análise de Ações\n\n")
        f.write(f"**Empresas:** {stock_analysis.company_symbols}\n\n")
        f.write(f"## Análise de Mercado\n{stock_analysis.market_analysis}\n\n")
        f.write(f"## Métricas Financeiras\n{stock_analysis.financial_metrics}\n\n")
        f.write(f"## Avaliação de Risco\n{stock_analysis.risk_assessment}\n\n")
        f.write(f"## Recomendações\n{stock_analysis.recommendations}\n")

    print(f"✅ Análise de ações concluída e salva em {stock_analyst_report}")

    # Fase 2: Classificação de Investimento
    print("\n🏆 FASE 2: CLASSIFICAÇÃO DE POTENCIAL DE INVESTIMENTO")
    print("=" * 60)

    ranking_prompt = f"""
    Com base na análise abrangente de ações abaixo, por favor classifique essas empresas por potencial de investimento.
    ANÁLISE DE AÇÕES:
    - Análise de Mercado: {stock_analysis.market_analysis}
    - Métricas Financeiras: {stock_analysis.financial_metrics}
    - Avaliação de Risco: {stock_analysis.risk_assessment}
    - Recomendações Iniciais: {stock_analysis.recommendations}
    Por favor forneça:
    1. Classificação detalhada de empresas do melhor ao pior potencial de investimento
    2. Racional de investimento para cada empresa
    3. Avaliação de risco e estratégias de mitigação
    4. Avaliação de potencial de crescimento
    """

    print("📈 Classificando empresas por potencial de investimento...")
    ranking_result = await research_analyst.arun(ranking_prompt)
    ranking_analysis = ranking_result.content

    # Salvar em arquivo
    with open(research_analyst_report, "w") as f:
        f.write("# Relatório de Classificação de Investimento\n\n")
        f.write(f"## Classificações de Empresas\n{ranking_analysis.ranked_companies}\n\n")
        f.write(f"## Racional de Investimento\n{ranking_analysis.investment_rationale}\n\n")
        f.write(f"## Avaliação de Risco\n{ranking_analysis.risk_evaluation}\n\n")
        f.write(f"## Potencial de Crescimento\n{ranking_analysis.growth_potential}\n")

    print(f"✅ Classificação de investimento concluída e salva em {research_analyst_report}")

    # Fase 3: Estratégia de Alocação de Portfólio
    print("\n💼 FASE 3: ESTRATÉGIA DE ALOCAÇÃO DE PORTFÓLIO")
    print("=" * 60)

    portfolio_prompt = f"""
    Com base na classificação e análise de investimento abaixo, criar uma alocação estratégica de portfólio.
    CLASSIFICAÇÃO DE INVESTIMENTO:
    - Classificações de Empresas: {ranking_analysis.ranked_companies}
    - Racional de Investimento: {ranking_analysis.investment_rationale}
    - Avaliação de Risco: {ranking_analysis.risk_evaluation}
    - Potencial de Crescimento: {ranking_analysis.growth_potential}
    Por favor forneça:
    1. Percentuais de alocação específicos para cada empresa
    2. Tese de investimento e racional estratégico
    3. Abordagem de gerenciamento de risco
    4. Recomendações finais acionáveis
    """

    print("💰 Desenvolvendo estratégia de alocação de portfólio...")
    portfolio_result = await investment_lead.arun(portfolio_prompt)
    portfolio_strategy = portfolio_result.content

    # Salvar em arquivo
    with open(investment_report, "w") as f:
        f.write("# Relatório de Portfólio de Investimento\n\n")
        f.write(f"## Estratégia de Alocação\n{portfolio_strategy.allocation_strategy}\n\n")
        f.write(f"## Tese de Investimento\n{portfolio_strategy.investment_thesis}\n\n")
        f.write(f"## Gerenciamento de Risco\n{portfolio_strategy.risk_management}\n\n")
        f.write(
            f"## Recomendações Finais\n{portfolio_strategy.final_recommendations}\n"
        )

    print(f"✅ Estratégia de portfólio concluída e salva em {investment_report}")

    # Resumo final
    summary = f"""
    🎉 WORKFLOW DE ANÁLISE DE INVESTIMENTO CONCLUÍDO!

    📊 Resumo da Análise:
    • Empresas Analisadas: {company_symbols}
    • Análise de Mercado: ✅ Concluída
    • Classificação de Investimento: ✅ Concluída
    • Estratégia de Portfólio: ✅ Concluída

    📁 Relatórios Gerados:
    • Análise de Ações: {stock_analyst_report}
    • Classificação de Investimento: {research_analyst_report}
    • Estratégia de Portfólio: {investment_report}

    💡 Principais Insights:
    {portfolio_strategy.allocation_strategy[:200]}...

    ⚠️ Aviso: Esta análise é apenas para fins educacionais e não deve ser considerada como aconselhamento financeiro.
    """

    return summary


# --- Definição do Workflow ---
investment_workflow = Workflow(
    name="Investment Report Generator",
    description="Análise de investimento automatizada com pesquisa de mercado e alocação de portfólio",
    db=SqliteDb(
        session_table="workflow_session",
        db_file="tmp/workflows.db",
    ),
    steps=investment_analysis_execution,
    session_state={},  # Inicializar estado de sessão do workflow vazio
)


if __name__ == "__main__":

    async def main():
        from rich.prompt import Prompt

        # Cenários de investimento de exemplo para mostrar as capacidades do analisador
        example_scenarios = [
            "AAPL, MSFT, GOOGL",  # Gigantes da Tecnologia
            "NVDA, AMD, INTC",  # Líderes de Semicondutores
            "TSLA, F, GM",  # Inovação Automotiva
            "JPM, BAC, GS",  # Setor Bancário
            "AMZN, WMT, TGT",  # Competição de Varejo
            "PFE, JNJ, MRNA",  # Foco em Saúde
            "XOM, CVX, BP",  # Setor de Energia
        ]

        # Obter empresas do usuário com sugestão de exemplo
        companies = Prompt.ask(
            "[bold]Digite símbolos de empresas (separados por vírgula)[/bold] "
            "(ou pressione Enter para um portfólio sugerido)\n✨",
            default=random.choice(example_scenarios),
        )

        print("🧪 Testando Gerador de Relatório de Investimento com Nova Estrutura de Workflow")
        print("=" * 70)

        result = await investment_workflow.arun(
            input="Generate comprehensive investment analysis and portfolio allocation recommendations",
            companies=companies,
        )

        pprint_run_response(result, markdown=True)

    asyncio.run(main())
