from typing import List

from agno.agent import Agent


def get_instructions(agent: Agent) -> List[str]:
    return [
        f"Seu nome é {agent.name}!",
        "Falar em haikus!",
        "Usar poesia para responder perguntas.",
    ]


agent = Agent(
    name="AgentX",
    instructions=get_instructions,
    markdown=True,
)
agent.print_response("Quem é você?", stream=True)
