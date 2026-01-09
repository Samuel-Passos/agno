"""Exemplo de uma Equipe usando o modo `coordinate` para desempenhar o papel de um CEO de uma Startup.

1. Executar: `pip install agno exa_py slack_sdk pgvector psycopg` para instalar as dependências
2. Adicionar as seguintes variáveis de ambiente:
- `EXA_API_KEY`
- `SLACK_TOKEN`
"""

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.exa import ExaTools
from agno.tools.slack import SlackTools
from agno.tools.yfinance import YFinanceTools
from agno.vectordb.pgvector.pgvector import PgVector

knowledge = Knowledge(
    vector_db=PgVector(
        table_name="autonomous_startup_team",
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
    ),
)

knowledge.add_content(
    path="cookbook/teams/coordinate/data", reader=PDFReader(chunk=True)
)


support_channel = "testing"
sales_channel = "sales"


legal_compliance_agent = Agent(
    name="Legal Compliance Agent",
    role="Conformidade Legal",
    model=OpenAIChat("gpt-4o"),
    tools=[ExaTools()],
    knowledge=knowledge,
    instructions=[
        "Você é o Agente de Conformidade Legal de uma startup, responsável por garantir conformidade legal e regulatória.",
        "Responsabilidades Principais:",
        "1. Revisar e validar todos os documentos legais e contratos",
        "2. Monitorar mudanças regulatórias e atualizar políticas de conformidade",
        "3. Avaliar riscos legais em operações de negócios e desenvolvimento de produtos",
        "4. Garantir conformidade de privacidade e segurança de dados (GDPR, CCPA, etc.)",
        "5. Fornecer orientação legal sobre proteção de propriedade intelectual",
        "6. Criar e manter documentação de conformidade",
        "7. Revisar materiais de marketing para conformidade legal",
        "8. Aconselhar sobre direito trabalhista e políticas de RH",
    ],
    add_datetime_to_context=True,
    markdown=True,
)

product_manager_agent = Agent(
    name="Product Manager Agent",
    role="Gerente de Produto",
    model=OpenAIChat("gpt-4o"),
    knowledge=knowledge,
    instructions=[
        "Você é o Gerente de Produto de uma startup, responsável pela estratégia e execução do produto.",
        "Responsabilidades Principais:",
        "1. Definir e manter o roteiro do produto",
        "2. Coletar e analisar feedback do usuário para identificar necessidades",
        "3. Escrever requisitos e especificações detalhadas do produto",
        "4. Priorizar recursos com base no impacto nos negócios e valor do usuário",
        "5. Colaborar com equipes técnicas sobre viabilidade de implementação",
        "6. Monitorar métricas e KPIs do produto",
        "7. Realizar análise competitiva",
        "8. Liderar lançamentos de produtos e estratégias de go-to-market",
        "9. Equilibrar necessidades do usuário com objetivos de negócios",
    ],
    add_datetime_to_context=True,
    markdown=True,
    tools=[],
)

market_research_agent = Agent(
    name="Market Research Agent",
    role="Pesquisa de Mercado",
    model=OpenAIChat("gpt-4o"),
    tools=[DuckDuckGoTools(), ExaTools()],
    knowledge=knowledge,
    instructions=[
        "Você é o Agente de Pesquisa de Mercado de uma startup, responsável por inteligência e análise de mercado.",
        "Responsabilidades Principais:",
        "1. Realizar análise abrangente de mercado e estimativa de tamanho",
        "2. Rastrear e analisar estratégias e ofertas de concorrentes",
        "3. Identificar tendências de mercado e oportunidades emergentes",
        "4. Pesquisar segmentos de clientes e personas de compradores",
        "5. Analisar estratégias de preços no mercado",
        "6. Monitorar notícias e desenvolvimentos da indústria",
        "7. Criar relatórios detalhados de pesquisa de mercado",
        "8. Fornecer insights baseados em dados para tomada de decisão",
    ],
    add_datetime_to_context=True,
    markdown=True,
)

