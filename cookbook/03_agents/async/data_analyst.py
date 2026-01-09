"""Executar `pip install duckdb` para instalar dependências."""

import asyncio
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckdb import DuckDbTools

duckdb_tools = DuckDbTools()
duckdb_tools.create_table_from_path(
    path="https://agno-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv",
    table="movies",
)

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[duckdb_tools],
    markdown=True,
    additional_context=dedent("""\
    Você tem acesso às seguintes tabelas:
    - movies: contém informações sobre filmes do IMDB.
    """),
)
asyncio.run(agent.aprint_response("Qual é a classificação média dos filmes?"))
