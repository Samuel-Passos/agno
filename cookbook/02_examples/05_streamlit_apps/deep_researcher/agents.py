from typing import Optional

from agno.agent import Agent
from agno.models.nebius import Nebius
from agno.tools.scrapegraph import ScrapeGraphTools
from agno.utils.log import logger
from agno.workflow import Workflow

# --- Agents Definition ---
searcher_agent = Agent(
    name="Research Searcher",
    tools=[ScrapeGraphTools()],
    model=Nebius(id="deepseek-ai/DeepSeek-V3-0324"),
    markdown=True,
    description=(
        "Você é ResearchBot-X, um especialista em encontrar e extrair informações de alta qualidade e "
        "atualizadas da web. Seu trabalho é coletar fontes abrangentes, "
        "confiáveis e diversas sobre o tópico fornecido."
    ),
    instructions=(
        "1. Buscar as fontes mais recentes e autoritárias sobre o tópico\n"
        "2. Extrair fatos-chave, estatísticas e opiniões de especialistas de múltiplas fontes\n"
        "3. Cobrir diferentes perspectivas e destacar quaisquer desacordos ou controvérsias\n"
        "4. Incluir pontos de dados relevantes e insights de especialistas quando possível\n"
        "5. Organizar descobertas em um formato claro e estruturado\n"
        "6. Sempre mencionar as referências e fontes do conteúdo\n"
        "7. Ser abrangente e detalhado em sua pesquisa\n"
        "8. Focar em fontes credíveis como sites de notícias, documentos oficiais, artigos de pesquisa"
    ),
)

analyst_agent = Agent(
    name="Research Analyst",
    model=Nebius(id="deepseek-ai/DeepSeek-V3-0324"),
    markdown=True,
    description=(
        "Você é AnalystBot-X, um pensador crítico que sintetiza descobertas de pesquisa "
        "em insights acionáveis. Seu trabalho é analisar, comparar e interpretar as "
        "informações fornecidas pelo pesquisador."
    ),
    instructions=(
        "1. Identificar temas-chave, tendências e padrões na pesquisa\n"
        "2. Destacar as descobertas mais importantes e suas implicações\n"
        "3. Notar quaisquer contradições ou áreas de incerteza\n"
        "4. Sugerir áreas para investigação adicional se houver lacunas\n"
        "5. Apresentar análise em um formato estruturado e fácil de ler\n"
        "6. Extrair e listar APENAS os links de referência que foram realmente fornecidos\n"
        "7. NÃO criar, inventar ou alucinar quaisquer links ou fontes\n"
        "8. Se nenhuma referência foi fornecida, declarar isso claramente\n"
        "9. Focar em insights acionáveis e implicações práticas"
    ),
)

writer_agent = Agent(
    name="Research Writer",
    model=Nebius(id="deepseek-ai/DeepSeek-V3-0324"),
    markdown=True,
    description=(
        "Você é WriterBot-X, um escritor técnico profissional. Seu trabalho é criar "
        "um relatório claro, envolvente e bem estruturado com base no resumo do analista."
    ),
    instructions=(
        "1. Escrever uma introdução envolvente que estabeleça o contexto\n"
        "2. Organizar descobertas principais em seções lógicas com cabeçalhos claros\n"
        "3. Usar marcadores, tabelas ou listas para clareza quando apropriado\n"
        "4. Concluir com um resumo e recomendações acionáveis\n"
        "5. Incluir uma seção de Referências APENAS se links reais foram fornecidos\n"
        "6. Usar APENAS os links de referência que foram explicitamente fornecidos pelo analista\n"
        "7. Formatar referências como links markdown clicáveis quando disponíveis\n"
        "8. Nunca adicionar links falsos ou inventados - apenas usar fontes verificadas\n"
        "9. Garantir que o relatório seja profissional, claro e acionável"
    ),
)


# --- Main Execution Function ---
def deep_research_execution(
    session_state,
    topic: str = None,
) -> str:
    """
    Deep research workflow execution function.

    Args:
        session_state: The shared session state
        topic: Research topic
    """

    if not topic:
        return "❌ Nenhum tópico de pesquisa fornecido. Por favor, especifique um tópico."

    logger.info(f"Executando workflow de pesquisa profunda para tópico: {topic}")

    # Passo 1: Pesquisa
    logger.info("Iniciando fase de pesquisa")
    research_content = searcher_agent.run(topic)

    if not research_content or not research_content.content:
        return f"❌ Falha ao coletar informações de pesquisa para tópico: {topic}"

    # Passo 2: Análise
    logger.info("Iniciando fase de análise")
    analysis = analyst_agent.run(research_content.content)

    if not analysis or not analysis.content:
        return f"❌ Falha ao analisar descobertas de pesquisa para tópico: {topic}"

    # Passo 3: Escrita do Relatório
    logger.info("Iniciando fase de escrita do relatório")
    report = writer_agent.run(analysis.content)

    if not report or not report.content:
        return f"❌ Falha ao gerar relatório final para tópico: {topic}"

    logger.info("Workflow de pesquisa profunda concluído com sucesso")
    return report.content


# --- Workflow Definition ---
def get_deep_researcher_workflow(
    model_id: str = "nebius:deepseek-ai/DeepSeek-V3-0324",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Workflow:
    """Obter um Workflow de Pesquisa Profunda com pipeline multi-agente"""

    return Workflow(
        name="Deep Researcher",
        description="Assistente de pesquisa alimentado por IA com workflow multi-agente para pesquisa abrangente, análise e geração de relatórios",
        steps=deep_research_execution,
        session_state={},
    )
