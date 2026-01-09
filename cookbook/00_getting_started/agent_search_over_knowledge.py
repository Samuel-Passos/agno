"""
Busca Agente sobre Conhecimento - Agente com Base de Conhecimento
==================================================================
Este exemplo mostra como dar a um agente uma base de conhecimento pesquisável.
O agente pode pesquisar em documentos (PDFs, texto, URLs) para responder perguntas.

Conceitos-chave:
- Conhecimento: Uma coleção pesquisável de documentos (PDFs, texto, URLs)
- Busca agente: O agente decide quando pesquisar a base de conhecimento
- Busca híbrida: Combina similaridade semântica com correspondência de palavras-chave.

Exemplos de prompts para testar:
- "O que é Agno?"
- "O que é o AgentOS?"
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.google import Gemini
from agno.vectordb.chroma import ChromaDb
from agno.vectordb.search import SearchType

# ============================================================================
# Configuração de Armazenamento
# ============================================================================
agent_db = SqliteDb(db_file="tmp/agents.db")

# ============================================================================
# Configuração de Conhecimento
# ============================================================================
knowledge = Knowledge(
    name="Agno Documentation",
    vector_db=ChromaDb(
        name="agno_docs",
        collection="agno_docs",
        path="tmp/chromadb",
        persistent_client=True,
        # Habilita busca híbrida - combina similaridade vetorial com correspondência de palavras-chave usando RRF
        search_type=SearchType.hybrid,
        # Constante RRF (Reciprocal Rank Fusion) - controla a suavidade do ranqueamento.
        # Valores maiores (ex: 60) dão mais peso a resultados de menor classificação,
        # Valores menores tornam os principais resultados mais dominantes. Padrão é 60 (conforme artigo original RRF).
        hybrid_rrf_k=60,
        embedder=GeminiEmbedder(id="gemini-embedding-001"),
    ),
    # Retorna 5 resultados na consulta
    max_results=5,
    # Armazena metadados sobre o conteúdo no banco de dados do agente, table_name="agno_knowledge"
    contents_db=agent_db,
)

# ============================================================================
# Instruções do Agente
# ============================================================================
instructions = """\
Você é um especialista no framework Agno e na construção de agentes de IA.

## Fluxo de Trabalho

1. Pesquisar
   - Para perguntas sobre Agno, sempre pesquise sua base de conhecimento primeiro
   - Extraia conceitos-chave da consulta para pesquisar efetivamente

2. Sintetizar
   - Combine informações de múltiplos resultados de busca
   - Priorize documentação oficial sobre conhecimento geral

3. Apresentar
   - Comece com uma resposta direta
   - Inclua exemplos de código quando útil
   - Mantenha prático e acionável

## Regras

- Sempre pesquise o conhecimento antes de responder perguntas sobre Agno
- Se a resposta não estiver na base de conhecimento, diga isso
- Inclua trechos de código para perguntas de implementação
- Seja conciso — desenvolvedores querem respostas, não ensaios\
"""

# ============================================================================
# Criar o Agente
# ============================================================================
agent_with_knowledge = Agent(
    name="Agent with Knowledge",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    knowledge=knowledge,
    search_knowledge=True,
    db=agent_db,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

# ============================================================================
# Carregar Conhecimento e Executar o Agente
# ============================================================================
if __name__ == "__main__":
    # Carrega a introdução da documentação Agno na base de conhecimento
    # Estamos carregando apenas 1 arquivo para manter este exemplo simples.
    knowledge.add_content(
        name="Agno Introduction", url="https://docs.agno.com/introduction.md"
    )

    agent_with_knowledge.print_response(
        "O que é Agno?",
        stream=True,
    )

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Carregue seu próprio conhecimento:

1. De uma URL
   knowledge.add_content(url="https://example.com/docs.pdf")

2. De um arquivo local
   knowledge.add_content(path="path/to/document.pdf")

3. De texto diretamente
   knowledge.add_content(text_content="Seu conteúdo aqui...")

A busca híbrida combina:
- Busca semântica: Encontra conteúdo conceitualmente similar
- Busca por palavras-chave: Encontra correspondências exatas de termos
- Resultados fundidos usando Reciprocal Rank Fusion (RRF)

O agente pesquisa automaticamente quando relevante (busca agente).
"""
