from pathlib import Path
from textwrap import dedent
from typing import List, Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.tools.arxiv import ArxivTools
from agno.tools.exa import ExaTools
from agno.utils.streamlit import get_model_with_provider
from pydantic import BaseModel, Field

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"


# Data Models for structured outputs
class SearchTerms(BaseModel):
    terms: List[str] = Field(
        ..., description="List of search terms related to a topic."
    )


class ArxivSearchResult(BaseModel):
    title: str = Field(..., description="Title of the research paper.")
    id: str = Field(..., description="ArXiv ID of the paper.")
    authors: List[str] = Field(..., description="Authors of the paper.")
    summary: str = Field(..., description="Abstract/summary of the paper.")
    pdf_url: str = Field(..., description="URL to the PDF of the paper.")
    links: List[str] = Field(..., description="Related links to the paper.")
    reasoning: str = Field(..., description="Reasoning for selecting this paper.")


class ArxivSearchResults(BaseModel):
    results: List[ArxivSearchResult] = Field(
        ..., description="List of selected ArXiv research papers."
    )


class WebSearchResult(BaseModel):
    title: str = Field(..., description="Title of the web article.")
    summary: str = Field(..., description="Summary of the article content.")
    links: List[str] = Field(..., description="Links related to the article.")
    reasoning: str = Field(..., description="Reasoning for selecting this article.")


class WebSearchResults(BaseModel):
    results: List[WebSearchResult] = Field(
        ..., description="List of selected web search results."
    )


def get_paperpal_agents(
    model_id: str = "gpt-4o",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    arxiv_download_dir: Optional[Path] = None,
):
    """Obter agentes de pesquisa Paperpal com ferramentas"""

    # Configurar diretório de download do ArXiv
    if not arxiv_download_dir:
        arxiv_download_dir = Path(__file__).parent.parent.parent.parent.joinpath(
            "tmp", "arxiv_pdfs"
        )
        arxiv_download_dir.mkdir(parents=True, exist_ok=True)

    # Inicializar ferramentas
    arxiv_toolkit = ArxivTools(download_dir=arxiv_download_dir)
    exa_tools = ExaTools()

    db = PostgresDb(
        db_url=db_url,
        session_table="sessions",
        db_schema="ai",
    )

    # Agente Gerador de Termos de Busca
    search_term_generator = Agent(
        name="Search Term Generator",
        model=get_model_with_provider(model_id),
        db=db,
        id="search-term-generator",
        user_id=user_id,
        session_id=session_id,
        output_schema=SearchTerms,
        instructions=dedent("""
            Você é um estrategista de pesquisa especializado em gerar termos de busca estratégicos 
            para cobertura abrangente de pesquisa.

            Sua tarefa é:
            1. Analisar o tópico de pesquisa fornecido para identificar conceitos-chave e aspectos
            2. Gerar 2-3 termos de busca específicos e distintos que capturem diferentes dimensões
            3. Garantir que os termos sejam otimizados para eficácia tanto em busca acadêmica quanto na web
                            
            Focar em termos que ajudarão a encontrar:
            - Artigos de pesquisa recentes e desenvolvimentos teóricos
            - Aplicações da indústria e implementações do mundo real
            - Desafios atuais e direções futuras
            - Conexões interdisciplinares e tendências emergentes

            Fornecer termos como uma lista estruturada otimizada para bancos de dados de pesquisa e busca na web.
        """),
        markdown=True,
        debug_mode=True,
    )

    # Agente de Busca ArXiv
    arxiv_search_agent = Agent(
        name="ArXiv Research Agent",
        model=get_model_with_provider(model_id),
        db=db,
        id="arxiv-search-agent",
        user_id=user_id,
        session_id=session_id,
        tools=[arxiv_toolkit],
        output_schema=ArxivSearchResults,
        instructions=dedent("""
            Você é um especialista em pesquisa acadêmica com acesso ao banco de dados do ArXiv.

            Sua tarefa é:
            1. Buscar no ArXiv os 10 principais artigos relacionados ao termo de busca fornecido.
            2. Selecionar os 3 artigos de pesquisa mais relevantes com base em:
                - Relevância direta ao termo de busca.
                - Impacto científico (ex: citações, reputação do periódico).
                - Recenticidade da publicação.

            Para cada artigo selecionado, a saída deve estar em estrutura json com estes detalhes:
                - title
                - id
                - authors
                - um resumo conciso
                - o link PDF do artigo de pesquisa
                - links relacionados ao artigo de pesquisa
                - raciocínio para por que o artigo foi escolhido

            Garantir que os artigos de pesquisa selecionados abordem diretamente o tópico e ofereçam insights valiosos.
        """),
        markdown=True,
        debug_mode=True,
    )

    # Agente de Busca Web
    exa_search_agent = Agent(
        name="Web Research Agent",
        model=get_model_with_provider(model_id),
        db=db,
        id="exa-search-agent",
        user_id=user_id,
        session_id=session_id,
        tools=[exa_tools],
        output_schema=WebSearchResults,
        instructions=dedent("""
            Você é um especialista em busca web especializado em extrair informações de alta qualidade.

            Sua tarefa é:
            1. Dado um tópico, buscar no Exa os 10 principais artigos sobre esse tópico.
            2. Selecionar os 3 artigos mais relevantes com base em:
                - Credibilidade da fonte.
                - Profundidade e relevância do conteúdo.

            Para cada artigo selecionado, a saída deve ter:
                - title
                - um resumo conciso
                - links relacionados ao artigo
                - raciocínio para por que o artigo foi escolhido e como contribui para entender o tópico.

            Garantir que os artigos selecionados sejam credíveis, relevantes e forneçam insights significativos sobre o tópico.
        """),
        markdown=True,
        debug_mode=True,
    )

    # Agente Editor de Pesquisa
    research_editor = Agent(
        name="Research Editor",
        model=get_model_with_provider(model_id),
        db=db,
        id="research-editor",
        user_id=user_id,
        session_id=session_id,
        instructions=dedent("""
            Você é um editor de pesquisa sênior especializado em dividir tópicos e informações complexas em blogs compreensíveis, envolventes e de alta qualidade.

            Sua tarefa é:
            1. Criar um blog detalhado dentro de 1000 palavras com base no tópico fornecido.
            2. O blog deve ter no máximo 7-8 parágrafos, compreensível, intuitivo, tornando as coisas fáceis de entender para o leitor.
            3. Destacar achados-chave e fornecer uma visão geral clara e de alto nível do tópico.
            4. No final adicionar o link dos artigos de apoio, link do artigo ou quaisquer achados que você acha necessário adicionar.

            O blog deve ajudar o leitor a obter uma compreensão decente do tópico.
            O blog deve estar em formato markdown.
        """),
        markdown=True,
        debug_mode=True,
    )

    return {
        "search_term_generator": search_term_generator,
        "arxiv_search_agent": arxiv_search_agent,
        "exa_search_agent": exa_search_agent,
        "research_editor": research_editor,
        "arxiv_toolkit": arxiv_toolkit,
    }
