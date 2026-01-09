"""🎨 Gerador de Post de Blog v2.0 - Seu Estúdio de Criação de Conteúdo de IA!

Este exemplo avançado demonstra como construir um gerador sofisticado de posts de blog usando
a nova arquitetura de workflow v2.0. O workflow combina capacidades de pesquisa web com
expertise profissional de escrita usando uma abordagem multi-estágio:

1. Pesquisa web inteligente e coleta de fontes
2. Extração e processamento de conteúdo
3. Escrita profissional de post de blog com citações adequadas

Capacidades principais:
- Pesquisa web avançada e avaliação de fontes
- Raspagem e processamento de conteúdo
- Escrita profissional com otimização SEO
- Cache automático de conteúdo para eficiência
- Atribuição de fontes e verificação de fatos
"""

import asyncio
import json
from textwrap import dedent
from typing import Dict, Optional

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow.workflow import Workflow
from pydantic import BaseModel, Field


# --- Modelos de Resposta ---
class NewsArticle(BaseModel):
    title: str = Field(..., description="Título do artigo.")
    url: str = Field(..., description="Link para o artigo.")
    summary: Optional[str] = Field(
        ..., description="Resumo do artigo se disponível."
    )


class SearchResults(BaseModel):
    articles: list[NewsArticle]


class ScrapedArticle(BaseModel):
    title: str = Field(..., description="Título do artigo.")
    url: str = Field(..., description="Link para o artigo.")
    summary: Optional[str] = Field(
        ..., description="Resumo do artigo se disponível."
    )
    content: Optional[str] = Field(
        ...,
        description="Conteúdo completo do artigo em formato markdown. None se o conteúdo não estiver disponível.",
    )


