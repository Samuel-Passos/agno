import os

from agno.agent.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai.chat import OpenAIChat
from agno.os import AgentOS
from agno.tools.notion import NotionTools
from agno.workflow.step import Step, StepInput, StepOutput
from agno.workflow.workflow import Workflow
from pydantic import BaseModel


# Modelo Pydantic para saída de classificação
class ClassificationResult(BaseModel):
    query: str
    tag: str
    message: str


# Agentes
notion_agent = Agent(
    name="Notion Manager",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        NotionTools(
            api_key=os.getenv("NOTION_API_KEY", ""),
            database_id=os.getenv("NOTION_DATABASE_ID", ""),
        )
    ],
    instructions=[
        "Você é um gerenciador de páginas Notion.",
        "Você receberá instruções com uma consulta e uma tag pré-classificada.",
        "CRÍTICO: Usar APENAS a tag exata fornecida nas instruções. NÃO criar novas tags ou modificar o nome da tag.",
        "As tags válidas são: travel, tech, general-blogs, fashion, documents",
        "Workflow:",
        "1. Pesquisar páginas existentes com a tag EXATA fornecida",
        "2. Se uma página existir: Atualizar essa página com o novo conteúdo da consulta",
        "3. Se nenhuma página existir: Criar uma nova página usando a tag EXATA fornecida",
        "Sempre preservar o nome exato da tag conforme dado nas instruções.",
    ],
)


# Funções executoras
# Passo 1: Função classificadora personalizada para atribuir tags
def classify_query(step_input: StepInput) -> StepOutput:
    """
    Classificar a consulta do usuário em uma das tags predefinidas.

    Tags disponíveis: travel, tech, general-blogs, fashion, documents
    """
    # Obter a consulta do usuário de step_input
    query = step_input.input

    # Criar um agente para classificar a consulta
    classifier_agent = Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=[
            "Você é um classificador de consultas.",
            "Classificar a consulta fornecida em UMA destas tags: travel, tech, general-blogs, fashion, documents",
            "Apenas responder com o nome da tag, nada mais.",
            "Regras de classificação:",
            "- travel: Qualquer coisa relacionada a destinos, passeios, viagens, locais, hotéis, guias de viagem, lugares para visitar",
            "- tech: Programação, software, IA, aprendizado de máquina, codificação, desenvolvimento, tópicos de tecnologia",
            "- fashion: Roupas, estilo, tendências, looks, indústria da moda",
            "- documents: Currículos, CVs, relatórios, documentos oficiais, contratos",
            "- general-blogs: Pensamentos pessoais, opiniões, conselhos de vida, conteúdo diverso",
            "",
            "Exemplos:",
            "- 'Melhores lugares para visitar na Itália' -> travel",
            "- 'Guia do tour Ha Giang Vietnã' -> travel",
            "- 'Adicionar link do site de guia de viagem' -> travel",
            "- 'Como construir um app React' -> tech",
            "- 'A ascensão da IA e aprendizado de máquina' -> tech",
            "- 'Tendências de moda 2025' -> fashion",
            "- 'Meu currículo e CV' -> documents",
            "- 'Pensamentos aleatórios sobre a vida' -> general-blogs",
        ],
    )

    # Obter classificação
    response = classifier_agent.run(query)
    tag = response.content.strip().lower()

    # Validar a tag
    valid_tags = ["travel", "tech", "general-blogs", "fashion", "documents"]
    if tag not in valid_tags:
        tag = "general-blogs"  # Fallback padrão

    # Retornar dados estruturados usando modelo Pydantic
    result = ClassificationResult(
        query=str(query), tag=tag, message=f"Consulta classificada como: {tag}"
    )

    return StepOutput(content=result)


# Função personalizada para preparar entrada para o agente Notion
def prepare_notion_input(step_input: StepInput) -> StepOutput:
    """
    Extrair o resultado da classificação e formatá-lo para o agente Notion.
    """
    # Obter o resultado da classificação do passo anterior (Classify Query)
    previous_output = step_input.previous_step_content

    # Analisá-lo em nosso modelo Pydantic se for um dict
    if isinstance(previous_output, dict):
        classification = ClassificationResult(**previous_output)
    elif isinstance(previous_output, str):
        # Se for uma string, tentar analisá-la ou usar a entrada original
        import json

        try:
            classification = ClassificationResult(**json.loads(previous_output))
        except (json.JSONDecodeError, TypeError, KeyError, ValueError):
            classification = ClassificationResult(
                query=str(step_input.input),
                tag="general-blogs",
                message="Falha ao analisar classificação",
            )
    else:
        classification = previous_output

    # Criar uma instrução clara para o agente Notion com requisito de tag EXPLÍCITO
    instruction = f"""Processar esta consulta classificada:

        Consulta: {classification.query}
        Tag: {classification.tag}

        IMPORTANTE: Você DEVE usar a tag "{classification.tag}" (uma de: travel, tech, general-blogs, fashion, documents).
        NÃO criar uma nova tag. Usar EXATAMENTE "{classification.tag}".

        Instruções:
        1. Usar ferramenta search_pages para encontrar páginas com tag "{classification.tag}"
        2. Se página existir: Usar update_page para adicionar o conteúdo da consulta
        3. Se nenhuma página existir: Usar create_page com título "Minha Coleção {classification.tag.title()}", tag "{classification.tag}", e a consulta como conteúdo

        A tag DEVE ser exatamente: {classification.tag}
    """

    return StepOutput(content=instruction)


# Passos
classify_step = Step(
    name="Classify Query",
    executor=classify_query,
    description="Classificar a consulta do usuário em uma categoria de tag",
)

notion_prep_step = Step(
    name="Prepare Notion Input",
    executor=prepare_notion_input,
    description="Formatar o resultado da classificação para o agente Notion",
)

notion_step = Step(
    name="Manage Notion Page",
    agent=notion_agent,
    description="Criar ou atualizar página Notion com base na consulta e tag",
)

# Criar o workflow
query_to_notion_workflow = Workflow(
    name="query-to-notion-workflow",
    description="Classificar consultas de usuários e organizá-las no Notion",
    db=SqliteDb(
        session_table="workflow_session",
        db_file="tmp/workflow.db",
    ),
    steps=[classify_step, notion_prep_step, notion_step],
)

# Inicializar o AgentOS
agent_os = AgentOS(
    description="Sistema de classificação de consultas e organização Notion",
    workflows=[query_to_notion_workflow],
)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="notion_manager:app", reload=True)
