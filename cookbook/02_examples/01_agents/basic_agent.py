from agno.agent import Agent
from agno.models.anthropic import Claude

agent = Agent(
    model=Claude(id="claude-3-7-sonnet-latest"),
    instructions="Você é um agente focado em responder em uma linha. Todas as suas respostas devem ser super concisas e focadas.",
    markdown=True,
)
runx = agent.run("What is the stock price of Apple?")