# --- Agentes ---
research_agent = Agent(
    name="Blog Research Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    description=dedent("""\
    Você é BlogResearch-X, um assistente de pesquisa de elite especializado em descobrir
    fontes de alta qualidade para conteúdo de blog convincente. Sua expertise inclui:

    - Encontrar fontes autorizadas e em tendência
    - Avaliar credibilidade e relevância do conteúdo
    - Identificar perspectivas diversas e opiniões de especialistas
    - Descobrir ângulos únicos e insights
    - Garantir cobertura abrangente do tópico
    """),
    instructions=dedent("""\
    1. Estratégia de Busca 🔍
       - Encontrar 10-15 fontes relevantes e selecionar as 5-7 melhores
       - Priorizar conteúdo recente e autorizado
       - Procurar ângulos únicos e insights de especialistas
    2. Avaliação de Fontes 📊
       - Verificar credibilidade e expertise da fonte
       - Verificar datas de publicação para atualidade
       - Avaliar profundidade e singularidade do conteúdo
    3. Diversidade de Perspectivas 🌐
       - Incluir diferentes pontos de vista
       - Coletar opiniões tanto mainstream quanto de especialistas
       - Encontrar dados e estatísticas de apoio
    """),
    output_schema=SearchResults,
)

content_scraper_agent = Agent(
    name="Content Scraper Agent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[Newspaper4kTools()],
    description=dedent("""\
    Você é ContentBot-X, um especialista em extrair e processar conteúdo digital
    para criação de blog. Sua expertise inclui:

    - Extração eficiente de conteúdo
    - Formatação e estruturação inteligente
    - Identificação de informações-chave
    - Preservação de citações e estatísticas
    - Manutenção de atribuição de fontes
    """),
    instructions=dedent("""\
    1. Extração de Conteúdo 📑
       - Extrair conteúdo do artigo
       - Preservar citações e estatísticas importantes
       - Manter atribuição adequada
       - Lidar com paywalls graciosamente
    2. Processamento de Conteúdo 🔄
       - Formatar texto em markdown limpo
       - Preservar informações-chave
       - Estruturar conteúdo logicamente
    3. Controle de Qualidade ✅
       - Verificar relevância do conteúdo
       - Garantir extração precisa
       - Manter legibilidade
    """),
    output_schema=ScrapedArticle,
)

blog_writer_agent = Agent(
    name="Blog Writer Agent",
    model=OpenAIChat(id="gpt-4o"),
    description=dedent("""\
    Você é BlogMaster-X, um criador de conteúdo de elite combinando excelência jornalística
    com expertise em marketing digital. Seus pontos fortes incluem:

    - Criar manchetes dignas de viral
    - Escrever introduções envolventes
    - Estruturar conteúdo para consumo digital
    - Incorporar pesquisa perfeitamente
    - Otimizar para SEO mantendo qualidade
    - Criar conclusões compartilháveis
    """),
    instructions=dedent("""\
    1. Estratégia de Conteúdo 📝
       - Criar manchetes que chamam atenção
       - Escrever introduções convincentes
       - Estruturar conteúdo para engajamento
       - Incluir subtítulos relevantes
    2. Excelência na Escrita ✍️
       - Equilibrar expertise com acessibilidade
       - Usar linguagem clara e envolvente
       - Incluir exemplos relevantes
       - Incorporar estatísticas naturalmente
    3. Integração de Fontes 🔍
       - Citar fontes adequadamente
       - Incluir citações de especialistas
       - Manter precisão factual
    4. Otimização Digital 💻
       - Estruturar para escaneabilidade
       - Incluir takeaways compartilháveis
       - Otimizar para SEO
       - Adicionar subtítulos envolventes

    Formatar seu post de blog com esta estrutura:
    # {Manchete Digna de Viral}

    ## Introdução
    {Gancho envolvente e contexto}

    ## {Seção Convincente 1}
    {Insights-chave e análise}
    {Citações de especialistas e estatísticas}

    ## {Seção Envolvente 2}
    {Exploração mais profunda}
    {Exemplos do mundo real}

    ## {Seção Prática 3}
    {Insights acionáveis}
    {Recomendações de especialistas}

    ## Principais Takeaways
    - {Insight compartilhável 1}
    - {Takeaway prático 2}
    - {Achado notável 3}

    ## Fontes
    {Fontes adequadamente atribuídas com links}
    """),
    markdown=True,
)


# --- Funções Auxiliares ---
def get_cached_blog_post(session_state, topic: str) -> Optional[str]:
    """Obter post de blog em cache do estado da sessão do workflow"""
    logger.info("Verificando se existe post de blog em cache")
    return session_state.get("blog_posts", {}).get(topic)


def cache_blog_post(session_state, topic: str, blog_post: str):
    """Armazenar post de blog em cache no estado da sessão do workflow"""
    logger.info(f"Salvando post de blog para tópico: {topic}")
    if "blog_posts" not in session_state:
        session_state["blog_posts"] = {}
    session_state["blog_posts"][topic] = blog_post


def get_cached_search_results(session_state, topic: str) -> Optional[SearchResults]:
    """Obter resultados de busca em cache do estado da sessão do workflow"""
    logger.info("Verificando se existem resultados de busca em cache")
    search_results = session_state.get("search_results", {}).get(topic)
    if search_results and isinstance(search_results, dict):
        try:
            return SearchResults.model_validate(search_results)
        except Exception as e:
            logger.warning(f"Não foi possível validar resultados de busca em cache: {e}")
    return search_results if isinstance(search_results, SearchResults) else None


def cache_search_results(session_state, topic: str, search_results: SearchResults):
    """Armazenar resultados de busca em cache no estado da sessão do workflow"""
    logger.info(f"Salvando resultados de busca para tópico: {topic}")
    if "search_results" not in session_state:
        session_state["search_results"] = {}
    session_state["search_results"][topic] = search_results.model_dump()


def get_cached_scraped_articles(
    session_state, topic: str
) -> Optional[Dict[str, ScrapedArticle]]:
    """Obter artigos raspados em cache do estado da sessão do workflow"""
    logger.info("Verificando se existem artigos raspados em cache")
    scraped_articles = session_state.get("scraped_articles", {}).get(topic)
    if scraped_articles and isinstance(scraped_articles, dict):
        try:
            return {
                url: ScrapedArticle.model_validate(article)
                for url, article in scraped_articles.items()
            }
        except Exception as e:
            logger.warning(f"Não foi possível validar artigos raspados em cache: {e}")
    return scraped_articles if isinstance(scraped_articles, dict) else None


def cache_scraped_articles(
    session_state, topic: str, scraped_articles: Dict[str, ScrapedArticle]
):
    """Armazenar artigos raspados em cache no estado da sessão do workflow"""
    logger.info(f"Salvando artigos raspados para tópico: {topic}")
    if "scraped_articles" not in session_state:
        session_state["scraped_articles"] = {}
    session_state["scraped_articles"][topic] = {
        url: article.model_dump() for url, article in scraped_articles.items()
    }


async def get_search_results(
    session_state, topic: str, use_cache: bool = True, num_attempts: int = 3
) -> Optional[SearchResults]:
    """Obter resultados de busca com suporte a cache"""

    # Verificar cache primeiro
    if use_cache:
        cached_results = get_cached_search_results(session_state, topic)
        if cached_results:
            logger.info(f"Encontrados {len(cached_results.articles)} artigos em cache.")
            return cached_results

    # Buscar novos resultados
    for attempt in range(num_attempts):
        try:
            print(
                f"🔍 Pesquisando artigos sobre: {topic} (tentativa {attempt + 1}/{num_attempts})"
            )
            response = await research_agent.arun(topic)

            if (
                response
                and response.content
                and isinstance(response.content, SearchResults)
            ):
                article_count = len(response.content.articles)
                logger.info(f"Encontrados {article_count} artigos na tentativa {attempt + 1}")
                print(f"✅ Encontrados {article_count} artigos relevantes")

                # Armazenar resultados em cache
                cache_search_results(session_state, topic, response.content)
                return response.content
            else:
                logger.warning(
                    f"Tentativa {attempt + 1}/{num_attempts} falhou: Tipo de resposta inválido"
                )

        except Exception as e:
            logger.warning(f"Tentativa {attempt + 1}/{num_attempts} falhou: {str(e)}")

    logger.error(f"Falha ao obter resultados de busca após {num_attempts} tentativas")
    return None


async def scrape_articles(
    session_state,
    topic: str,
    search_results: SearchResults,
    use_cache: bool = True,
) -> Dict[str, ScrapedArticle]:
    """Raspar artigos com suporte a cache"""

    # Verificar cache primeiro
    if use_cache:
        cached_articles = get_cached_scraped_articles(session_state, topic)
        if cached_articles:
            logger.info(f"Encontrados {len(cached_articles)} artigos raspados em cache.")
            return cached_articles

    scraped_articles: Dict[str, ScrapedArticle] = {}

    print(f"📄 Raspando {len(search_results.articles)} artigos...")

    for i, article in enumerate(search_results.articles, 1):
        try:
            print(
                f"📖 Raspando artigo {i}/{len(search_results.articles)}: {article.title[:50]}..."
            )
            response = await content_scraper_agent.arun(article.url)

            if (
                response
                and response.content
                and isinstance(response.content, ScrapedArticle)
            ):
                scraped_articles[response.content.url] = response.content
                logger.info(f"Artigo raspado: {response.content.url}")
                print(f"✅ Raspado com sucesso: {response.content.title[:50]}...")
            else:
                print(f"❌ Falha ao raspar: {article.title[:50]}...")

        except Exception as e:
            logger.warning(f"Falha ao raspar {article.url}: {str(e)}")
            print(f"❌ Erro ao raspar: {article.title[:50]}...")

    # Armazenar artigos raspados em cache
    cache_scraped_articles(session_state, topic, scraped_articles)
    return scraped_articles


# --- Função Principal de Execução ---
async def blog_generation_execution(
    session_state,
    topic: str = None,
    use_search_cache: bool = True,
    use_scrape_cache: bool = True,
    use_blog_cache: bool = True,
) -> str:
    """
    Função de execução do workflow de geração de post de blog.

    Args:
        session_state: O estado compartilhado da sessão
        topic: Tópico do post de blog (se não fornecido, usa execution_input.input)
        use_search_cache: Se deve usar resultados de busca em cache
        use_scrape_cache: Se deve usar artigos raspados em cache
        use_blog_cache: Se deve usar posts de blog em cache
    """

    blog_topic = topic

    if not blog_topic:
        return "❌ Nenhum tópico de blog fornecido. Por favor, especifique um tópico."

    print(f"🎨 Gerando post de blog sobre: {blog_topic}")
    print("=" * 60)

    # Verificar post de blog em cache primeiro
    if use_blog_cache:
        cached_blog = get_cached_blog_post(session_state, blog_topic)
        if cached_blog:
            print("📋 Post de blog em cache encontrado!")
            return cached_blog

    # Fase 1: Pesquisa e coleta de fontes
    print("\n🔍 FASE 1: PESQUISA E COLETA DE FONTES")
    print("=" * 50)

    search_results = await get_search_results(
        session_state, blog_topic, use_search_cache
    )

    if not search_results or len(search_results.articles) == 0:
        return f"❌ Desculpe, não foi possível encontrar artigos sobre o tópico: {blog_topic}"

    print(f"📊 Encontradas {len(search_results.articles)} fontes relevantes:")
    for i, article in enumerate(search_results.articles, 1):
        print(f"   {i}. {article.title[:60]}...")

    # Fase 2: Extração de conteúdo
    print("\n📄 FASE 2: EXTRAÇÃO DE CONTEÚDO")
    print("=" * 50)

    scraped_articles = await scrape_articles(
        session_state, blog_topic, search_results, use_scrape_cache
    )

    if not scraped_articles:
        return f"❌ Não foi possível extrair conteúdo de nenhum artigo para o tópico: {blog_topic}"

    print(f"📖 Conteúdo extraído com sucesso de {len(scraped_articles)} artigos")

    # Fase 3: Escrita do post de blog
    print("\n✍️ FASE 3: CRIAÇÃO DO POST DE BLOG")
    print("=" * 50)

    # Preparar entrada para o escritor
    writer_input = {
        "topic": blog_topic,
        "articles": [article.model_dump() for article in scraped_articles.values()],
    }

    print("🤖 IA está criando seu post de blog...")
    writer_response = await blog_writer_agent.arun(json.dumps(writer_input, indent=2))

    if not writer_response or not writer_response.content:
        return f"❌ Falha ao gerar post de blog para o tópico: {blog_topic}"

    blog_post = writer_response.content

    # Armazenar post de blog em cache
    cache_blog_post(session_state, blog_topic, blog_post)

    print("✅ Post de blog gerado com sucesso!")
    print(f"📝 Comprimento: {len(blog_post)} caracteres")
    print(f"📚 Fontes: {len(scraped_articles)} artigos")

    return blog_post


# --- Definição do Workflow ---
blog_generator_workflow = Workflow(
    name="Blog Post Generator",
    description="Gerador avançado de posts de blog com capacidades de pesquisa e criação de conteúdo",
    db=SqliteDb(
        session_table="workflow_session",
        db_file="tmp/blog_generator.db",
    ),
    steps=blog_generation_execution,
    session_state={},  # Inicializar estado de sessão vazio para cache
)


if __name__ == "__main__":
    import random

    async def main():
        # Tópicos de exemplo divertidos para mostrar a versatilidade do gerador
        example_topics = [
            "The Rise of Artificial General Intelligence: Latest Breakthroughs",
            "How Quantum Computing is Revolutionizing Cybersecurity",
            "Sustainable Living in 2024: Practical Tips for Reducing Carbon Footprint",
            "The Future of Work: AI and Human Collaboration",
            "Space Tourism: From Science Fiction to Reality",
            "Mindfulness and Mental Health in the Digital Age",
            "The Evolution of Electric Vehicles: Current State and Future Trends",
            "Why Cats Secretly Run the Internet",
            "The Science Behind Why Pizza Tastes Better at 2 AM",
            "How Rubber Ducks Revolutionized Software Development",
        ]

        # Testar com um tópico aleatório
        topic = random.choice(example_topics)

        print("🧪 Testando Gerador de Post de Blog v2.0")
        print("=" * 60)
        print(f"📝 Tópico: {topic}")
        print()

        # Generate the blog post
        resp = await blog_generator_workflow.arun(
            topic=topic,
            use_search_cache=True,
            use_scrape_cache=True,
            use_blog_cache=True,
        )

        pprint_run_response(resp, markdown=True, show_time=True)

    asyncio.run(main())
