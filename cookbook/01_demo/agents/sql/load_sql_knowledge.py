from pathlib import Path

from agno.utils.log import logger
from sql_agent import sql_agent_knowledge

# ============================================================================
# Caminho para Conhecimento do Agente SQL
# ============================================================================
cwd = Path(__file__).parent
knowledge_dir = cwd.joinpath("knowledge")

# ============================================================================
# Carregar Conhecimento do Agente SQL
# ============================================================================
if __name__ == "__main__":
    logger.info(f"Carregando Conhecimento do Agente SQL de {knowledge_dir}")
    sql_agent_knowledge.add_content(path=str(knowledge_dir))
    logger.info("Conhecimento do Agente SQL carregado.")
