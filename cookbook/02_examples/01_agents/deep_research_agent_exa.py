"""Exemplo: Agente de Pesquisa Avançado usando Ferramentas de Pesquisa Exa

Este exemplo demonstra como usar a ferramenta de pesquisa Exa para tarefas de pesquisa
complexas e estruturadas com rastreamento automático de citações.
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[ExaTools(enable_research=True, research_model="exa-research-pro")],
    instructions=dedent("""
        Você é um analista de pesquisa especialista com acesso a ferramentas de pesquisa avançadas.
        
        Quando receber um schema para usar, passá-lo para a ferramenta de pesquisa como parâmetro output_schema para a ferramenta de pesquisa. 

        A ferramenta de pesquisa tem dois parâmetros:
        - instructions (str): O tópico/pergunta de pesquisa 
        - output_schema (dict, opcional): Um schema JSON para saída estruturada

        Exemplo: Se o usuário disser "Research X. Use this schema {'type': 'object', ...}", você deve chamar a ferramenta de pesquisa com o schema.

        Se nenhum schema for fornecido, a ferramenta inferirá automaticamente um schema apropriado.

        Apresentar os achados exatamente como fornecidos pela ferramenta de pesquisa.
    """),
)

# Exemplo 1: Pesquisa básica com string simples
agent.print_response(
    "Perform a comprehensive research on the current flagship GPUs from NVIDIA, AMD and Intel. Return a table of model name, MSRP USD, TDP watts, and launch date. Include citations for each cell."
)

# Definir um schema JSON para saída de pesquisa estruturada
# research_schema = {
#     "type": "object",
#     "properties": {
#         "major_players": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "name": {"type": "string"},
#                     "role": {"type": "string"},
#                     "contributions": {"type": "string"},
#                 },
#             },
#         },
#     },
#     "required": ["major_players"],
# }

# agent.print_response(
#     f"Research the top 3 Semiconductor companies in 2024. Use this schema {research_schema}."
# )
