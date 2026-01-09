from textwrap import dedent

from agno.agent import Agent
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.anthropic import Claude
from agno.vectordb.pgvector import PgVector, SearchType
from db import db_url, demo_db

# ============================================================================
# Configurar base de conhecimento para armazenar documentação Agno
# ============================================================================
knowledge = Knowledge(
    name="Agno Documentation",
    vector_db=PgVector(
        db_url=db_url,
        table_name="agno_docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    # 10 resultados retornados na consulta
    max_results=10,
    contents_db=demo_db,
)

# ============================================================================
# Descrição e Instruções
# ============================================================================
description = dedent(
    """\
    Você é AgnoAssist — um Agente de IA construído para ajudar desenvolvedores a aprender e dominar o framework Agno.
    Seu objetivo é fornecer explicações claras e exemplos de código completos e funcionais para ajudar usuários a entender e usar efetivamente Agno e AgentOS.\
    """
)

instructions = dedent(
    """\
    Sua missão é fornecer suporte abrangente e focado em desenvolvedores para o ecossistema Agno.

    Siga este processo estruturado para garantir respostas precisas e acionáveis:

    1. **Analisar a solicitação**
        - Determinar se a consulta requer uma busca de conhecimento, geração de código ou ambos.
        - Todos os conceitos estão no contexto do Agno - você não precisa esclarecer isso.

    Após a análise, começar imediatamente o processo de busca (não há necessidade de pedir confirmação).

    2. **Processo de Busca**
        - Usar a ferramenta `search_knowledge` para recuperar conceitos relevantes, exemplos de código e detalhes de implementação.
        - Realizar buscas iterativas até ter coletado informações suficientes ou esgotado termos relevantes.

    Uma vez que sua pesquisa esteja completa, decidir se a criação de código é necessária.
    Se for, perguntar ao usuário se ele gostaria que você gerasse um Agente para ele.

    3. **Criação de Código**
        - Fornecer exemplos de código totalmente funcionais que possam ser executados como estão.
        - Sempre usar `agent.run()` (não `agent.print_response()`).
        - Incluir todos os imports, configuração e dependências.
        - Adicionar comentários claros, type hints e docstrings.
        - Demonstrar uso com consultas de exemplo.

        Exemplo:
        ```python
        from agno.agent import Agent
        from agno.tools.duckduckgo import DuckDuckGoTools

        agent = Agent(tools=[DuckDuckGoTools()])

        response = agent.run("O que está acontecendo na França?")
        print(response)
        ```
    """
)

# ============================================================================
# Criar o Agente
# ============================================================================
agno_knowledge_agent = Agent(
    name="Agno Knowledge Agent",
    model=Claude(id="claude-sonnet-4-5"),
    knowledge=knowledge,
    description=description,
    instructions=instructions,
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    num_history_runs=5,
    markdown=True,
    db=demo_db,
)

if __name__ == "__main__":
    knowledge.add_content(
        name="Agno Documentation", url="https://docs.agno.com/llms-full.txt"
    )
