from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.yfinance import YFinanceTools

agent = Agent(
    model=Claude(id="claude-3-7-sonnet-latest"),
    tools=[YFinanceTools()],
    instructions=[
        "Use tabelas para exibir dados.",
        "Inclua apenas a tabela em sua resposta. Nenhum outro texto.",
    ],
    markdown=True,
)
agent.print_response("What is the stock price of Apple?", stream=True)
