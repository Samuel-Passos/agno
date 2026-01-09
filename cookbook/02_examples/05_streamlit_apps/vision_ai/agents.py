from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.utils.streamlit import get_model_with_provider

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

EXTRACTION_PROMPT = dedent("""
    Analisar esta imagem minuciosamente e fornecer insights detalhados. Por favor, incluir:

    1. **Objetos e Elementos**: Identificar e descrever todos os objetos visíveis, pessoas, animais ou itens
    2. **Conteúdo de Texto**: Extrair qualquer texto legível, placas, rótulos ou conteúdo escrito
    3. **Descrição da Cena**: Descrever o cenário, ambiente e cena geral
    5. **Contexto e Propósito**: Inferir o provável propósito, contexto ou história por trás da imagem
    6. **Detalhes Técnicos**: Comentar sobre qualidade da imagem, estilo ou aspectos fotográficos se relevante

    Fornecer uma análise abrangente que seja útil para perguntas de acompanhamento.
    Ser específico e detalhado em suas observações.
""")


def get_vision_agent(
    model_id: str = "openai:gpt-4o",
    enable_search: bool = False,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Agent:
    """Obter um Agente Vision AI unificado para análise de imagem e conversa"""

    db = PostgresDb(
        db_url=db_url,
        session_table="sessions",
        db_schema="ai",
    )

    tools = [DuckDuckGoTools()] if enable_search else []

    agent = Agent(
        name="Vision AI Agent",
        model=get_model_with_provider(model_id),
        db=db,
        id="vision-ai-agent",
        user_id=user_id,
        session_id=session_id,
        tools=tools,
        add_history_to_context=True,
        num_history_runs=5,
        instructions=dedent("""
            Você é um assistente Vision AI especializado que pode tanto analisar imagens quanto se envolver em conversa.
            
            Quando fornecido com imagens:
            1. **Análise Visual**: Identificar objetos, pessoas, animais e itens
            2. **Conteúdo de Texto**: Extrair qualquer texto legível, placas ou rótulos  
            3. **Descrição da Cena**: Descrever o cenário, ambiente e contexto
            4. **Propósito e História**: Inferir o provável propósito ou história por trás da imagem
            5. **Detalhes Técnicos**: Comentar sobre qualidade da imagem, estilo e composição
            
            Para perguntas de acompanhamento:
            - Referenciar análises de imagem anteriores em seu histórico de conversa
            - Fornecer detalhes e insights específicos
            - Usar busca web (quando habilitada) para contexto adicional
            - Manter fluxo de conversa e sugerir perguntas relacionadas
            
            Sempre fornecer:
            - Respostas abrangentes e precisas
            - Respostas bem estruturadas com seções claras
            - Tom profissional e útil
            - Detalhes específicos em vez de observações genéricas
        """),
        markdown=True,
        debug_mode=True,
    )

    return agent
