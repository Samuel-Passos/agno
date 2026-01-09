from textwrap import dedent
from typing import Dict, List, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.firecrawl import FirecrawlTools
from pydantic import BaseModel, Field
from rich.pretty import pprint


class ContentSection(BaseModel):
    """Representa uma seção de conteúdo da página web."""

    heading: Optional[str] = Field(None, description="Cabeçalho da seção")
    content: str = Field(..., description="Texto do conteúdo da seção")


class PageInformation(BaseModel):
    """Representação estruturada de uma página web."""

    url: str = Field(..., description="URL da página")
    title: str = Field(..., description="Título da página")
    description: Optional[str] = Field(
        None, description="Meta descrição ou resumo da página"
    )
    features: Optional[List[str]] = Field(None, description="Lista de recursos principais")
    content_sections: Optional[List[ContentSection]] = Field(
        None, description="Seções principais de conteúdo da página"
    )
    links: Optional[Dict[str, str]] = Field(
        None, description="Links importantes encontrados na página com descrição"
    )
    contact_info: Optional[Dict[str, str]] = Field(
        None, description="Informações de contato se disponíveis"
    )
    metadata: Optional[Dict[str, str]] = Field(
        None, description="Metadados importantes da página"
    )


agent = Agent(
    model=OpenAIChat(id="gpt-4.1"),
    tools=[FirecrawlTools(enable_scrape=True, enable_crawl=True)],
    instructions=dedent("""
        Você é um pesquisador web especialista e extrator de conteúdo. Extrair informações abrangentes e estruturadas
        da página web fornecida. Focar em:

        1. Capturar com precisão o título da página, descrição e recursos principais
        2. Identificar e extrair seções principais de conteúdo com seus cabeçalhos
        3. Encontrar links importantes para páginas ou recursos relacionados
        4. Localizar informações de contato se disponíveis
        5. Extrair metadados relevantes que fornecem contexto sobre o site

        Seja minucioso mas conciso. Se a página tiver conteúdo extenso, priorizar as informações mais importantes.
    """).strip(),
    output_schema=PageInformation,
)

result = agent.run("Extract all information from https://www.agno.com")
pprint(result.content)
