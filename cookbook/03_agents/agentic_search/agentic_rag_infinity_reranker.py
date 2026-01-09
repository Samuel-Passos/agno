"""Este livro de receitas mostra como implementar RAG Agente usando Infinity Reranker.

Infinity é um servidor de inferência de alto desempenho para modelos de embeddings de texto, reranking e classificação.
Fornece capacidades de reranking rápidas e eficientes para aplicações RAG.

## Instruções de Configuração:

### 1. Instalar Dependências
Executar: `pip install agno anthropic infinity-client lancedb`

### 2. Configurar Servidor Infinity
Você tem várias opções para implantar Infinity:

#### Instalação Local
```bash
# Instalar infinity
pip install "infinity-emb[all]"

# Executar servidor infinity com modelo de reranking
infinity_emb v2 --model-id BAAI/bge-reranker-base --port 7997
```
Aguardar o motor iniciar.

# Para melhor desempenho, você pode usar modelos maiores:
# BAAI/bge-reranker-large
# BAAI/bge-reranker-v2-m3
# ms-marco-MiniLM-L-12-v2


### 3. Exportar Chaves de API
```bash
export ANTHROPIC_API_KEY="sua-chave-api-anthropic"
```

### 4. Executar o Exemplo
```bash
python cookbook/agent_concepts/agentic_search/agentic_rag_infinity_reranker.py
```

## Sobre Infinity Reranker:
- Fornece reranking rápido e local sem chamadas de API externas
- Suporta múltiplos modelos de reranking state-of-the-art
- Pode ser implantado em GPU para melhor desempenho
- Oferece capacidades de reranking tanto síncronas quanto assíncronas
- Mais opções de implantação: https://michaelfeil.eu/infinity/0.0.76/deploy/
"""

import asyncio

from agno.agent import Agent
from agno.knowledge.embedder.cohere import CohereEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reranker.infinity import InfinityReranker
from agno.models.anthropic import Claude
from agno.vectordb.lancedb import LanceDb, SearchType

knowledge = Knowledge(
    # Usar LanceDB como banco de dados vetorial, armazenar embeddings na tabela `agno_docs_infinity`
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="agno_docs_infinity",
        search_type=SearchType.hybrid,
        embedder=CohereEmbedder(id="embed-v4.0"),
        # Usar reranker Infinity para reranking local e rápido
        reranker=InfinityReranker(
            model="BAAI/bge-reranker-base",  # Você pode mudar isso para outros modelos
            host="localhost",
            port=7997,
            top_n=5,  # Retornar os 5 principais documentos rerankeados
        ),
    ),
)
asyncio.run(
    knowledge.add_contents_async(
        urls=[
            "https://docs.agno.com/basics/agents/overview.md",
            "https://docs.agno.com/basics/tools/overview.md",
            "https://docs.agno.com/basics/knowledge/overview.md",
        ]
    )
)

agent = Agent(
    model=Claude(id="claude-3-7-sonnet-latest"),
    # RAG Agente é habilitado por padrão quando `knowledge` é fornecido ao Agent.
    knowledge=knowledge,
    # search_knowledge=True dá ao Agent a capacidade de buscar sob demanda
    # search_knowledge é True por padrão
    search_knowledge=True,
    instructions=[
        "Incluir fontes em sua resposta.",
        "Sempre buscar seu conhecimento antes de responder a pergunta.",
        "Fornecer informações detalhadas e precisas com base nos documentos recuperados.",
    ],
    markdown=True,
)


def test_infinity_connection():
    """Testar se o servidor Infinity está em execução e acessível"""
    try:
        from infinity_client import Client

        _ = Client(base_url="http://localhost:7997")
        print("✅ Conectado com sucesso ao servidor Infinity em localhost:7997")
        return True
    except Exception as e:
        print(f"❌ Falha ao conectar ao servidor Infinity: {e}")
        print(
            "\nPor favor, certifique-se de que o servidor Infinity está em execução. Veja as instruções de configuração acima."
        )
        return False


if __name__ == "__main__":
    print("🚀 Exemplo de RAG Agente com Infinity Reranker")
    print("=" * 50)

    # Testar conexão Infinity primeiro
    if not test_infinity_connection():
        exit(1)

    print("\n🤖 Iniciando interação com agente...")
    print("=" * 50)

    # Perguntas de exemplo para testar as capacidades de reranking
    questions = [
        "O que são Agentes e como eles funcionam?",
        "Como uso ferramentas com agentes?",
        "Qual é a diferença entre conhecimento e ferramentas?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n🔍 Pergunta {i}: {question}")
        print("-" * 40)
        agent.print_response(question, stream=True)
        print("\n" + "=" * 50)

    print("\n🎉 Exemplo concluído!")
    print("\nO reranker Infinity ajudou a melhorar a relevância dos documentos recuperados")
    print("rerankeando-os com base na similaridade semântica às suas consultas.")
