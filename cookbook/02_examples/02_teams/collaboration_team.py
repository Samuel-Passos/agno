"""Exemplo de uma Equipe usando o modo `collaborate`.

No Modo Colaboração, todos os membros da equipe recebem a mesma tarefa e o líder da equipe sintetiza suas saídas em uma resposta coesa.

Executar `pip install agno arxiv pypdf pycountry` para instalar as dependências.
"""

import asyncio
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.arxiv import ArxivTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools

arxiv_download_dir = Path(__file__).parent.joinpath("tmp", "arxiv_pdfs__{session_id}")
arxiv_download_dir.mkdir(parents=True, exist_ok=True)

reddit_researcher = Agent(
    name="Reddit Researcher",
    role="Pesquisar um tópico no Reddit",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    add_name_to_context=True,
    instructions=dedent("""
    Você é um pesquisador do Reddit.
    Você receberá um tópico para pesquisar no Reddit.
    Você precisará encontrar os posts mais relevantes no Reddit.
    """),
)

hackernews_researcher = Agent(
    name="HackerNews Researcher",
    model=OpenAIChat("gpt-4o"),
    role="Pesquisar um tópico no HackerNews.",
    tools=[HackerNewsTools()],
    add_name_to_context=True,
    instructions=dedent("""
    Você é um pesquisador do HackerNews.
    Você receberá um tópico para pesquisar no HackerNews.
    Você precisará encontrar os posts mais relevantes no HackerNews.
    """),
)

academic_paper_researcher = Agent(
    name="Academic Paper Researcher",
    model=OpenAIChat("gpt-4o"),
    role="Pesquisar artigos acadêmicos e conteúdo acadêmico",
    tools=[DuckDuckGoTools(), ArxivTools(download_dir=arxiv_download_dir)],
    add_name_to_context=True,
    instructions=dedent("""
    Você é um pesquisador de artigos acadêmicos.
    Você receberá um tópico para pesquisar na literatura acadêmica.
    Você precisará encontrar artigos acadêmicos, papers e discussões acadêmicas relevantes.
    Focar em conteúdo revisado por pares e citações de fontes respeitáveis.
    Fornecer resumos breves de principais achados e metodologias.
    """),
)

twitter_researcher = Agent(
    name="Twitter Researcher",
    model=OpenAIChat("gpt-4o"),
    role="Pesquisar discussões em tendência e atualizações em tempo real",
    tools=[DuckDuckGoTools()],
    add_name_to_context=True,
    instructions=dedent("""
    Você é um pesquisador do Twitter/X.
    Você receberá um tópico para pesquisar no Twitter/X.
    Você precisará encontrar discussões em tendência, vozes influentes e atualizações em tempo real.
    Focar em contas verificadas e fontes credíveis quando possível.
    Rastrear hashtags relevantes e conversas em andamento.
    """),
)


agent_team = Team(
    name="Discussion Team",
    model=OpenAIChat("gpt-4o"),
    members=[
        reddit_researcher,
        hackernews_researcher,
        academic_paper_researcher,
        twitter_researcher,
    ],
    delegate_to_all_members=True,
    instructions=[
        "Você é um mestre de discussão.",
        "Você deve parar a discussão quando achar que a equipe chegou a um consenso.",
    ],
    markdown=True,
    show_members_responses=True,
)

if __name__ == "__main__":
    asyncio.run(
        agent_team.aprint_response(
            input="Start the discussion on the topic: 'What is the best way to learn to code?'",
            stream=True,
        )
    )
