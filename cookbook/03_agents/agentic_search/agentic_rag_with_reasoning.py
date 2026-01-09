"""Este livro de receitas mostra como implementar RAG Agente com Raciocínio.
1. Executar: `pip install agno anthropic cohere lancedb tantivy sqlalchemy` para instalar as dependências
2. Exportar suas ANTHROPIC_API_KEY e CO_API_KEY
3. Executar: `python cookbook/agent_concepts/agentic_search/agentic_rag_with_reasoning.py` para executar o agente
"""

import asyncio

from agno.agent import Agent
from agno.knowledge.embedder.cohere import CohereEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reranker.cohere import CohereReranker
from agno.models.anthropic import Claude
from agno.tools.reasoning import ReasoningTools
from agno.vectordb.lancedb import LanceDb, SearchType

knowledge = Knowledge(
    # Usar LanceDB como banco de dados vetorial, armazenar embeddings na tabela `agno_docs`
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="agno_docs",
        search_type=SearchType.hybrid,
        embedder=CohereEmbedder(id="embed-v4.0"),
        reranker=CohereReranker(model="rerank-v3.5"),
    ),
)

asyncio.run(
    knowledge.add_contents_async(
        urls=["https://docs.agno.com/basics/agents/overview.md"]
    )
)

agent = Agent(
    model=Claude(id="claude-sonnet-4-20250514"),
    # RAG Agente é habilitado por padrão quando `knowledge` é fornecido ao Agent.
    knowledge=knowledge,
    # search_knowledge=True dá ao Agent a capacidade de buscar sob demanda
    # search_knowledge é True por padrão
    search_knowledge=True,
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        "Incluir fontes em sua resposta.",
        "Sempre buscar seu conhecimento antes de responder a pergunta.",
    ],
    markdown=True,
)

if __name__ == "__main__":
    agent.print_response(
        "O que são Agentes?",
        stream=True,
        show_full_reasoning=True,
    )
