from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[DuckDuckGoTools()],
    description="Especializado em rastrear atividades de concorrentes",
    instructions="Usar as ferramentas de busca e sempre usar as informações e dados mais recentes.",
    db=SqliteDb(db_file="tmp/dbs/tool_call_compression.db"),
    compress_tool_results=True,  # Habilitar compressão de chamadas de ferramenta
)

agent.print_response(
    """
    Usar as ferramentas de busca e sempre buscar as informações e dados mais recentes.
    Pesquisar atividades recentes (últimos 3 meses) para estas empresas de IA:
    
    1. OpenAI - lançamentos de produtos, parcerias, preços
    2. Anthropic - novos recursos, acordos empresariais, financiamento
    3. Google DeepMind - avanços em pesquisa, lançamentos de produtos
    4. Meta AI - lançamentos de código aberto, artigos de pesquisa
   
    Para cada uma, encontrar ações específicas com datas e números.""",
    stream=True,
)
