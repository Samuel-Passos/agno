from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.anthropic import Claude
from rich.pretty import pprint

# Conexão com o banco de dados
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
db = PostgresDb(
    db_url=db_url,
    session_table="sessions",
    memory_table="user_memories",
)

user_id = "peter_rabbit"

# Criar agente com o novo sistema de memória
agent = Agent(
    model=Claude(id="claude-3-7-sonnet-latest"),
    user_id=user_id,
    db=db,
    # Habilitar o Agente para criar e gerenciar dinamicamente memórias do usuário
    enable_user_memories=True,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    agent.print_response("My name is Peter Rabbit and I like to eat carrots.")

    # Obter memórias usando o método do agente
    memories = agent.get_user_memories(user_id=user_id)
    print(f"Memories about {user_id}:")
    pprint(memories)

    agent.print_response("What is my favorite food?")
    agent.print_response("My best friend is Jemima Puddleduck.")

    # Obter memórias atualizadas
    memories = agent.get_user_memories(user_id=user_id)
    print(f"Memories about {user_id}:")
    pprint(memories)

    agent.print_response("Recommend a good lunch meal, who should i invite?")
    agent.print_response("What have we been talking about?")
