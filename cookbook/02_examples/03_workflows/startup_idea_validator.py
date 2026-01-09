"""
🚀 Validador de Ideia de Startup - Seu Assistente Pessoal de Validação de Negócios!

Este workflow ajuda empreendedores a validar suas ideias de startup por:
1. Esclarecer e refinar o conceito central do negócio
2. Avaliar originalidade comparada a soluções existentes
3. Definir missão e objetivos claros
4. Realizar pesquisa e análise abrangente de mercado

Por que isso é útil?
--------------------------------------------------------------------------------
• Obter feedback objetivo sobre sua ideia de startup antes de investir recursos
• Entender seu mercado total endereçável e segmentos-alvo
• Validar suposições sobre oportunidade de mercado e competição
• Definir missão e objetivos claros para guiar a execução

Quem deve usar isso?
--------------------------------------------------------------------------------
• Empreendedores e Fundadores de Startup
• Gerentes de Produto e Estrategistas de Negócios
• Equipes de Inovação
• Investidores Anjo e VCs fazendo triagem inicial

Casos de uso de exemplo:
--------------------------------------------------------------------------------
• Validação de novo produto/serviço
• Avaliação de oportunidade de mercado
• Análise competitiva
• Validação de modelo de negócios
• Segmentação de clientes-alvo
• Refinamento de missão/visão

Início Rápido:
--------------------------------------------------------------------------------
1. Instalar dependências:
   pip install openai agno

2. Definir variáveis de ambiente:
   - OPENAI_API_KEY

3. Executar:
   python startup_idea_validator.py

O workflow guiará você através da validação de sua ideia de startup com análise
e pesquisa alimentadas por IA. Use os insights para refinar seu conceito e plano de negócios!
"""

import asyncio
from typing import Any

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.utils.pprint import pprint_run_response
from agno.workflow.types import WorkflowExecutionInput
from agno.workflow.workflow import Workflow
from pydantic import BaseModel, Field


# --- Modelos de Resposta ---
class IdeaClarification(BaseModel):
    originality: str = Field(..., description="Originalidade da ideia.")
    mission: str = Field(..., description="Missão da empresa.")
    objectives: str = Field(..., description="Objetivos da empresa.")


class MarketResearch(BaseModel):
    total_addressable_market: str = Field(
        ..., description="Mercado total endereçável (TAM)."
    )
    serviceable_available_market: str = Field(
        ..., description="Mercado disponível atendível (SAM)."
    )
    serviceable_obtainable_market: str = Field(
        ..., description="Mercado obtível atendível (SOM)."
    )
    target_customer_segments: str = Field(..., description="Segmentos de clientes-alvo.")


class CompetitorAnalysis(BaseModel):
    competitors: str = Field(..., description="Lista de concorrentes identificados.")
    swot_analysis: str = Field(..., description="Análise SWOT para cada concorrente.")
    positioning: str = Field(
        ..., description="Posicionamento potencial da startup em relação aos concorrentes."
    )


class ValidationReport(BaseModel):
    executive_summary: str = Field(
        ..., description="Resumo executivo da validação."
    )
    idea_assessment: str = Field(..., description="Avaliação da ideia de startup.")
    market_opportunity: str = Field(..., description="Análise de oportunidade de mercado.")
    competitive_landscape: str = Field(
        ..., description="Visão geral do cenário competitivo."
    )
    recommendations: str = Field(..., description="Recomendações estratégicas.")
    next_steps: str = Field(..., description="Próximos passos recomendados.")


# --- Agentes ---
idea_clarifier_agent = Agent(
    name="Idea Clarifier",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "Dada uma ideia de startup do usuário, seu objetivo é refinar essa ideia.",
        "Avaliar a originalidade da ideia comparando-a com conceitos existentes.",
        "Definir a missão e objetivos da startup.",
        "Fornecer insights claros e acionáveis sobre o conceito central do negócio.",
    ],
    add_history_to_context=True,
    add_datetime_to_context=True,
    output_schema=IdeaClarification,
    debug_mode=False,
)

market_research_agent = Agent(
    name="Market Research Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions=[
        "Você recebe uma ideia de startup e a missão e objetivos da empresa.",
        "Estimar o mercado total endereçável (TAM), mercado disponível atendível (SAM) e mercado obtível atendível (SOM).",
        "Definir segmentos de clientes-alvo e suas características.",
        "Pesquisar na web por recursos e dados para apoiar sua análise.",
        "Fornecer estimativas específicas de tamanho de mercado com fontes de dados de apoio.",
    ],
    add_history_to_context=True,
    add_datetime_to_context=True,
    output_schema=MarketResearch,
)

