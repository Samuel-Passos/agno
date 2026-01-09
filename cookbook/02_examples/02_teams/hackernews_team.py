"""Exemplo de uma Equipe usando o modo `coordinate` para desempenhar o papel de um Pesquisador HackerNews.

1. Executar: `pip install openai ddgs newspaper4k lxml_html_clean agno` para instalar as dependências
2. Executar: `python cookbook/examples/teams/coordinate_mode/hackernews_team.py` para executar o agente
"""

from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.newspaper4k import Newspaper4kTools
from pydantic import BaseModel


class Article(BaseModel):
    title: str
    summary: str
    reference_links: List[str]


hn_researcher = Agent(
    name="HackerNews Researcher",
    model=OpenAIChat("gpt-4o"),
    role="Obtém as principais histórias do hackernews.",
    tools=[HackerNewsTools()],
)

web_searcher = Agent(
    name="Web Searcher",
    model=OpenAIChat("gpt-4o"),
    role="Busca informações na web sobre um tópico",
    tools=[DuckDuckGoTools()],
    add_datetime_to_context=True,
)

article_reader = Agent(
    name="Article Reader",
    role="Lê artigos de URLs.",
    tools=[Newspaper4kTools()],
)


hn_team = Team(
    name="HackerNews Team",
    model=OpenAIChat("gpt-4o"),
    members=[hn_researcher, web_searcher, article_reader],
    instructions=[
        "Primeiro, pesquisar no hackernews sobre o que o usuário está perguntando.",
        "Depois, pedir ao leitor de artigos para ler os links das histórias para obter mais informações.",
        "Importante: você deve fornecer ao leitor de artigos os links para ler.",
        "Depois, pedir ao buscador web para pesquisar cada história para obter mais informações.",
        "Finalmente, fornecer um resumo reflexivo e envolvente.",
    ],
    output_schema=Article,
    share_member_interactions=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
)

hn_team.print_response("Write an article about the top 2 stories on hackernews")
