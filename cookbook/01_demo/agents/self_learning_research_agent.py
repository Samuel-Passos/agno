import json
from datetime import datetime, timezone
from typing import Optional

from agno.agent import Agent
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.text_reader import TextReader
from agno.models.openai import OpenAIResponses
from agno.tools.parallel import ParallelTools
from agno.utils.log import logger
from agno.vectordb.pgvector import PgVector, SearchType
from db import db_url, demo_db

# =============================================================================
# Base de conhecimento para armazenar snapshots de pesquisa históricos
# =============================================================================
research_snapshots = Knowledge(
    name="Research Snapshots",
    vector_db=PgVector(
        db_url=db_url,
        table_name="research_snapshots",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    max_results=3,  # buscar alguns candidatos; agente seleciona o mais recente por created_at
    contents_db=demo_db,
)


# =============================================================================
# Ferramenta: Salvar um snapshot de pesquisa (aprovação explícita do usuário necessária)
# =============================================================================
def save_research_snapshot(
    name: str,
    question: str,
    report_summary: str,
    consensus_summary: str,
    claims: str,
    sources: str,
    notes: Optional[str] = None,
) -> str:
    """Salva um snapshot de pesquisa validado na base de conhecimento.
    Este snapshot registra o consenso atual em um ponto no tempo para que execuções futuras possam comparar o que mudou e por quê.

    Args:
        name:
            Nome de snapshot curto e legível por humanos.
            Exemplo: "Agentes de IA em produção empresarial (Dez 2025)"

        question:
            A pergunta original do usuário exatamente como foi feita.

        report_summary:
            Um resumo conciso desta execução.
            - Máximo 8 pontos OU ~120 palavras
            - Apenas texto simples (sem markdown)

        consensus_summary:
            Um resumo de 1-2 frases descrevendo o consenso geral.

        claims:
            Uma STRING JSON representando uma LISTA de objetos de claim.

            Schema JSON obrigatório:
            [
              {
                "claim_id": "stable.short.slug",
                "claim": "Declaração factual curta",
                "confidence": "Low | Medium | High",
                "source_urls": ["https://example.com", "..."]
              }
            ]

            Regras:
            - Deve ser JSON válido
            - Deve ser uma lista, não um dict
            - Cada claim deve incluir todos os campos obrigatórios
            - source_urls deve ser uma lista de 1–3 URLs

        sources:
            Uma STRING JSON representando uma LISTA de objetos de source.

            Schema JSON obrigatório:
            [
              {
                "title": "Título da fonte",
                "url": "https://example.com"
              }
            ]

            Regras:
            - Deve ser JSON válido
            - Desduplicar URLs
            - Preferir URLs canônicas (sem parâmetros de rastreamento)

        notes:
            Notas opcionais em texto simples para ressalvas, incerteza ou problemas de qualidade de dados.
            Usar null se não necessário.

    Returns:
        Uma mensagem de status curta indicando se o snapshot foi salvo com sucesso.
    """

    if research_snapshots is None:
        return "Conhecimento não disponível"

    payload = {
        "name": name.strip(),
        "question": question.strip(),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "report_summary": report_summary.strip(),
        "consensus_summary": consensus_summary.strip(),
        "claims": claims.strip(),
        "sources": sources.strip(),
        "notes": notes.strip() if notes else None,
    }

    logger.info(f"Salvando snapshot de pesquisa: {payload['name']}")
    research_snapshots.add_content(
        name=payload["name"],
        text_content=json.dumps(payload, ensure_ascii=False),
        reader=TextReader(),
        skip_if_exists=True,
    )

    return "Snapshot de pesquisa salvo na base de conhecimento"


# =============================================================================
# Mensagem do sistema
# =============================================================================
system_message = """\
Você é um agente de pesquisa de autoaprendizado chamado Atlas.

Você tem acesso a:
- Busca web via ferramentas (usar `parallel_search`)
- Uma base de conhecimento contendo snapshots de pesquisa anteriores
- Uma ferramenta para salvar snapshots de pesquisa validados (`save_research_snapshot`)

Seu objetivo:
Produzir uma resposta de pesquisa fundamentada, resumir o consenso atual como claims estruturados,
compará-lo ao snapshot anterior mais recente, explicar o que mudou e por quê, e opcionalmente
persistir um novo snapshot com aprovação explícita do usuário.

+--------------------
WORKFLOW OBRIGATÓRIO
+--------------------

Você DEVE seguir esta sequência exatamente:

1) Pesquisa (web)
   - Usar a ferramenta `parallel_search`.
   - Emitir MÚLTIPLAS consultas de busca em paralelo.
   - Agregar e desduplicar resultados.
   - Cobrir pelo menos:
     - Fontes primárias / oficiais (docs de fornecedores, órgãos de padrões, anúncios)
     - Análise independente (blogs respeitáveis, benchmarks, laboratórios de pesquisa)

2) Recuperar consenso anterior
   - Usar `search_knowledge` para recuperar até 3 snapshots similares.
   - Se múltiplos snapshots forem retornados, selecionar o com `created_at` mais novo.
   - Tratar isso como o "consenso anterior".

3) Sintetizar consenso atual
   - Derivar um pequeno conjunto de claims claros e defensáveis das fontes atuais.
   - Cada claim deve ser explícito, apoiado por evidências e classificado por confiança.

4) Diferença
   - Comparar claims atuais contra o snapshot anterior.
   - Identificar:
     - Claims novos ou fortalecidos
     - Claims enfraquecidos ou disputados
     - Claims removidos
   - Para cada mudança, explicar brevemente POR QUE a mudança ocorreu e citar fontes.

5) Responder
   - Apresentar resultados usando o formato de resposta exato abaixo.

6) Salvar (humano-no-loop)
   - Perguntar ao usuário se deseja salvar o novo snapshot.
   - APENAS chamar `save_research_snapshot` se o usuário concordar explicitamente.
   - Ao chamar a ferramenta, seguir sua docstring EXATAMENTE.

+--------------------
REGRAS DE CONSENSO
+--------------------

- Um claim requer suporte de pelo menos DUAS fontes independentes,
  a menos que seja baseado em uma fonte primária ou oficial.
- Se fontes credíveis discordarem, marcar o claim como disputado
  e reduzir a confiança correspondentemente.
- NÃO especular além da evidência.

+--------------------
FORMATO DE RESPOSTA (RIGOROSO)
+--------------------

## Resposta Rápida
2-4 frases resumindo o consenso geral.

## Resumo da Pesquisa
Seções estruturadas com pontos resumindo descobertas-chave.

## Consenso Atual (Claims)
Resumir o consenso atual usando 3-5 claims.
Cada claim deve ser escrito claramente e precisamente.

## O que Mudou Desde a Última Vez
- Se um snapshot anterior existir:
  - Claims novos ou fortalecidos
  - Claims enfraquecidos ou disputados
  - Claims removidos
  - Explicação breve de por que cada mudança ocorreu, com citações
- Se nenhum snapshot anterior existir:
  - Declarar: "Nenhum snapshot anterior encontrado. Este é o primeiro consenso registrado."

## Fontes
- Desduplicadas
- Apenas URLs canônicas
- Máximo 5 fontes
- Renderizar como links markdown clicáveis

Após a resposta, anexar:

## Salvar Snapshot?
Perguntar exatamente:
"Quer que eu salve este snapshot na base de conhecimento para comparações futuras?"

+--------------------
REGRAS GLOBAIS
+--------------------

- Separar claramente fatos de interpretação.
- Notar explicitamente incerteza, lacunas ou informações desatualizadas.
- NÃO revelar raciocínio interno ou chain-of-thought.
- NÃO chamar `save_research_snapshot` a menos que o usuário diga explicitamente sim.
- Ao chamar `save_research_snapshot`, seguir sua docstring precisamente:
   - Todos os campos estruturados devem ser passados como STRINGS JSON.
"""

# =============================================================================
# Criar o agente
# =============================================================================
self_learning_research_agent = Agent(
    name="Self Learning Research Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    system_message=system_message,
    db=demo_db,
    knowledge=research_snapshots,
    tools=[ParallelTools(), save_research_snapshot],
    # Habilitar o agente para lembrar informações e preferências do usuário
    enable_agentic_memory=True,
    # Habilitar o agente para pesquisar a base de conhecimento (ex: snapshots de pesquisa anteriores)
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
