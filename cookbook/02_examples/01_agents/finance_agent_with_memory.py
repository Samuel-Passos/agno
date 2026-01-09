"""🗞️ Finance Agent with Memory - Seu Analista de Mercado que lembra suas preferências

1. Criar ambiente virtual e instalar dependências:
   - Executar `uv venv --python 3.12` para criar um ambiente virtual
   - Executar `source .venv/bin/activate` para ativar o ambiente virtual
   - Executar `uv pip install agno openai sqlalchemy fastapi uvicorn yfinance ddgs` para instalar as dependências
   - Executar `ag setup` para conectar seu ambiente local ao Agno
   - Exportar sua chave OpenAI: `export OPENAI_API_KEY=<your_openai_key>`
2. Executar o aplicativo:
   - Executar `python cookbook/examples/agents/financial_agent_with_memory.py` para iniciar o aplicativo
3. Conversar com o agente:
   - Abrir `https://app.agno.com/playground?endpoint=localhost%3A7777`
   - Dizer ao agente seu nome e ações favoritas
   - Pedir ao agente para analisar suas ações favoritas
"""

from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

finance_agent_with_memory = Agent(
    name="Finance Agent with Memory",
    id="financial_agent_with_memory",
    model=OpenAIChat(id="gpt-4.1"),
    tools=[YFinanceTools(), DuckDuckGoTools()],
    # Permitir que o Agente crie e gerencie memórias do usuário
    enable_agentic_memory=True,
    # Descomentar para sempre criar memórias a partir da entrada
    # pode ser usado em vez de enable_agentic_memory
    # enable_user_memories=True,
    db=SqliteDb(
        session_table="agent_sessions",
        db_file="tmp/agent_data.db",
        memory_table="agent_memory",
    ),
    # Adicionar mensagens das últimas 3 execuções às mensagens
    add_history_to_context=True,
    num_history_runs=3,
    # Adicionar a data e hora atual às instruções
    add_datetime_to_context=True,
    # Usar formatação markdown
    markdown=True,
    instructions=dedent("""\
        Você é um analista de Wall Street. Seu objetivo é ajudar usuários com análise financeira.

        Lista de verificação para diferentes tipos de análise financeira:
        1. Visão Geral do Mercado: Preço da ação, faixa de 52 semanas.
        2. Financeiro: P/E, Market Cap, EPS.
        3. Insights: Recomendações de analistas, mudanças de classificação.
        4. Contexto de Mercado: Tendências da indústria, cenário competitivo, sentimento.

        Diretrizes de formatação:
        - Usar tabelas para apresentação de dados
        - Incluir cabeçalhos de seção claros
        - Adicionar indicadores de emoji para tendências (📈 📉)
        - Destacar insights-chave com marcadores
    """),
)

# Inicializar o AgentOS com os workflows
agent_os = AgentOS(
    description="Configuração de OS de exemplo",
    agents=[finance_agent_with_memory],
)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="financial_agent_with_memory:app", reload=True)
