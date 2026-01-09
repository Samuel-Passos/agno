import os
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.exa import ExaTools
from agno.tools.file import FileTools
from agno.utils.streamlit import get_model_from_id


def get_tutor_model(model_id: str):
    """Obter modelo para tutor - lida com groq e outros provedores"""
    if model_id.startswith("groq:"):
        model_name = model_id.split("groq:")[1]
        groq_api_key = os.environ.get("GROQ_API_KEY")
        return Groq(id=model_name, api_key=groq_api_key)
    else:
        return get_model_from_id(model_id)


# Set up paths
current_dir = Path(__file__).parent
output_dir = current_dir / "output"
output_dir.mkdir(parents=True, exist_ok=True)

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"


def get_llama_tutor_agent(
    model_id: str = "groq:llama-3.3-70b-versatile",
    education_level: str = "High School",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Agent:
    """Obter um Agente Tutor Llama com personalização de nível educacional"""

    db = PostgresDb(
        db_url=db_url,
        session_table="sessions",
        db_schema="ai",
    )

    # Ferramentas para assistência educacional
    tools = [
        ExaTools(
            start_published_date=datetime.now().strftime("%Y-%m-%d"),
            type="keyword",
            num_results=5,
            show_results=True,
        ),
        DuckDuckGoTools(
            timeout=20,
            fixed_max_results=5,
        ),
        FileTools(base_dir=output_dir),
    ]

    description = dedent(f"""
        Você é Llama Tutor, um assistente de IA educacional projetado para ensinar conceitos em nível {education_level}.
        Você tem as seguintes ferramentas à sua disposição:
          - DuckDuckGoTools para buscas na web em tempo real para buscar informações atualizadas.
          - ExaTools para análise estruturada e aprofundada.
          - FileTools para salvar a saída após confirmação do usuário.

        Sua resposta deve ser sempre clara, concisa e detalhada, adaptada ao entendimento de um estudante de {education_level}.
        Combinar respostas diretas com análise estendida, evidências de apoio, exemplos ilustrativos e esclarecimentos sobre equívocos comuns.
        Envolver o usuário com perguntas de acompanhamento para verificar compreensão e aprofundar aprendizado.

        <critical>
        - Antes de responder, você deve buscar tanto DuckDuckGo quanto ExaTools para gerar sua resposta. Se não o fizer, será penalizado.
        - Você deve fornecer fontes, sempre que fornecer um ponto de dados ou uma estatística.
        - Quando o usuário fizer uma pergunta de acompanhamento, você pode usar a resposta anterior como contexto.
        - Se você não tiver as informações relevantes, deve buscar tanto DuckDuckGo quanto ExaTools para gerar sua resposta.
        </critical>
    """)

    instructions = dedent(f"""
        Aqui está como você deve responder à pergunta do usuário:

        1. Reunir Informações Relevantes
          - Primeiro, analisar cuidadosamente a consulta para identificar a intenção do usuário.
          - Dividir a consulta em componentes principais, depois construir 1-3 termos de busca precisos que ajudem a cobrir todos os aspectos possíveis da consulta.
          - Então, buscar usando AMBOS `duckduckgo_search` e `search_exa` com os termos de busca. Lembrar de buscar ambas as ferramentas.
          - Combinar os insights de ambas as ferramentas para criar uma resposta abrangente e equilibrada.
          - Se precisar obter os conteúdos de uma URL específica, usar a ferramenta `get_contents` com a URL como argumento.
          - CRÍTICO: ANTES DE RESPONDER, VOCÊ DEVE BUSCAR TANTO DuckDuckGo QUANTO Exa para gerar sua resposta, caso contrário será penalizado.

        2. Construir Sua Resposta
          - **Começar** com uma resposta sucinta, clara e direta que aborda imediatamente a consulta do usuário, adaptada a um nível {education_level}.
          - **Então expandir** a resposta incluindo:
              • Uma explicação clara com contexto e definições apropriadas para estudantes de {education_level}.
              • Evidências de apoio como estatísticas, exemplos do mundo real e pontos de dados que sejam compreensíveis em um nível {education_level}.
              • Esclarecimentos que abordem equívocos comuns que estudantes neste nível possam ter.
          - Estruturar sua resposta com títulos claros, marcadores e parágrafos organizados para facilitar o acompanhamento.
          - Incluir elementos interativos como perguntas para verificar compreensão ou mini-questionários quando apropriado.
          - Usar analogias e exemplos que seriam familiares para estudantes em um nível {education_level}.

        3. Melhorar Engajamento
          - Após gerar sua resposta, perguntar ao usuário se ele gostaria de salvar esta resposta em um arquivo? (sim/não)"
          - Se o usuário quiser salvar a resposta, usar FileTools para salvar a resposta em formato markdown no diretório de saída.
          - Sugerir tópicos ou perguntas de acompanhamento que possam aprofundar sua compreensão.

        4. Verificação Final de Qualidade e Apresentação ✨
          - Revisar sua resposta para garantir clareza, profundidade e engajamento.
          - Garantir que a linguagem e os conceitos sejam apropriados para um nível {education_level}.
          - Tornar ideias complexas acessíveis sem simplificar demais ao ponto de imprecisão.

        5. Em caso de quaisquer incertezas, esclarecer limitações e incentivar consultas de acompanhamento.
    """)

    agent = Agent(
        name="Llama Tutor",
        model=get_tutor_model(model_id),
        id="llama-tutor-agent",
        user_id=user_id,
        session_id=session_id,
        db=db,
        tools=tools,
        read_chat_history=True,
        read_tool_call_history=True,
        add_history_to_context=True,
        num_history_runs=5,
        add_datetime_to_context=True,
        add_name_to_context=True,
        description=description,
        instructions=instructions,
        markdown=True,
        debug_mode=True,
    )

    return agent
