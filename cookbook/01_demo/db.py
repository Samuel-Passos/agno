# ============================================================================
# Configurar banco de dados para armazenar sessões, memórias, métricas, avaliações e conhecimento
# ============================================================================
from agno.db.postgres import PostgresDb

# Usado para VectorDB de Conhecimento
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
demo_db = PostgresDb(id="agno-demo-db", db_url=db_url)
