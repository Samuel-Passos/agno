from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.hackernews import HackerNewsTools
from pydantic import BaseModel, Field


class ResearchTopic(BaseModel):
    """Tópico de pesquisa estruturado com requisitos específicos"""

    topic: str
    focus_areas: List[str] = Field(description="Áreas específicas para focar")
    target_audience: str = Field(description="Para quem esta pesquisa é")
    sources_required: int = Field(description="Número de fontes necessárias", default=5)


# Definir agentes
hackernews_agent = Agent(
    name="Hackernews Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[HackerNewsTools()],
    role="Extrair insights-chave e conteúdo de posts do Hackernews",
)

hackernews_agent.print_response(
    input=ResearchTopic(
        topic="AI",
        focus_areas=["AI", "Machine Learning"],
        target_audience="Developers",
        sources_required=5,
    )
)
