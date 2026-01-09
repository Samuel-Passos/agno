from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    add_datetime_to_context=True,
    timezone_identifier="Etc/UTC",
)
agent.print_response(
    "Qual é a data e hora atuais? Qual é a hora atual em NYC?"
)
