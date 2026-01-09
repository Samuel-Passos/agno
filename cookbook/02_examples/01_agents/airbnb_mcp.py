"""🏠 MCP Airbnb Agent - Buscar listagens do Airbnb!

Este exemplo mostra como criar um agente que usa MCP e Llama 4 para buscar listagens do Airbnb.

1. Executar: `pip install groq mcp agno` para instalar as dependências
2. Exportar sua GROQ_API_KEY
3. Executar: `python cookbook/examples/agents/airbnb_mcp.py` para executar o agente
"""

import asyncio
from textwrap import dedent

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.mcp import MCPTools
from agno.tools.reasoning import ReasoningTools


async def run_agent(message: str) -> None:
    async with MCPTools(
        "npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt"
    ) as mcp_tools:
        agent = Agent(
            model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
            tools=[ReasoningTools(add_instructions=True), mcp_tools],
            instructions=dedent("""\
            ## Instruções Gerais
            - Sempre começar usando a ferramenta think para mapear os passos necessários para completar a tarefa.
            - Após receber resultados de ferramentas, usar a ferramenta think como um rascunho para validar os resultados quanto à correção
            - Antes de responder ao usuário, usar a ferramenta think para anotar pensamentos e ideias finais.
            - Apresentar saídas finais em tabelas bem organizadas sempre que possível.
            - Sempre fornecer links para as listagens em sua resposta.
            - Mostrar suas 10 principais recomendações em uma tabela e fazer um caso para por que cada uma é a melhor escolha.

            ## Usando a ferramenta think
            Em cada passo, usar a ferramenta think como um rascunho para:
            - Reformular o objeto em suas próprias palavras para garantir compreensão completa.
            - Listar as regras específicas que se aplicam à solicitação atual
            - Verificar se todas as informações necessárias foram coletadas e são válidas
            - Verificar se a ação planejada completa a tarefa\
            """),
            add_datetime_to_context=True,
            markdown=True,
        )
        await agent.aprint_response(message, stream=True)


if __name__ == "__main__":
    task = dedent("""\
    I'm traveling to San Francisco from April 20th - May 8th. Can you find me the best deals for a 1 bedroom apartment?
    I'd like a dedicated workspace and close proximity to public transport.\
    """)
    asyncio.run(run_agent(task))
