import os
from textwrap import dedent

from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.utils.log import logger
from agno.utils.streamlit import get_model_from_id


async def run_github_agent(message: str, model_id: str = "gpt-4o"):
    if not os.getenv("GITHUB_TOKEN"):
        return "Erro: Token do GitHub não fornecido"

    try:
        # Inicializar toolkit MCP
        async with MCPTools(
            command="npx -y @modelcontextprotocol/server-github"
        ) as mcp_tools:
            model = get_model_from_id(model_id)

            # Criar agente
            agent = Agent(
                tools=[mcp_tools],
                model=model,
                instructions=dedent("""\
                    Você é um assistente do GitHub. Ajudar usuários a explorar repositórios e sua atividade.
                    - Fornecer insights organizados e concisos sobre o repositório
                    - Focar em fatos e dados da API do GitHub
                    - Usar formatação markdown para melhor legibilidade
                    - Apresentar dados numéricos em tabelas quando apropriado
                    - Incluir links para páginas relevantes do GitHub quando útil
                """),
                markdown=True,
            )

            # Executar agente
            response = await agent.arun(message)
            return response.content
    except Exception as e:
        logger.error(f"Erro ao executar agente GitHub MCP: {e}")
        return f"Erro: {str(e)}"
