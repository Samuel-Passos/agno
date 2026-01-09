from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    add_location_to_context=True,
    tools=[DuckDuckGoTools(cache_results=True)],
)
agent.print_response("Em qual cidade estou?")
agent.print_response("Quais são as notícias atuais sobre minha cidade?")
