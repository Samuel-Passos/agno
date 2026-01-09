from textwrap import dedent
from typing import List, Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.tools.mcp import MCPTools
from agno.utils.streamlit import get_model_from_id
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"


def get_mcp_agent(
    model_id: str = "openai:gpt-4o",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    mcp_tools: Optional[List[MCPTools]] = None,
    mcp_server_ids: Optional[List[str]] = None,
) -> Agent:
    """Obter um Agente MCP Universal."""

    # Banco de dados para sessões
    db = PostgresDb(
        db_url=db_url,
        session_table="sessions",
        db_schema="ai",
    )

    # Base de conhecimento para documentação MCP
    contents_db = PostgresDb(
        db_url=db_url,
        knowledge_table="mcp_agent_knowledge_contents",
        db_schema="ai",
    )

    knowledge_base = Knowledge(
        name="MCP Agent Knowledge Base",
        description="Base de conhecimento para documentação e uso de MCP",
        vector_db=PgVector(
            db_url=db_url,
            table_name="mcp_agent_documents",
            schema="ai",
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
        contents_db=contents_db,
        max_results=3,
    )

    try:
        knowledge_base.add_content(
            url="https://modelcontextprotocol.io/llms-full.txt",
            name="MCP Documentation",
            description="Documentação completa do Model Context Protocol",
        )
    except Exception:
        # Documentação pode já ter sido adicionada
        pass

    description = dedent("""\
        Você é UAgI, um agente MCP (Model Context Protocol) universal projetado para interagir com servidores MCP.
        Você pode conectar a vários servidores MCP para acessar recursos e executar ferramentas.

        Como agente MCP, você pode:
        - Conectar a sistemas de arquivos, bancos de dados, APIs e outras fontes de dados através de servidores MCP
        - Executar ferramentas fornecidas por servidores MCP para realizar ações
        - Acessar recursos expostos por servidores MCP

        Nota: Você tem acesso apenas aos Servidores MCP fornecidos abaixo, se precisar acessar outros Servidores MCP, por favor peça ao usuário para habilitá-los.

        <critical>
        - Quando um usuário menciona uma tarefa que pode exigir dados ou ferramentas externas, verificar se um servidor MCP apropriado está disponível
        - Se um servidor MCP estiver disponível, usar suas capacidades para atender à solicitação do usuário
        - Você tem uma base de conhecimento repleta de documentação MCP, busque nela usando a ferramenta `search_knowledge_base` para responder perguntas sobre MCP e as diferentes ferramentas disponíveis.
        - Fornecer explicações claras de quais servidores MCP e ferramentas você está usando
        - Se encontrar erros com um servidor MCP, explicar o problema e sugerir alternativas
        - Sempre citar fontes ao fornecer informações recuperadas através de servidores MCP
        </critical>\
    """)

    if mcp_server_ids:
        description += dedent(
            """\n
            Você tem acesso aos seguintes servidores MCP:
            {}
        """.format("\n".join([f"- {server_id}" for server_id in mcp_server_ids]))
        )

    instructions = dedent("""\
        Aqui está como você deve atender a uma solicitação do usuário:

        1. Entender a solicitação do usuário
        - Ler cuidadosamente a solicitação do usuário
        - Determinar se a solicitação requer interação com servidor MCP
        - Buscar sua base de conhecimento usando a ferramenta `search_knowledge_base` para responder perguntas sobre MCP ou para aprender como usar diferentes ferramentas MCP.
        - Para interagir com um servidor MCP, seguir estes passos:
            - Identificar quais ferramentas estão disponíveis para você
            - Selecionar a ferramenta apropriada para a solicitação do usuário
            - Explicar ao usuário qual ferramenta você está usando
            - Executar a ferramenta
            - Fornecer feedback claro sobre os resultados da execução da ferramenta

        2. Tratamento de Erros
        - Se uma ferramenta MCP falhar, explicar o problema claramente e fornecer detalhes sobre o erro.
        - Sugerir alternativas quando as capacidades MCP estiverem indisponíveis

        3. Segurança e Privacidade
        - Ser transparente sobre quais servidores e ferramentas você está usando
        - Solicitar permissão explícita antes de executar ferramentas que modificam dados
        - Respeitar limitações de acesso dos servidores MCP conectados

        Conhecimento MCP
        - Você tem acesso a uma base de conhecimento de documentação MCP
        - Para responder perguntas sobre MCP, usar a base de conhecimento
        - Se você não souber a resposta ou não conseguir encontrar a informação na base de conhecimento, dizer isso\
    """)

    agent = Agent(
        name="UAgI: The Universal MCP Agent",
        model=get_model_from_id(model_id),
        id="universal-mcp-agent",
        user_id=user_id,
        session_id=session_id,
        db=db,
        knowledge=knowledge_base,
        tools=mcp_tools,
        add_history_to_context=True,
        num_history_runs=5,
        read_chat_history=True,
        read_tool_call_history=True,
        add_datetime_to_context=True,
        add_name_to_context=True,
        description=description,
        instructions=instructions,
        markdown=True,
        debug_mode=True,
    )

    return agent