competitor_analysis_agent = Agent(
    name="Competitor Analysis Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions=[
        "Você recebe uma ideia de startup e dados de pesquisa de mercado.",
        "Identificar concorrentes existentes no mercado.",
        "Realizar análise de Forças, Fraquezas, Oportunidades e Ameaças (SWOT) para cada concorrente.",
        "Avaliar o posicionamento potencial da startup em relação aos concorrentes.",
        "Pesquisar informações recentes de concorrentes e posicionamento de mercado.",
    ],
    add_history_to_context=True,
    add_datetime_to_context=True,
    output_schema=CompetitorAnalysis,
    debug_mode=False,
)

report_agent = Agent(
    name="Report Generator",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "Você recebe dados abrangentes sobre uma ideia de startup incluindo esclarecimento, pesquisa de mercado e análise de concorrentes.",
        "Sintetizar todas as informações em um relatório de validação abrangente.",
        "Fornecer resumo executivo claro, avaliação e recomendações acionáveis.",
        "Estruturar o relatório profissionalmente com seções e insights claros.",
        "Incluir próximos passos específicos para o empreendedor.",
    ],
    add_history_to_context=True,
    add_datetime_to_context=True,
    output_schema=ValidationReport,
    debug_mode=False,
)


# --- Função de Execução ---
async def startup_validation_execution(
    workflow: Workflow,
    execution_input: WorkflowExecutionInput,
    startup_idea: str,
    **kwargs: Any,
) -> str:
    """Executar o workflow completo de validação de ideia de startup"""

    # Obter entradas
    message: str = execution_input.input
    idea: str = startup_idea

    if not idea:
        return "❌ Nenhuma ideia de startup fornecida"

    print(f"🚀 Iniciando validação de ideia de startup para: {idea}")
    print(f"💡 Solicitação de validação: {message}")

    # Fase 1: Esclarecimento de Ideia
    print("\n🎯 FASE 1: ESCLARECIMENTO E REFINAMENTO DE IDEIA")
    print("=" * 60)

    clarification_prompt = f"""
    {message}

    Please analyze and refine the following startup idea:

    STARTUP IDEA: {idea}

    Evaluate:
    1. The originality of this idea compared to existing solutions
    2. Define a clear mission statement for this startup
    3. Outline specific, measurable objectives
    Provide insights on how to strengthen and focus the core concept.
    """

    print("🔍 Analisando e refinando o conceito de startup...")

    try:
        clarification_result = await idea_clarifier_agent.arun(clarification_prompt)
        idea_clarification = clarification_result.content

        print("✅ Esclarecimento de ideia concluído")
        print(f"📝 Missão: {idea_clarification.mission[:100]}...")

    except Exception as e:
        return f"❌ Falha ao esclarecer ideia: {str(e)}"

    # Fase 2: Pesquisa de Mercado
    print("\n📊 FASE 2: PESQUISA E ANÁLISE DE MERCADO")
    print("=" * 60)

    market_research_prompt = f"""
    Com base na ideia de startup refinada e esclarecimento abaixo, realizar pesquisa abrangente de mercado:
    IDEIA DE STARTUP: {idea}
    ORIGINALIDADE: {idea_clarification.originality}
    MISSÃO: {idea_clarification.mission}
    OBJETIVOS: {idea_clarification.objectives}
    Por favor pesquisar e fornecer:
    1. Mercado Total Endereçável (TAM) - tamanho geral do mercado
    2. Mercado Disponível Atendível (SAM) - porção que você poderia atender
    3. Mercado Obtível Atendível (SOM) - participação de mercado realista
    4. Segmentos de clientes-alvo com características detalhadas
    Usar busca web para encontrar dados e tendências atuais de mercado.
    """

    print("📈 Pesquisando tamanho de mercado e segmentos de clientes...")

    try:
        market_result = await market_research_agent.arun(market_research_prompt)
        market_research = market_result.content

        print("✅ Pesquisa de mercado concluída")
        print(f"🎯 TAM: {market_research.total_addressable_market[:100]}...")

    except Exception as e:
        return f"❌ Falha ao completar pesquisa de mercado: {str(e)}"

    # Fase 3: Análise de Concorrentes
    print("\n🏢 FASE 3: ANÁLISE DO CENÁRIO COMPETITIVO")
    print("=" * 60)

    competitor_prompt = f"""
    Com base na ideia de startup e pesquisa de mercado abaixo, analisar o cenário competitivo:
    IDEIA DE STARTUP: {idea}
    TAM: {market_research.total_addressable_market}
    SAM: {market_research.serviceable_available_market}
    SOM: {market_research.serviceable_obtainable_market}
    SEGMENTOS-ALVO: {market_research.target_customer_segments}
    Por favor pesquisar e fornecer:
    1. Identificar concorrentes diretos e indiretos
    2. Análise SWOT para cada concorrente principal
    3. Avaliação do posicionamento competitivo potencial da startup
    4. Lacunas e oportunidades de mercado
    Usar busca web para encontrar informações atuais de concorrentes.
    """

    print("🔎 Analisando cenário competitivo...")

    try:
        competitor_result = await competitor_analysis_agent.arun(competitor_prompt)
        competitor_analysis = competitor_result.content

        print("✅ Análise de concorrentes concluída")
        print(f"🏆 Posicionamento: {competitor_analysis.positioning[:100]}...")

    except Exception as e:
        return f"❌ Falha ao completar análise de concorrentes: {str(e)}"

    # Fase 4: Relatório Final de Validação
    print("\n📋 FASE 4: RELATÓRIO ABRANGENTE DE VALIDAÇÃO")
    print("=" * 60)

    report_prompt = f"""
    Sintetizar toda a pesquisa e análise em um relatório abrangente de validação de startup:

    IDEIA DE STARTUP: {idea}

    ESCLARECIMENTO DE IDEIA:
    - Originalidade: {idea_clarification.originality}
    - Missão: {idea_clarification.mission}
    - Objetivos: {idea_clarification.objectives}
    PESQUISA DE MERCADO:
    - TAM: {market_research.total_addressable_market}
    - SAM: {market_research.serviceable_available_market}
    - SOM: {market_research.serviceable_obtainable_market}
    - Segmentos-Alvo: {market_research.target_customer_segments}
    ANÁLISE DE CONCORRENTES:
    - Concorrentes: {competitor_analysis.competitors}
    - SWOT: {competitor_analysis.swot_analysis}
    - Posicionamento: {competitor_analysis.positioning}
    Criar um relatório de validação profissional com:
    1. Resumo executivo
    2. Avaliação de ideia (pontos fortes/fraquezas)
    3. Análise de oportunidade de mercado
    4. Visão geral do cenário competitivo
    5. Recomendações estratégicas
    6. Próximos passos específicos para o empreendedor
    """

    print("📝 Gerando relatório abrangente de validação...")

    try:
        final_result = await report_agent.arun(report_prompt)
        validation_report = final_result.content

        print("✅ Relatório de validação concluído")

    except Exception as e:
        return f"❌ Falha ao gerar relatório final: {str(e)}"

    # Resumo final
    summary = f"""
    🎉 VALIDAÇÃO DE IDEIA DE STARTUP CONCLUÍDA!
    📊 Resumo da Validação:
    • Ideia de Startup: {idea}
    • Esclarecimento de Ideia: ✅ Concluído
    • Pesquisa de Mercado: ✅ Concluída
    • Análise de Concorrentes: ✅ Concluída
    • Relatório Final: ✅ Gerado

    📈 Principais Insights de Mercado:
    • TAM: {market_research.total_addressable_market[:150]}...
    • Segmentos-Alvo: {market_research.target_customer_segments[:150]}...

    🏆 Posicionamento Competitivo:
    {competitor_analysis.positioning[:200]}...

    📋 RELATÓRIO ABRANGENTE DE VALIDAÇÃO:

    ## Resumo Executivo
    {validation_report.executive_summary}

    ## Avaliação de Ideia
    {validation_report.idea_assessment}

    ## Oportunidade de Mercado
    {validation_report.market_opportunity}

    ## Cenário Competitivo
    {validation_report.competitive_landscape}

    ## Recomendações Estratégicas
    {validation_report.recommendations}

    ## Próximos Passos
    {validation_report.next_steps}

    ⚠️ Aviso: Esta validação é apenas para fins informativos. Realizar due diligence adicional antes de tomar decisões de investimento.
    """

    return summary


# --- Definição do Workflow ---
startup_validation_workflow = Workflow(
    name="Startup Idea Validator",
    description="Validação abrangente de ideia de startup com pesquisa de mercado e análise competitiva",
    db=SqliteDb(
        session_table="workflow_session",
        db_file="tmp/workflows.db",
    ),
    steps=startup_validation_execution,
    session_state={},  # Inicializar estado de sessão do workflow vazio
)


if __name__ == "__main__":

    async def main():
        from rich.prompt import Prompt

        # Obter ideia do usuário
        idea = Prompt.ask(
            "[bold]Qual é sua ideia de startup?[/bold]\n✨",
            default="A marketplace for Christmas Ornaments made from leather",
        )

        print("🧪 Testando Validador de Ideia de Startup com Nova Estrutura de Workflow")
        print("=" * 70)

        result = await startup_validation_workflow.arun(
            input="Please validate this startup idea with comprehensive market research and competitive analysis",
            startup_idea=idea,
        )

        pprint_run_response(result, markdown=True)

    asyncio.run(main())
