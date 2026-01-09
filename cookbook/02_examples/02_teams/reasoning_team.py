from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

web_agent = Agent(
    name="Web Search Agent",
    role="Lidar com solicitações de busca na web",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions=["Sempre incluir fontes"],
)

finance_agent = Agent(
    name="Finance Agent",
    role="Lidar com solicitações de dados financeiros",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools()],
    instructions=["Usar tabelas para exibir dados"],
)

team_leader = Team(
    name="Reasoning Team Leader",
    model=Claude(id="claude-3-7-sonnet-latest"),
    members=[
        web_agent,
        finance_agent,
    ],
    tools=[ReasoningTools(add_instructions=True)],
    markdown=True,
    show_members_responses=True,
)

team_leader.print_response("Hi", stream=True, show_full_reasoning=True)
team_leader.print_response(
    "What is the stock price of Apple?",
    stream=True,
    show_full_reasoning=True,
)
team_leader.print_response(
    "What's going on in New York?",
    stream=True,
    show_full_reasoning=True,
)
