"""🔍 Competitor Analysis Agent - Seu Sistema de Inteligência de Mercado Alimentado por IA!

Este exemplo demonstra como construir um agente de análise de concorrentes sofisticado que combina capacidades poderosas de busca e scraping com ferramentas de raciocínio avançadas para fornecer
inteligência competitiva abrangente. O agente realiza análise profunda de concorrentes incluindo
posicionamento de mercado, ofertas de produtos e insights estratégicos.

Capacidades principais:
- Descoberta de empresas usando busca Firecrawl
- Scraping de sites e análise de conteúdo
- Coleta de inteligência competitiva
- Análise SWOT com raciocínio
- Recomendações estratégicas
- Pensamento e análise estruturados

Exemplos de consultas para tentar:
- "Analyze OpenAI's main competitors in the LLM space"
- "Compare Uber vs Lyft in the ride-sharing market"
- "Analyze Tesla's competitive position vs traditional automakers"
- "Research fintech competitors to Stripe"
- "Analyze Nike vs Adidas in the athletic apparel market"

Dependências: `pip install openai firecrawl-py agno`
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.reasoning import ReasoningTools

competitor_analysis_agent = Agent(
    model=OpenAIChat(id="gpt-4.1"),
    tools=[
        FirecrawlTools(
            enable_search=True,
            enable_crawl=True,
            enable_mapping=True,
            formats=["markdown", "links", "html"],
            search_params={
                "limit": 2,
            },
            limit=5,
        ),
        ReasoningTools(
            add_instructions=True,
        ),
    ],
    instructions=[
        "1. Pesquisa e Descoberta Inicial:",
        "   - Usar ferramenta de busca para encontrar informações sobre a empresa-alvo",
        "   - Buscar por '[nome da empresa] competitors', 'companies like [nome da empresa]'",
        "   - Buscar relatórios da indústria e análise de mercado",
        "   - Usar a ferramenta think para planejar sua abordagem de pesquisa",
        "2. Identificação de Concorrentes:",
        "   - Buscar cada concorrente identificado usando Firecrawl",
        "   - Encontrar seus sites oficiais e fontes de informação-chave",
        "   - Mapear o cenário competitivo",
        "3. Análise de Website:",
        "   - Fazer scraping dos sites dos concorrentes usando Firecrawl",
        "   - Mapear a estrutura do site para entender suas ofertas",
        "   - Extrair informações de produtos, preços e propostas de valor",
        "   - Procurar estudos de caso e depoimentos de clientes",
        "4. Análise Competitiva Profunda:",
        "   - Usar a ferramenta analyze após coletar informações sobre cada concorrente",
        "   - Comparar recursos, preços e posicionamento de mercado",
        "   - Identificar padrões e dinâmicas competitivas",
        "   - Pensar nas implicações de suas descobertas",
        "5. Síntese Estratégica:",
        "   - Realizar análise SWOT para cada concorrente principal",
        "   - Usar raciocínio para identificar vantagens competitivas",
        "   - Analisar tendências de mercado e oportunidades",
        "   - Desenvolver recomendações estratégicas",
        "- Sempre usar a ferramenta think antes de iniciar fases principais de pesquisa",
        "- Usar a ferramenta analyze para processar descobertas e extrair insights",
        "- Buscar múltiplas perspectivas sobre cada concorrente",
        "- Verificar informações verificando múltiplas fontes",
        "- Ser minucioso mas focado em sua análise",
        "- Fornecer recomendações baseadas em evidências",
    ],
    expected_output=dedent("""\
    # Relatório de Análise Competitiva: {Target Company}

    ## Resumo Executivo
    {Visão geral de alto nível do cenário competitivo e principais descobertas}

    ## Metodologia de Pesquisa
    - Consultas de busca usadas
    - Sites analisados
    - Fontes de informação-chave

    ## Visão Geral do Mercado
    ### Contexto da Indústria
    - Tamanho do mercado e taxa de crescimento
    - Tendências e drivers-chave
    - Ambiente regulatório

    ### Cenário Competitivo
    - Principais players identificados
    - Segmentação de mercado
    - Dinâmicas competitivas

    ## Análise de Concorrentes

    ### Concorrente 1: {Name}
    #### Visão Geral da Empresa
    - Website: {URL}
    - Fundada: {Year}
    - Sede: {Location}
    - Tamanho da empresa: {Employees/Revenue if available}

    #### Produtos e Serviços
    - Ofertas principais
    - Recursos e capacidades-chave
    - Modelo de preços e níveis
    - Segmentos de mercado-alvo

    #### Análise de Presença Digital
    - Estrutura do site e experiência do usuário
    - Mensagens-chave e propostas de valor
    - Estratégia de conteúdo e recursos
    - Prova social de clientes

    #### Análise SWOT
    **Pontos Fortes:**
    - {Pontos fortes baseados em evidências}

    **Pontos Fracos:**
    - {Pontos fracos identificados}

    **Oportunidades:**
    - {Oportunidades de mercado}

    **Ameaças:**
    - {Ameaças competitivas}

    ### Concorrente 2: {Name}
    {Estrutura similar à acima}

    ### Concorrente 3: {Name}
    {Estrutura similar à acima}

    ## Análise Comparativa

    ### Matriz de Comparação de Recursos
    | Recurso | {Target} | Concorrente 1 | Concorrente 2 | Concorrente 3 |
    |---------|----------|--------------|--------------|--------------|
    | {Feature 1} | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ |
    | {Feature 2} | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ |

    ### Comparação de Preços
    | Empresa | Nível de Entrada | Profissional | Enterprise |
    |---------|-------------|--------------|------------|
    | {Detalhes de preços extraídos dos sites} |

    ### Análise de Posicionamento de Mercado
    {Análise de como cada concorrente se posiciona}

    ## Insights Estratégicos

    ### Principais Descobertas
    1. {Insight principal com evidências}
    2. {Dinâmicas competitivas observadas}
    3. {Lacunas de mercado identificadas}

    ### Vantagens Competitivas
    - {Vantagens da empresa-alvo}
    - {Diferenciadores únicos}

    ### Riscos Competitivos
    - {Principais ameaças dos concorrentes}
    - {Desafios de mercado}

    ## Recomendações Estratégicas

    ### Ações Imediatas (0-3 meses)
    1. {Respostas competitivas rápidas}
    2. {Oportunidades de baixo esforço}

    ### Estratégia de Curto Prazo (3-12 meses)
    1. {Melhorias de produtos/serviços}
    2. {Ajustes de posicionamento de mercado}

    ### Estratégia de Longo Prazo (12+ meses)
    1. {Diferenciação sustentável}
    2. {Oportunidades de expansão de mercado}

    ## Conclusão
    {Resumo da posição competitiva e imperativos estratégicos}
    """),
    markdown=True,
    add_datetime_to_context=True,
    stream_events=True,
)

competitor_analysis_agent.print_response(
    """\
    Analyze the competitive landscape for Stripe in the payments industry.
    Focus on their products, pricing models, and market positioning.\
    """,
    stream=True,
    show_full_reasoning=True,
    debug_mode=True,
)
