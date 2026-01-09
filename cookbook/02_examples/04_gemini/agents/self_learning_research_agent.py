import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from agno.agent import Agent
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.text_reader import TextReader
from agno.models.google import Gemini
from agno.tools.parallel import ParallelTools
from agno.utils.log import logger
from agno.vectordb.pgvector import PgVector, SearchType
from db import db_url, gemini_agents_db

# =============================================================================
# Base de conhecimento para armazenar snapshots de pesquisa históricos
# =============================================================================
research_knowledge = Knowledge(
    name="Research Snapshots",
    vector_db=PgVector(
        db_url=db_url,
        table_name="research_snapshots",
        search_type=SearchType.hybrid,
        embedder=GeminiEmbedder(id="gemini-embedding-001"),
    ),
    max_results=3,  # buscar alguns candidatos; agente seleciona o mais recente por created_at
    contents_db=gemini_agents_db,
)


# =============================================================================
# Ferramenta: Salvar um snapshot de pesquisa (aprovação explícita do usuário necessária)
# =============================================================================
def save_research_snapshot(
    name: str,
    question: str,
    report_summary: str,
    consensus_summary: str,
    claims: List[Dict[str, Any]],
    sources: List[Dict[str, str]],
    notes: Optional[str] = None,
) -> str:
    """Salvar um snapshot de pesquisa validado na base de conhecimento.

    Args:
        name: O nome do snapshot.
        question: A pergunta original feita pelo usuário.
        report_summary: Um resumo conciso desta execução (máx 8 marcadores ou ~120 palavras).
        consensus_summary: Resumo de consenso de 1-2 frases.
        claims: Uma lista de afirmações apoiadas pela evidência.
        sources: Uma lista de fontes usadas para apoiar as afirmações.
        notes: Considerações opcionais de ressalvas, suposições ou qualidade de dados.

    Returns:
        str: Mensagem de status.
    """

    if research_knowledge is None:
        return "Conhecimento não disponível"

    payload = {
        "name": name.strip(),
        "question": question.strip(),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "report_summary": report_summary.strip(),
        "consensus_summary": consensus_summary.strip(),
        "claims": claims,
        "sources": sources,
        "notes": notes,
    }

    logger.info("Salvando snapshot de pesquisa")

    research_knowledge.add_content(
        name=payload["name"],
        text_content=json.dumps(payload, ensure_ascii=False),
        reader=TextReader(),
        skip_if_exists=False,  # snapshots são históricos
    )

    return "Snapshot de pesquisa salvo na base de conhecimento"


# =============================================================================
# Instruções
# =============================================================================
instructions = """\
Você é um agente de pesquisa de auto-aprendizado com acesso a busca web e uma base de conhecimento
contendo snapshots de pesquisa anteriores.

Seu trabalho:
- Responder a pergunta do usuário usando busca web (via parallel_search).
- Resumir o consenso atual da internet como afirmações estruturadas.
- Buscar sua base de conhecimento pelo snapshot mais recente de uma pergunta semelhante.
- Comparar as afirmações atuais ao snapshot anterior e explicar o que mudou e por quê.
- Perguntar ao usuário se ele quer salvar o novo snapshot na base de conhecimento.

Você DEVE seguir este fluxo:
1) Usar a ferramenta `parallel_search` para coletar informações atuais.
   - Emitir MÚLTIPLAS consultas de busca em paralelo (fan-out) e depois agregar resultados.
   - Cobrir pelo menos:
     - Fontes primárias/oficiais (docs, páginas de fornecedores, órgãos de padrões)
     - Análise independente (blogs respeitáveis da indústria, benchmarks, laboratórios de pesquisa)
2) Usar `search_knowledge` para recuperar até 3 snapshots semelhantes (se houver).
3) Dos snapshots recuperados, selecionar o com `created_at` mais novo como "consenso anterior".
4) Diferenciar as afirmações atuais das afirmações anteriores.
5) Apresentar resultados usando o formato abaixo.
6) Perguntar ao usuário se ele quer salvar o novo snapshot na base de conhecimento.

Regras de consenso:
- Uma afirmação deve ser apoiada por pelo menos duas fontes independentes, a menos que seja uma fonte primária/oficial.
- Se as fontes discordarem, marcar a afirmação como disputada e reduzir a confiança.

Formato de resposta (deve seguir exatamente):

## Resposta Rápida
(2-4 frases)

## Resumo da Pesquisa
(Seções estruturadas com marcadores)

## Consenso Atual (Afirmações)
Fornecer 4-10 afirmações. Cada afirmação deve incluir:
- claim_id: id estável (gerar um slug curto)
- claim: declaração curta
- confidence: Low | Medium | High
- source_urls: 1-3 URLs

## O Que Mudou Desde a Última Vez
- Se um snapshot anterior existir:
  - Novas ou fortalecidas afirmações
  - Enfraquecidas ou disputadas afirmações
  - Afirmações removidas
  - Para cada mudança, explicar brevemente por quê e citar fontes
- Se nenhum snapshot anterior existir:
  - Dizer: "Nenhum snapshot anterior encontrado. Este é o primeiro consenso registrado."

## Fontes
- Desduplicar URLs
- Preferir URLs canônicas
- Máx 12 fontes
(URLs clicáveis)

Após a resposta, adicionar:

## Salvar Snapshot?
"Quer que eu salve este snapshot na base de conhecimento para comparações futuras?"

Regras:
- Separar claramente fatos de interpretação.
- Notar incerteza ou informações desatualizadas explicitamente.
- Perguntar ao usuário se ele quer salvar o novo snapshot na base de conhecimento e então chamar a ferramenta `save_research_snapshot` se ele disser sim.
"""


# =============================================================================
# Create the agent
# =============================================================================
self_learning_research_agent = Agent(
    name="Self Learning Research Agent",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    db=gemini_agents_db,
    knowledge=research_knowledge,
    tools=[ParallelTools(), save_research_snapshot],
    # Habilitar o agente para lembrar informações e preferências do usuário
    enable_agentic_memory=True,
    # Habilitar o agente para buscar a base de conhecimento (ex: snapshots de pesquisa anteriores)
    search_knowledge=True,
    # Adicionar a data e hora atuais ao contexto
    add_datetime_to_context=True,
    # Adicionar o histórico das execuções do agente ao contexto
    add_history_to_context=True,
    # Número de execuções históricas para incluir no contexto
    num_history_runs=5,
    # Dar ao agente uma ferramenta para ler histórico de chat além das últimas 5 mensagens
    read_chat_history=True,
    markdown=True,
)


if __name__ == "__main__":
    self_learning_research_agent.print_response(
        "What is the current consensus on using AI agents in enterprise production systems?",
        stream=True,
    )
