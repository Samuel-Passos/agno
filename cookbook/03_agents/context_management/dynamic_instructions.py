from agno.agent import Agent
from agno.run import RunContext


def get_instructions(run_context: RunContext):
    if run_context.session_state and run_context.session_state.get("current_user_id"):
        return (
            f"Fazer a história sobre {run_context.session_state.get('current_user_id')}."
        )
    return "Fazer a história sobre o usuário."


agent = Agent(instructions=get_instructions)
agent.print_response("Escrever uma história de 2 frases", user_id="john.doe")
