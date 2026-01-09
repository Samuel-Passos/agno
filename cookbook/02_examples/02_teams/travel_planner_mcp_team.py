"""
Este exemplo demonstra como usar o protocolo MCP para coordenar uma equipe de agentes.

Pré-requisitos:
- Google Maps:
    - Definir a variável de ambiente `GOOGLE_MAPS_API_KEY` com sua chave de API do Google Maps.
    Você pode obter o token de API do Google Cloud Console:
    https://console.cloud.google.com/projectselector2/google/maps-apis/credentials

    - Você também precisa ativar a API de Validação de Endereços para seu.
    https://console.developers.google.com/apis/api/addressvalidation.googleapis.com

- Apify:
    - Definir a variável de ambiente `APIFY_TOKEN` com seu token de API do Apify.
    Você pode obter o token de API do Apify Console:
    https://console.apify.com/settings/integrations

"""

import asyncio
import os
from textwrap import dedent
from typing import List, Optional

from agno.agent import Agent
from agno.models.openai.chat import OpenAIChat
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.mcp import MCPTools
from agno.tools.reasoning import ReasoningTools
from mcp import StdioServerParameters
from pydantic import BaseModel


# Definir modelos de resposta
class AirbnbListing(BaseModel):
    name: str
    description: str
    address: Optional[str] = None
    price: Optional[str] = None
    dates_available: Optional[List[str]] = None
    url: Optional[str] = None


class Attraction(BaseModel):
    name: str
    description: str
    location: str
    rating: Optional[float] = None
    visit_duration: Optional[str] = None
    best_time_to_visit: Optional[str] = None


class WeatherInfo(BaseModel):
    average_temperature: str
    precipitation: str
    recommendations: str


class TravelPlan(BaseModel):
    airbnb_listings: List[AirbnbListing]
    attractions: List[Attraction]
    weather_info: Optional[WeatherInfo] = None
    suggested_itinerary: Optional[List[str]] = None


async def run_team():
    env = {
        **os.environ,
        "GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY"),
    }
    # Definir parâmetros do servidor
    airbnb_server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
        env=env,
    )

    maps_server_params = StdioServerParameters(
        command="npx", args=["-y", "@modelcontextprotocol/server-google-maps"], env=env
    )

    # Usar AsyncExitStack para gerenciar múltiplos gerenciadores de contexto
    async with (
        MCPTools(server_params=airbnb_server_params) as airbnb_tools,
        MCPTools(server_params=maps_server_params) as maps_tools,
    ):
        # Criar todos os agentes
        airbnb_agent = Agent(
            name="Airbnb",
            role="Airbnb Agent",
            model=OpenAIChat("gpt-4o"),
            tools=[airbnb_tools],
            instructions=dedent("""\
                Você é um agente que pode encontrar listagens do Airbnb para um local fornecido.\
            """),
            add_datetime_to_context=True,
        )

        maps_agent = Agent(
            name="Google Maps",
            role="Agente de Serviços de Localização",
            model=OpenAIChat("gpt-4o"),
            tools=[maps_tools],
            instructions=dedent("""\
                Você é um agente que ajuda a encontrar atrações, pontos de interesse,
                e fornece direções em destinos de viagem. Ajudar a planejar rotas
                de viagem e encontrar lugares interessantes para visitar para um local e data fornecidos.\
            """),
            add_datetime_to_context=True,
        )

        web_search_agent = Agent(
            name="Web Search",
            role="Agente de Busca Web",
            model=OpenAIChat("gpt-4o"),
            tools=[DuckDuckGoTools(cache_results=True)],
            instructions=dedent("""\
                Você é um agente que pode pesquisar na web por informações.
                Pesquisar informações sobre um local fornecido.\
            """),
            add_datetime_to_context=True,
        )

        weather_search_agent = Agent(
            name="Weather Search",
            role="Agente de Busca de Clima",
            model=OpenAIChat("gpt-4o"),
            tools=[DuckDuckGoTools()],
            instructions=dedent("""\
                Você é um agente que pode pesquisar na web por informações.
                Pesquisar a previsão do tempo para um local e data fornecidos.\
            """),
            add_datetime_to_context=True,
        )

        # Criar e executar a equipe
        team = Team(
            name="SkyPlanner",
            model=OpenAIChat("gpt-4o"),
            members=[
                airbnb_agent,
                web_search_agent,
                maps_agent,
                weather_search_agent,
            ],
            instructions=[
                "Planejar um itinerário completo para a viagem.",
                "Continuar perguntando aos membros individuais da equipe até ter TODAS as informações necessárias.",
                "Pensar na melhor forma de abordar a tarefa.",
            ],
            tools=[ReasoningTools(add_instructions=True)],
            output_schema=TravelPlan,
            markdown=True,
            debug_mode=True,
            show_members_responses=True,
            add_datetime_to_context=True,
        )

        # Executar a tarefa da equipe
        await team.aprint_response(
            dedent("""\
            I want to travel to San Francisco from New York sometime in May.
            I am one person going for 2 weeks.
            Plan my travel itinerary.
            Make sure to include the best attractions, restaurants, and activities.
            Make sure to include the best Airbnb listings.
            Make sure to include the weather information.\
        """)
        )


if __name__ == "__main__":
    asyncio.run(run_team())
