from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

db = SqliteDb(db_file="tmp/agents.db", session_table="agent_sessions")

INTRODUCTION = """Olá, sou seu assistente pessoal. Posso ajudá-lo apenas com perguntas relacionadas a escalada de montanhas."""

agent = Agent(
    model=OpenAIChat(),
    db=db,
    introduction=INTRODUCTION,
    session_id="introduction_session_mountain_climbing",
    add_history_to_context=True,
)

agent.print_response("14er mais fácil nos EUA?")
agent.print_response("K2 é mais difícil de escalar que o Everest?")
