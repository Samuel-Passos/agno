"""Exemplo de uma Equipe usando o modo `coordinate` para desempenhar o papel de uma Agência de Notícias.

1. Executar: `pip install openai ddgs newspaper4k lxml_html_clean agno` para instalar as dependências
2. Executar: `python cookbook/examples/teams/coordinate_mode/news_agency_team.py` para executar o agente
"""

from pathlib import Path

from agno.agent import Agent
from agno.models.openai.chat import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

urls_file = Path(__file__).parent.joinpath("tmp", "urls__{session_id}.md")
urls_file.parent.mkdir(parents=True, exist_ok=True)


searcher = Agent(
    name="Searcher",
    role="Busca as principais URLs para um tópico",
    instructions=[
        "Dado um tópico, primeiro gerar uma lista de 3 termos de busca relacionados a esse tópico.",
        "Para cada termo de busca, pesquisar na web e analisar os resultados. Retornar as 10 URLs mais relevantes para o tópico.",
        "Você está escrevendo para o New York Times, então a qualidade das fontes é importante.",
    ],
    tools=[DuckDuckGoTools()],
    add_datetime_to_context=True,
)
writer = Agent(
    name="Writer",
    role="Escreve um artigo de alta qualidade",
    description=(
        "Você é um escritor sênior do New York Times. Dado um tópico e uma lista de URLs, "
        "seu objetivo é escrever um artigo de alta qualidade digno do NYT sobre o tópico."
    ),
    instructions=[
        "Primeiro ler todas as URLs usando `read_article`."
        "Depois escrever um artigo de alta qualidade digno do NYT sobre o tópico."
        "O artigo deve ser bem estruturado, informativo, envolvente e cativante.",
        "Garantir que o comprimento seja pelo menos tão longo quanto uma matéria de capa do NYT -- no mínimo, 15 parágrafos.",
        "Garantir que você forneça uma opinião matizada e equilibrada, citando fatos sempre que possível.",
        "Focar em clareza, coerência e qualidade geral.",
        "Nunca inventar fatos ou plagiar. Sempre fornecer atribuição adequada.",
        "Lembre-se: você está escrevendo para o New York Times, então a qualidade do artigo é importante.",
    ],
    tools=[Newspaper4kTools()],
    add_datetime_to_context=True,
)

editor = Team(
    name="Editor",
    model=OpenAIChat("gpt-4o"),
    members=[searcher, writer],
    description="Você é um editor sênior do NYT. Dado um tópico, seu objetivo é escrever um artigo digno do NYT.",
    instructions=[
        "Primeiro pedir ao jornalista de busca para buscar as URLs mais relevantes para esse tópico.",
        "Depois pedir ao escritor para obter um rascunho envolvente do artigo.",
        "Editar, revisar e refinar o artigo para garantir que atenda aos altos padrões do New York Times.",
        "O artigo deve ser extremamente articulado e bem escrito. "
        "Focar em clareza, coerência e qualidade geral.",
        "Lembre-se: você é o guardião final antes do artigo ser publicado, então certifique-se de que o artigo está perfeito.",
    ],
    add_datetime_to_context=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
)
editor.print_response("Write an article about latest developments in AI.")
