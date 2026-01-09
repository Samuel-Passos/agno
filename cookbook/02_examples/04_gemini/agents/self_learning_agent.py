"""
Agente de Auto-Aprendizado
==========================
Aprendizado Contínuo GPU Poor: Aprendizado em nível de sistema sem fine-tuning.

O loop:
1. Buscar base de conhecimento por aprendizados relevantes
2. Coletar informações novas (busca, APIs)
3. Sintetizar resposta usando ambos
4. Identificar insight reutilizável
5. Salvar com aprovação do usuário

Construído com Agno + Gemini 3 Flash
"""

import json
from datetime import datetime, timezone

from agno.agent import Agent
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.text_reader import TextReader
from agno.models.google import Gemini
from agno.tools.parallel import ParallelTools
from agno.tools.yfinance import YFinanceTools
from agno.utils.log import logger
from agno.vectordb.pgvector import PgVector, SearchType
from db import db_url, gemini_agents_db

# ============================================================================
# Base de Conhecimento: armazena aprendizados bem-sucedidos
# ============================================================================
agent_knowledge = Knowledge(
    name="Agent Learnings",
    vector_db=PgVector(
        db_url=db_url,
        table_name="agent_learnings",
        search_type=SearchType.hybrid,
        embedder=GeminiEmbedder(id="gemini-embedding-001"),
    ),
    max_results=5,
    contents_db=gemini_agents_db,
)


# ============================================================================
# Ferramenta: Salvar Aprendizado
# ============================================================================
def save_learning(
    title: str,
    context: str,
    learning: str,
    confidence: str = "medium",
    type: str = "rule",
) -> str:
    """
    Salvar um aprendizado reutilizável de uma execução bem-sucedida.

    Args:
        title: Título descritivo curto (ex: "Tratamento de limite de taxa de API")
        context: Quando/por que este aprendizado se aplica (ex: "Ao chamar APIs externas...")
        learning: O insight reutilizável real (seja específico e acionável)
        confidence: low | medium | high
        type: rule | heuristic | source | process | constraint

    Returns:
        Mensagem de status indicando o que aconteceu
    """
    # Validar entradas
    if not title or not title.strip():
        return "Não é possível salvar: título é obrigatório"
    if not learning or not learning.strip():
        return "Não é possível salvar: conteúdo do aprendizado é obrigatório"
    if len(learning.strip()) < 20:
        return "Não é possível salvar: aprendizado é muito curto para ser útil. Seja mais específico."
    if confidence not in ("low", "medium", "high"):
        return f"Não é possível salvar: confiança deve ser low|medium|high, recebido '{confidence}'"
    if type not in ("rule", "heuristic", "source", "process", "constraint"):
        return f"Não é possível salvar: tipo deve ser rule|heuristic|source|process|constraint, recebido '{type}'"

    # Construir o payload do aprendizado
    payload = {
        "title": title.strip(),
        "context": context.strip() if context else "",
        "learning": learning.strip(),
        "confidence": confidence,
        "type": type,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    # Salvar na base de conhecimento
    try:
        agent_knowledge.add_content(
            name=payload["title"],
            text_content=json.dumps(payload, ensure_ascii=False),
            reader=TextReader(),
            skip_if_exists=True,
        )
    except Exception as e:
        logger.error(f"[Learning] Falha ao salvar: {e}")
        return f"Falha ao salvar aprendizado: {e}"

    logger.info(f"[Learning] Salvo: {payload['title']}")
    return f"Aprendizado salvo: '{payload['title']}'"


# ============================================================================
# Instruções
# ============================================================================
instructions = """\
Você é um Agente de Auto-Aprendizado que melhora com o tempo capturando e reutilizando padrões bem-sucedidos.

Você constrói memória institucional: insights bem-sucedidos são salvos em uma base de conhecimento e recuperados em execuções futuras. O modelo permanece fixo, mas o sistema fica mais inteligente.

## Ferramentas

| Ferramenta | Usar Para |
|------------|-----------|
| search_knowledge | Recuperar aprendizados anteriores relevantes |
| parallel_search | Busca web, informações atuais |
| yfinance | Dados de mercado, financeiros, informações de empresas |
| save_learning | Armazenar um insight reutilizável (requer aprovação do usuário) |

## Fluxo de Trabalho

Para cada solicitação:

1. BUSCAR CONHECIMENTO PRIMEIRO — Sempre chamar `search_knowledge` antes de qualquer coisa. Extrair conceitos-chave da consulta do usuário e buscar aprendizados relevantes. Se nada relevante for encontrado, prosseguir sem contexto anterior.
2. PESQUISAR — Usar `parallel_search` ou `yfinance` para coletar informações novas conforme necessário.
3. SINTETIZAR — Combinar aprendizados anteriores (se houver) com novas informações. Ao aplicar um aprendizado anterior, referenciá-lo naturalmente: "Com base em um padrão anterior..." ou "Um aprendizado anterior sugere..."
4. REFLETIR — Após responder, considerar: esta tarefa revelou um insight reutilizável? A maioria das consultas não produzirá um aprendizado. Apenas sinalizar descobertas genuínas.
5. PROPOR (se aplicável) — Se você identificou algo que vale a pena salvar, propor no final de sua resposta. Nunca chamar save_learning sem aprovação explícita do usuário.

## O Que Faz um Bom Aprendizado

Um aprendizado vale a pena salvar se for:
- Específico: "Ao comparar ETFs, verificar taxa de despesa E erro de rastreamento" não "Olhar métricas de ETF"
- Acionável: Pode ser aplicado diretamente em consultas futuras semelhantes
- Generalizável: Útil além desta questão específica

Não salvar: fatos brutos, respostas pontuais, resumos, especulação ou qualquer coisa improvável de recorrer.

A maioria das tarefas não produzirá um aprendizado. Isso é esperado.

## Propondo um Aprendizado

Quando você tiver um insight genuíno que vale a pena salvar, terminar sua resposta com:

---
Aprendizado Proposto

Título: [título conciso]
Tipo: rule | heuristic | source | process | constraint
Contexto: [quando aplicar isso]
Aprendizado: [o insight — específico e acionável]

Salvar isso? (sim/não)
---

Se o usuário recusar, reconhecer e seguir em frente. Não repropor o mesmo aprendizado.
"""


# ============================================================================
# Create the Agent
# ============================================================================
self_learning_agent = Agent(
    name="Self-Learning Agent",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    db=gemini_agents_db,
    knowledge=agent_knowledge,
    tools=[
        ParallelTools(),
        YFinanceTools(),
        save_learning,
    ],
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


# ============================================================================
# CLI
# ============================================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        self_learning_agent.print_response(query, stream=True)
    else:
        print("=" * 60)
        print("🧠 Agente de Auto-Aprendizado")
        print("   Aprendizado Contínuo GPU Poor com Gemini 3 Flash")
        print("=" * 60)
        print("\nDigite 'quit' para sair.\n")

        while True:
            try:
                user_input = input("Você: ").strip()
                if user_input.lower() in ("quit", "exit", "q"):
                    print("\n👋 Até logo!")
                    break
                if not user_input:
                    continue

                print()
                self_learning_agent.print_response(user_input, stream=True)
                print()

            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
