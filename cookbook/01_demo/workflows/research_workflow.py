from textwrap import dedent
from typing import Dict, List, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.parallel import ParallelTools
from agno.tools.reasoning import ReasoningTools
from agno.workflow import Step, Workflow
from agno.workflow.parallel import Parallel
from agno.workflow.step import StepInput, StepOutput
from db import demo_db

# ============================================================================
# Criar Agentes de Pesquisa
# ============================================================================
hn_researcher = Agent(
    name="HN Researcher",
    role="Research trending topics and discussions on Hacker News",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[HackerNewsTools()],
    description=dedent("""\
        Você é o Pesquisador HN — um agente que pesquisa o Hacker News por discussões relevantes,
        tópicos em tendência e insights técnicos da comunidade de desenvolvedores.
        """),
    instructions=dedent("""\
        1. Pesquisar Hacker News por histórias, discussões e comentários relevantes sobre o tópico dado.
        2. Focar em histórias altamente votadas e comentários perspicazes.
        3. Identificar temas-chave, opiniões e detalhes técnicos da comunidade.
        4. Resumir suas descobertas em um formato claro e organizado com links para fontes.
        """),
    add_history_to_context=True,
    markdown=True,
    db=demo_db,
)

web_researcher = Agent(
    name="Web Researcher",
    role="Search the web for current information and sources",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[DuckDuckGoTools()],
    description=dedent("""\
        Você é o Pesquisador Web — um agente que pesquisa a web por informações atualizadas,
        artigos de notícias e fontes credíveis sobre qualquer tópico.
        """),
    instructions=dedent("""\
        1. Pesquisar a web por informações recentes e relevantes sobre o tópico dado.
        2. Priorizar fontes credíveis como sites de notícias, documentação oficial e publicações respeitáveis.
        3. Coletar perspectivas diversas e informações factuais.
        4. Resumir descobertas com citações claras e links.
        """),
    add_history_to_context=True,
    markdown=True,
    db=demo_db,
)

parallel_researcher = Agent(
    name="Parallel Researcher",
    role="Perform deep semantic search for high-quality content",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[ParallelTools(enable_search=True, enable_extract=True)],
    description=dedent("""\
        Você é o Pesquisador Parallel — um agente que usa busca semântica para encontrar
        conteúdo de alta qualidade e relevante de toda a web.
        """),
    instructions=dedent("""\
        1. Usar as ferramentas de busca e extração do Parallel para encontrar conteúdo altamente relevante e de qualidade.
        2. Focar em fontes autoritárias, artigos aprofundados e análise de especialistas.
        3. Fornecer contexto e resumos das descobertas mais valiosas.
        4. Incluir links para todas as fontes.
        """),
    add_history_to_context=True,
    markdown=True,
    db=demo_db,
)

# ============================================================================
# Criar Agentes Escritor e Revisor
# ============================================================================
writer = Agent(
    name="Writer",
    role="Synthesize research into compelling content",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[ReasoningTools()],
    description=dedent("""\
        Você é o Escritor — um agente que sintetiza descobertas de pesquisa em conteúdo claro,
        envolvente e bem estruturado.
        """),
    instructions=dedent("""\
        **Entrada:** A pesquisa consolidada da Fase de Pesquisa.
        **Saída:** Um relatório bem estruturado e envolvente sobre a solicitação do usuário.
        **Instruções:**
        1. Analisar e consolidar todas as descobertas de pesquisa que você recebeu.
        2. Identificar temas-chave, insights e detalhes importantes.
        3. Estruturar o conteúdo logicamente com seções e subseções claras.
        4. Escrever em um estilo claro e envolvente apropriado para o tópico.
        5. Incluir citações e links relevantes da pesquisa.
        6. Usar ferramentas de raciocínio para pensar em tópicos complexos e estruturar o conteúdo.
        """),
    add_history_to_context=True,
    markdown=True,
    db=demo_db,
)


async def consolidate_research_step_function(input: StepInput) -> StepOutput:
    """Consolidar a pesquisa dos diferentes agentes"""
    # Obter todas as saídas de etapas anteriores
    previous_step_outputs: Optional[Dict[str, StepOutput]] = input.previous_step_outputs
    # Obter a saída da etapa paralela
    parallel_step_output: Optional[StepOutput] = (
        previous_step_outputs.get("Research Phase") if previous_step_outputs else None
    )
    # Obter a lista de saídas de etapas da etapa paralela
    parallel_step_output_list: Optional[List[StepOutput]] = (
        parallel_step_output.steps if parallel_step_output else None
    )
    # Criar o conteúdo de pesquisa combinando o conteúdo das diferentes saídas de etapas
    research_content = "Por favor, use a seguinte pesquisa extraída para criar um relatório abrangente sobre a solicitação do usuário. \n\n"
    if parallel_step_output_list and len(parallel_step_output_list) > 0:
        for step_output in parallel_step_output_list:
            research_content += (
                f"## {step_output.step_name} \n\n{step_output.content}\n\n"
            )

        return StepOutput(content=research_content, success=True)

    return StepOutput(content="Nenhum conteúdo de pesquisa encontrado", success=False)


# ============================================================================
# Criar Etapas do Workflow
# ============================================================================
hn_research_step = Step(
    name="HN Research",
    agent=hn_researcher,
)
web_research_step = Step(
    name="Web Research",
    agent=web_researcher,
)
parallel_research_step = Step(
    name="Parallel Research",
    agent=parallel_researcher,
)
researcher_steps: List[Step] = [
    hn_research_step,
    web_research_step,
    parallel_research_step,
]

research_consolidation_step = Step(
    name="Consolidate Research",
    executor=consolidate_research_step_function,
)

writer_step = Step(
    name="Writer",
    agent=writer,
)

# ============================================================================
# Criar o Workflow
# ============================================================================
research_workflow = Workflow(
    name="Research Workflow",
    description=dedent("""\
        Um workflow paralelo que pesquisa informações de múltiplas fontes simultaneamente,
        depois sintetiza e revisa as informações para publicação.
        """),
    steps=[
        Parallel(*researcher_steps, name="Research Phase"),  # type: ignore
        research_consolidation_step,
        writer_step,
    ],
    db=demo_db,
)