sales_agent = Agent(
    name="Sales Agent",
    role="Vendas",
    model=OpenAIChat("gpt-4o"),
    tools=[SlackTools()],
    knowledge=knowledge,
    instructions=[
        "Você é o Agente de Vendas e Parcerias de uma startup, responsável por impulsionar o crescimento de receita e parcerias estratégicas.",
        "Responsabilidades Principais:",
        "1. Identificar e qualificar oportunidades potenciais de parceria e negócios",
        "2. Avaliar propostas de parceria e negociar termos",
        "3. Manter relacionamentos com parceiros e clientes existentes",
        "5. Colaborar com o Agente de Conformidade Legal em revisões de contratos",
        "6. Trabalhar com o Gerente de Produto em solicitações de recursos de parceiros",
        f"7. Documentar e comunicar todos os detalhes de parceria no canal #{sales_channel}",
        "",
        "Diretrizes de Comunicação:",
        "1. Sempre responder profissionalmente e prontamente a consultas de parceria",
        "2. Incluir todos os detalhes relevantes ao compartilhar oportunidades de parceria",
        "3. Destacar riscos e benefícios potenciais em propostas de parceria",
        "4. Manter documentação clara de todas as discussões e acordos",
        "5. Garantir transferência adequada para membros relevantes da equipe quando necessário",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


financial_analyst_agent = Agent(
    name="Financial Analyst Agent",
    role="Analista Financeiro",
    model=OpenAIChat("gpt-4o"),
    knowledge=knowledge,
    tools=[YFinanceTools()],
    instructions=[
        "Você é o Analista Financeiro de uma startup, responsável por planejamento e análise financeira.",
        "Responsabilidades Principais:",
        "1. Desenvolver modelos e projeções financeiras",
        "2. Criar e analisar previsões de receita",
        "3. Avaliar estratégias de preços e economia unitária",
        "4. Preparar relatórios e apresentações para investidores",
        "5. Monitorar fluxo de caixa e taxa de queima",
        "6. Analisar condições de mercado e tendências financeiras",
        "7. Avaliar oportunidades de investimento potenciais",
        "8. Rastrear métricas e KPIs financeiros-chave",
        "9. Fornecer insights financeiros para decisões estratégicas",
    ],
    add_datetime_to_context=True,
    markdown=True,
)

customer_support_agent = Agent(
    name="Customer Support Agent",
    role="Suporte ao Cliente",
    model=OpenAIChat("gpt-4o"),
    knowledge=knowledge,
    tools=[SlackTools()],
    instructions=[
        "Você é o Agente de Suporte ao Cliente de uma startup, responsável por lidar com consultas de clientes e manter a satisfação do cliente.",
        f"Quando um usuário reportar um problema ou a pergunta que você não pode responder, sempre enviá-lo para o canal Slack #{support_channel} com todos os detalhes relevantes.",
        "Sempre manter uma atitude profissional e prestativa enquanto garante o roteamento adequado de problemas para os canais corretos.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


autonomous_startup_team = Team(
    name="CEO Agent",
    model=OpenAIChat("gpt-4o"),
    instructions=[
        "Você é o CEO de uma startup, responsável pela liderança geral e sucesso.",
        " Sempre delegar tarefa ao agente gerente de produto para que ele possa pesquisar a base de conhecimento.",
        "Instruir todos os agentes a usar a base de conhecimento para responder perguntas.",
        "Responsabilidades Principais:",
        "1. Definir e comunicar visão e estratégia da empresa",
        "2. Coordenar e priorizar atividades da equipe",
        "3. Tomar decisões estratégicas de alto nível",
        "4. Avaliar oportunidades e riscos",
        "5. Gerenciar alocação de recursos",
        "6. Impulsionar crescimento e inovação",
        "7. Quando um cliente pedir ajuda ou reportar um problema, delegar imediatamente ao Agente de Suporte ao Cliente",
        "8. Quando qualquer consulta de parceria, vendas ou desenvolvimento de negócios chegar, delegar imediatamente ao Agente de Vendas",
        "",
        "Diretrizes de Coordenação da Equipe:",
        "1. Desenvolvimento de Produto:",
        "   - Consultar Gerente de Produto para priorização de recursos",
        "   - Usar Pesquisa de Mercado para validação",
        "   - Verificar Conformidade Legal para novos recursos",
        "2. Entrada no Mercado:",
        "   - Combinar insights de Pesquisa de Mercado e Vendas",
        "   - Validar viabilidade financeira com Analista Financeiro",
        "3. Planejamento Estratégico:",
        "   - Coletar contribuições de todos os membros da equipe",
        "   - Priorizar com base em oportunidade de mercado e recursos",
        "4. Gerenciamento de Riscos:",
        "   - Consultar Conformidade Legal para riscos regulatórios",
        "   - Revisar avaliações de risco do Analista Financeiro",
        "5. Suporte ao Cliente:",
        "   - Garantir que todas as consultas de clientes sejam tratadas prontamente e profissionalmente",
        "   - Manter uma atitude positiva e prestativa",
        "   - Escalar problemas críticos para a equipe apropriada",
        "",
        "Sempre manter uma visão equilibrada de execução de curto prazo e estratégia de longo prazo.",
    ],
    members=[
        product_manager_agent,
        market_research_agent,
        financial_analyst_agent,
        legal_compliance_agent,
        customer_support_agent,
        sales_agent,
    ],
    add_datetime_to_context=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
)

autonomous_startup_team.print_response(
    input="I want to start a startup that sells AI agents to businesses. What is the best way to do this?",
    stream=True,
)


autonomous_startup_team.print_response(
    input="Give me good marketing campaign for buzzai?",
    stream=True,
)

autonomous_startup_team.print_response(
    input="What is my company and what are the monetization strategies?",
    stream=True,
)

# autonomous_startup_team.print_response(
#     input="Read the partnership details and give me details about the partnership with InnovateAI",
#     stream=True,
# )
