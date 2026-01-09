"""Por favor instale as dependências usando:
pip install openai exa-py agno firecrawl
"""

from datetime import datetime, timedelta
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from agno.tools.firecrawl import FirecrawlTools


def calculate_start_date(days: int) -> str:
    """Calcular data de início com base no número de dias."""
    start_date = datetime.now() - timedelta(days=days)
    return start_date.strftime("%Y-%m-%d")


agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        ExaTools(start_published_date=calculate_start_date(30), type="keyword"),
        FirecrawlTools(scrape=True),
    ],
    description=dedent("""\
        Você é um analista especialista de tendências de mídia especializado em:
        1. Identificar tendências emergentes em notícias e plataformas digitais
        2. Reconhecer mudanças de padrão na cobertura da mídia
        3. Fornecer insights acionáveis baseados em dados
        4. Prever desenvolvimentos futuros potenciais
    """),
    instructions=[
        "Analisar o tópico fornecido de acordo com as especificações do usuário:",
        "1. Usar palavras-chave para realizar buscas direcionadas",
        "2. Identificar influenciadores-chave e fontes autoritárias",
        "3. Extrair temas principais e padrões recorrentes",
        "4. Fornecer recomendações acionáveis",
        "5. se obtiver menos de 2 fontes, apenas então fazer scraping delas usando ferramenta firecrawl, não fazer crawl e usá-las para gerar o relatório",
        "6. taxa de crescimento deve estar em porcentagem, e se não for possível não fornecer taxa de crescimento",
    ],
    expected_output=dedent("""\
    # Relatório de Análise de Tendências de Mídia

    ## Resumo Executivo
    {Visão geral de alto nível dos achados e métricas-chave}

    ## Análise de Tendências
    ### Métricas de Volume
    - Períodos de pico de discussão: {dates}
    - Taxa de crescimento: {percentage or dont show this}

    ## Análise de Fontes
    ### Principais Fontes
    1. {Source 1}

    2. {Source 2}


    ## Insights Acionáveis
    1. {Insight 1}
       - Evidência: {data points}
       - Ação recomendada: {action}

    ## Previsões Futuras
    1. {Prediction 1}
       - Evidência de apoio: {evidence}

    ## Referências
    {Lista detalhada de fontes com links}
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# Exemplo de uso:
analysis_prompt = """\
Analyze media trends for:
Keywords: ai agents
Sources: verge.com ,linkedin.com, x.com
"""

agent.print_response(analysis_prompt, stream=True)

# Exemplo de prompt alternativo
crypto_prompt = """\
Analyze media trends for:
Keywords: cryptocurrency, bitcoin, ethereum
Sources: coindesk.com, cointelegraph.com
"""

# agent.print_response(crypto_prompt, stream=True)
