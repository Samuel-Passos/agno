"""🤖 Agentic RAG - Seu Agente de Conhecimento de IA!
Este exemplo avançado mostra como construir um sistema RAG (Retrieval Augmented Generation) sofisticado que
aproveita busca vetorial e Modelos de Linguagem para fornecer insights profundos de qualquer base de conhecimento.

O Agente pode:
- Processar e entender documentos de múltiplas fontes (PDFs, sites, arquivos de texto)
- Construir uma base de conhecimento pesquisável usando embeddings vetoriais
- Manter contexto de conversa e memória através de sessões
- Fornecer citações e fontes relevantes para suas respostas
- Gerar resumos e extrair insights-chave
- Responder perguntas de acompanhamento e esclarecimentos

Exemplos de Consultas para Tentar:
- "Quais são os pontos-chave deste documento?"
- "Você pode resumir os principais argumentos e evidências de apoio?"
- "Quais são as estatísticas e descobertas importantes?"
- "Como isso se relaciona com [tópico X]?"
- "Quais são as limitações ou lacunas nesta análise?"
- "Você pode explicar [conceito X] em mais detalhes?"
- "Quais outras fontes apoiam ou contradizem essas afirmações?"

O Agente usa:
- Busca de similaridade vetorial para recuperação de documentos relevantes
- Memória de conversa para respostas contextuais
- Rastreamento de citações para atribuição de fontes
- Atualizações dinâmicas da base de conhecimento

Ver o README para instruções sobre como executar a aplicação.
"""

from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.utils.streamlit import get_model_from_id
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"


def get_agentic_rag_agent(
    model_id: str = "openai:gpt-4o",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Agent:
    """Obter um Agente Agentic RAG com Memória"""
    contents_db = PostgresDb(
        db_url=db_url,
        knowledge_table="agentic_rag_knowledge_contents",
        db_schema="ai",
    )

    knowledge_base = Knowledge(
        name="Agentic RAG Knowledge Base",
        description="Knowledge base for agentic RAG application",
        vector_db=PgVector(
            db_url=db_url,
            table_name="agentic_rag_documents",
            schema="ai",
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
        contents_db=contents_db,
        max_results=3,  # Only return top 3 most relevant documents
    )

    db = PostgresDb(
        db_url=db_url,
        session_table="sessions",
        db_schema="ai",
    )

    agent = Agent(
        name="Agentic RAG Agent",
        model=get_model_from_id(model_id),
        id="agentic-rag-agent",
        user_id=user_id,
        db=db,
        enable_user_memories=True,
        knowledge=knowledge_base,
        add_history_to_context=True,
        num_history_runs=5,
        session_id=session_id,
        tools=[DuckDuckGoTools()],
        instructions=dedent("""
            1. Busca na Base de Conhecimento:
               - SEMPRE começar buscando na base de conhecimento usando a ferramenta search_knowledge_base
               - Analisar TODOS os documentos retornados completamente antes de responder
               - Se múltiplos documentos forem retornados, sintetizar as informações de forma coerente
            2. Busca Externa:
               - Se a busca na base de conhecimento produzir resultados insuficientes, usar duckduckgo_search
               - Focar em fontes respeitáveis e informações recentes
               - Fazer referência cruzada de informações de múltiplas fontes quando possível
            3. Gerenciamento de Contexto:
               - Usar a ferramenta get_chat_history para manter continuidade da conversa
               - Referenciar interações anteriores quando relevante
               - Manter controle das preferências do usuário e esclarecimentos anteriores
            4. Qualidade da Resposta:
               - Fornecer citações e fontes específicas para afirmações
               - Estruturar respostas com seções claras e marcadores quando apropriado
               - Incluir citações relevantes dos materiais de origem
               - Evitar frases evasivas como 'com base no meu conhecimento' ou 'dependendo das informações'
            5. Interação com o Usuário:
               - Pedir esclarecimentos se a consulta for ambígua
               - Dividir perguntas complexas em partes gerenciáveis
               - Sugerir proativamente tópicos relacionados ou perguntas de acompanhamento
            6. Tratamento de Erros:
               - Se nenhuma informação relevante for encontrada, declarar isso claramente
               - Sugerir abordagens alternativas ou perguntas
               - Ser transparente sobre limitações nas informações disponíveis
        """),
        markdown=True,
        debug_mode=True,
    )

    return agent
