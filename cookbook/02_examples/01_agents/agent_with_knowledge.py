from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.anthropic import Claude
from agno.vectordb.pgvector import PgVector, SearchType

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
agent_db = PostgresDb(db_url=db_url)

# Criar uma base de conhecimento com a documentação do Agno
knowledge = Knowledge(
    vector_db=PgVector(
        table_name="vectors",
        db_url=db_url,
        search_type=SearchType.hybrid,
        # Usar OpenAI para embeddings
        embedder=OpenAIEmbedder(id="text-embedding-3-small", dimensions=1536),
    ),
)

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    knowledge=knowledge,
    db=agent_db,
    add_history_to_context=True,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    # Carregar documentação do Agno na base de conhecimento
    knowledge.add_content(name="Agno Docs", url="https://docs.agno.com/introduction.md")

    # Perguntar ao agente sobre Agno
    agent.print_response("What is Agno?", stream=True)
