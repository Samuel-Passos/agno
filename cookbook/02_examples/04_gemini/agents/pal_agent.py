"""
PaL — Agente Planejar e Aprender
=================================
Um agente de planejamento e execução disciplinado que:
- Cria planos estruturados com critérios de sucesso
- Executa passos sequencialmente com verificação
- Aprende de execuções bem-sucedidas
- Persiste estado através de sessões

> Planejar. Executar. Aprender. Repetir.
"""

import json
from datetime import datetime, timezone
from typing import List, Optional

from agno.agent import Agent
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.text_reader import TextReader
from agno.models.google import Gemini
from agno.run import RunContext
from agno.tools.parallel import ParallelTools
from agno.tools.yfinance import YFinanceTools
from agno.utils.log import logger
from agno.vectordb.pgvector import PgVector, SearchType
from db import db_url, gemini_agents_db

# ============================================================================
# Base de Conhecimento: Armazena aprendizados de execução
# ============================================================================
execution_knowledge = Knowledge(
    name="PaL Execution Learnings",
    vector_db=PgVector(
        db_url=db_url,
        table_name="pal_execution_learnings",
        search_type=SearchType.hybrid,
        embedder=GeminiEmbedder(id="gemini-embedding-001"),
    ),
    max_results=5,
    contents_db=gemini_agents_db,
)


# ============================================================================
# Ferramentas de Planejamento
# ============================================================================
def create_plan(
    run_context: RunContext,
    objective: str,
    steps: List[dict],
    context: Optional[str] = None,
) -> str:
    """
    Criar um plano de execução com passos ordenados e critérios de sucesso.

    Args:
        objective: O objetivo geral a alcançar
        steps: Lista de objetos de passo, cada um com:
               - description (str): O que fazer
               - success_criteria (str): Como verificar conclusão
        context: Informações de fundo opcionais

    Exemplo:
        create_plan(
            objective="Análise competitiva de armazenamento em nuvem",
            steps=[
                {"description": "Identificar top 3 provedores", "success_criteria": "Lista com dados de participação de mercado"},
                {"description": "Comparar níveis de preços", "success_criteria": "Tabela de preços para todos os níveis"},
                {"description": "Analisar recursos", "success_criteria": "Matriz de recursos com 10+ atributos"},
                {"description": "Escrever resumo", "success_criteria": "Resumo executivo com menos de 500 palavras"},
            ]
        )
    """
    state = run_context.session_state

    # Guarda: Não sobrescrever plano ativo
    if state.get("plan") and state.get("status") == "in_progress":
        return (
            "⚠️ Um plano já está em progresso.\n"
            "Opções:\n"
            "  - Completar o plano atual\n"
            "  - Chamar reset_plan(confirm=True) para começar do zero"
        )

    # Validar e construir estrutura do plano
    plan_items = []
    for i, step in enumerate(steps, 1):
        if not isinstance(step, dict) or "description" not in step:
            return f"❌ Formato de passo inválido na posição {i}. Precisa {{'description': '...', 'success_criteria': '...'}}"

        plan_items.append(
            {
                "id": i,
                "description": step["description"].strip(),
                "success_criteria": step.get(
                    "success_criteria", "Tarefa concluída com sucesso"
                ).strip(),
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "output": None,
            }
        )

    # Inicializar estado
    state["objective"] = objective.strip()
    state["context"] = context.strip() if context else None
    state["plan"] = plan_items
    state["plan_length"] = len(plan_items)
    state["current_step"] = 1
    state["status"] = "in_progress"
    state["created_at"] = datetime.now(timezone.utc).isoformat()
    state["completed_at"] = None

    # Formatar resposta
    steps_display = "\n".join(
        [
            f"  {s['id']}. {s['description']}\n     ✓ Concluído quando: {s['success_criteria']}"
            for s in plan_items
        ]
    )

    logger.info(f"[PaL] Plano criado: {objective} ({len(plan_items)} passos)")

    return (
        f"✅ Plano criado!\n\n"
        f"🎯 Objetivo: {objective}\n"
        f"{'📝 Contexto: ' + context + chr(10) if context else ''}\n"
        f"Passos:\n{steps_display}\n\n"
        f"→ Pronto para começar com Passo 1"
    )


def complete_step(run_context: RunContext, output: str) -> str:
    """
    Marcar o passo atual como completo com saída de verificação.

    A saída deve demonstrar que os critérios de sucesso foram atendidos.
    O agente avançará automaticamente para o próximo passo.

    Args:
        output: Evidências/resultados que satisfazem os critérios de sucesso do passo
    """
    state = run_context.session_state
    plan = state.get("plan", [])
    current = state.get("current_step", 1)

    if not plan:
        return "❌ Nenhum plano existe. Criar um primeiro com create_plan()."

    if state.get("status") == "complete":
        return "✅ Plano já está completo. Usar reset_plan(confirm=True) para começar um novo."

    # Obter passo atual
    step = plan[current - 1]

    if step["status"] == "complete":
        return f"❌ Passo {current} já está completo."

    # Marcar como completo
    now = datetime.now(timezone.utc).isoformat()
    step["status"] = "complete"
    step["completed_at"] = now
    step["output"] = output.strip()

    logger.info(f"[PaL] Passo {current} concluído: {step['description'][:50]}...")

    # Verificar se este foi o último passo
    if current >= len(plan):
        state["status"] = "complete"
        state["completed_at"] = now

        # Calcular duração
        created = datetime.fromisoformat(state["created_at"].replace("Z", "+00:00"))
        completed = datetime.fromisoformat(now.replace("Z", "+00:00"))
        duration = completed - created

        return (
            f"✅ Passo {current} completo!\n\n"
            f"🎉 **Plano Finalizado!**\n"
            f"Todos os {len(plan)} passos concluídos com sucesso.\n"
            f"Duração: {duration}\n\n"
            f"💡 **Oportunidade de aprendizado**: Há um insight reutilizável desta execução?\n"
            f"Se sim, proponha e eu salvarei com `save_learning()` para tarefas futuras."
        )

    # Avançar para o próximo passo
    state["current_step"] = current + 1
    next_step = plan[current]

    return (
        f"✅ Passo {current} completo!\n\n"
        f"→ **Passo {current + 1}**: {next_step['description']}\n"
        f"  Critérios de sucesso: {next_step['success_criteria']}"
    )


def update_plan(
    run_context: RunContext,
    action: str,
    step_id: Optional[int] = None,
    new_step: Optional[dict] = None,
    reason: Optional[str] = None,
) -> str:
    """
    Modificar o plano atual dinamicamente.

    Args:
        action: O tipo de modificação
                - "add": Anexar um novo passo ao final
                - "insert": Inserir um passo após step_id
                - "remove": Remover um passo futuro
                - "revisit": Voltar a um passo anterior
        step_id: ID do passo alvo (necessário para insert/remove/revisit)
        new_step: Definição de passo para add/insert {"description": "...", "success_criteria": "..."}
        reason: Explicação para a mudança (necessário para revisit)
    """
    state = run_context.session_state
    plan = state.get("plan", [])
    current = state.get("current_step", 1)

    if not plan:
        return "❌ Nenhum plano existe. Criar um primeiro."

    # ADD: Anexar novo passo ao final
    if action == "add":
        if not new_step or "description" not in new_step:
            return (
                "❌ Fornecer new_step={'description': '...', 'success_criteria': '...'}"
            )

        new_item = {
            "id": len(plan) + 1,
            "description": new_step["description"].strip(),
            "success_criteria": new_step.get(
                "success_criteria", "Tarefa concluída"
            ).strip(),
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "output": None,
        }
        plan.append(new_item)
        state["plan_length"] = len(plan)

        logger.info(f"[PaL] Passo adicionado: {new_item['description'][:50]}...")
        return f"✅ Passo {new_item['id']} adicionado: {new_item['description']}"

    # INSERT: Adicionar passo após uma posição específica
    elif action == "insert":
        if not step_id or not new_step:
            return "❌ Fornecer step_id (inserir após) e new_step"
        if step_id < current:
            return f"❌ Não é possível inserir antes do passo atual {current}"

        new_item = {
            "id": step_id + 1,
            "description": new_step["description"].strip(),
            "success_criteria": new_step.get(
                "success_criteria", "Tarefa concluída"
            ).strip(),
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "output": None,
        }

        # Inserir e renumerar
        plan.insert(step_id, new_item)
        for i, s in enumerate(plan, 1):
            s["id"] = i
        state["plan_length"] = len(plan)

        logger.info(
            f"[PaL] Passo inserido após {step_id}: {new_item['description'][:50]}..."
        )
        return f"✅ Novo Passo {step_id + 1} inserido: {new_item['description']}"

    # REMOVE: Excluir um passo futuro
    elif action == "remove":
        if not step_id:
            return "❌ Fornecer step_id para remover"
        if step_id <= current:
            return f"❌ Não é possível remover passo {step_id} — já é atual ou concluído"

        removed = next((s for s in plan if s["id"] == step_id), None)
        if not removed:
            return f"❌ Passo {step_id} não encontrado"

        state["plan"] = [s for s in plan if s["id"] != step_id]
        # Renumerar passos restantes
        for i, s in enumerate(state["plan"], 1):
            s["id"] = i
        state["plan_length"] = len(state["plan"])

        logger.info(f"[PaL] Passo removido: {removed['description'][:50]}...")
        return f"✅ Removido: {removed['description']}\nPlano agora tem {state['plan_length']} passos."

    # REVISIT: Voltar a um passo anterior
    elif action == "revisit":
        if not step_id:
            return "❌ Fornecer step_id para revisitar"
        if not reason:
            return "❌ Fornecer razão para revisitar"
        if step_id > current:
            return f"❌ Passo {step_id} ainda não foi alcançado"

        # Redefinir este passo e todos os subsequentes
        for s in plan:
            if s["id"] >= step_id:
                s["status"] = "pending"
                s["started_at"] = None
                s["completed_at"] = None
                if s["id"] == step_id:
                    s["output"] = f"[Revisitando: {reason}]"
                else:
                    s["output"] = None

        state["current_step"] = step_id
        state["status"] = "in_progress"

        logger.info(f"[PaL] Revisitando passo {step_id}: {reason}")
        return (
            f"🔄 Revisitando Passo {step_id}\n"
            f"Razão: {reason}\n"
            f"Progresso redefinido para este passo."
        )

    return f"❌ Ação desconhecida: {action}. Usar 'add', 'insert', 'remove' ou 'revisit'."


def block_step(
    run_context: RunContext, blocker: str, suggestion: Optional[str] = None
) -> str:
    """
    Marcar o passo atual como bloqueado com uma explicação.

    Args:
        blocker: O que está impedindo o progresso
        suggestion: Resolução sugerida opcional
    """
    state = run_context.session_state
    plan = state.get("plan", [])
    current = state.get("current_step", 1)

    if not plan:
        return "❌ Nenhum plano existe."

    step = plan[current - 1]
    step["status"] = "blocked"
    step["output"] = f"BLOQUEADO: {blocker}"

    logger.warning(f"[PaL] Passo {current} bloqueado: {blocker}")

    response = f"⚠️ Passo {current} está bloqueado\n\n**Bloqueador**: {blocker}\n"

    if suggestion:
        response += f"**Resolução sugerida**: {suggestion}\n"

    response += (
        "\n**Opções**:\n"
        "  - Resolver o bloqueador e chamar complete_step()\n"
        "  - Usar update_plan(action='revisit', ...) para tentar uma abordagem diferente\n"
        "  - Usar reset_plan(confirm=True) para começar do zero"
    )

    return response


def get_status(run_context: RunContext) -> str:
    """
    Obter uma visão formatada do status atual do plano.
    Mostra objetivo, todos os passos com seus status e progresso.
    """
    state = run_context.session_state

    if not state.get("plan"):
        return (
            "📋 Nenhum plano ativo.\n\n"
            "Usar create_plan() para começar. Exemplo:\n"
            "```\n"
            "create_plan(\n"
            '    objective="Seu objetivo aqui",\n'
            "    steps=[\n"
            '        {"description": "Primeiro passo", "success_criteria": "Como verificar"},\n'
            '        {"description": "Segundo passo", "success_criteria": "Como verificar"},\n'
            "    ]\n"
            ")\n"
            "```"
        )

    objective = state["objective"]
    context = state.get("context")
    plan = state["plan"]
    current = state["current_step"]
    status = state["status"]

    # Status icons
    icons = {
        "pending": "○",
        "complete": "✓",
        "blocked": "✗",
    }

    # Build output
    lines = [
        f"{'═' * 50}",
        f"🎯 OBJECTIVE: {objective}",
        f"📊 STATUS: {status.upper()}",
    ]

    if context:
        lines.append(f"📝 Context: {context}")

    lines.extend(["", "STEPS:", ""])

    for s in plan:
        icon = icons.get(s["status"], "○")
        is_current = s["id"] == current and s["status"] not in ["complete", "blocked"]
        marker = " ◀ CURRENT" if is_current else ""

        lines.append(f"  {icon} [{s['id']}] {s['description']}{marker}")

        if is_current:
            lines.append(f"       ✓ Must satisfy: {s['success_criteria']}")

        if s["output"] and s["status"] == "complete":
            # Truncate long outputs
            output_preview = (
                s["output"][:80] + "..." if len(s["output"]) > 80 else s["output"]
            )
            lines.append(f"       └─ {output_preview}")
        elif s["status"] == "blocked":
            lines.append(f"       └─ {s['output']}")

    # Progress bar
    done = sum(1 for s in plan if s["status"] == "complete")
    total = len(plan)
    pct = int(done / total * 100) if total > 0 else 0
    bar_filled = int(pct / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)

    lines.extend(
        [
            "",
            f"Progress: [{bar}] {done}/{total} ({pct}%)",
            f"{'═' * 50}",
        ]
    )

    return "\n".join(lines)


def reset_plan(run_context: RunContext, confirm: bool = False) -> str:
    """
    Limpar o plano atual para começar do zero.

    Args:
        confirm: Deve ser True para realmente redefinir (verificação de segurança)
    """
    if not confirm:
        return (
            "⚠️ Isso limpará o plano atual e todo o progresso.\n"
            "Para confirmar, chamar: reset_plan(confirm=True)"
        )

    state = run_context.session_state
    state.update(
        {
            "objective": None,
            "context": None,
            "plan": [],
            "plan_length": 0,
            "current_step": 1,
            "status": "no_plan",
            "created_at": None,
            "completed_at": None,
        }
    )

    logger.info("[PaL] Plano redefinido")
    return "🗑️ Plano limpo. Pronto para criar um novo plano."


# ============================================================================
# Ferramenta de Aprendizado
# ============================================================================
def save_learning(
    run_context: RunContext,
    title: str,
    learning: str,
    applies_to: str,
    effectiveness: Optional[str] = "medium",
) -> str:
    """
    Salvar um aprendizado reutilizável desta execução para referência futura.

    Apenas salvar aprendizados que sejam:
    - Específicos e acionáveis
    - Aplicáveis a tarefas futuras semelhantes
    - Baseados no que realmente funcionou

    Args:
        title: Nome descritivo curto (ex: "Padrão de Pesquisa de Preços")
        learning: O insight/padrão real (seja específico!)
        applies_to: Que tipos de tarefas isso ajuda
        effectiveness: Quão bem funcionou - "low" | "medium" | "high"

    Exemplo:
        save_learning(
            title="Fontes de Preços de Concorrentes",
            learning="Para preços SaaS: 1) Página oficial de preços, 2) G2/Capterra, 3) Arquivos PricingBot. Páginas oficiais frequentemente escondem níveis empresariais.",
            applies_to="análise competitiva, pesquisa de preços, pesquisa de mercado",
            effectiveness="high"
        )
    """
    state = run_context.session_state

    payload = {
        "title": title.strip(),
        "learning": learning.strip(),
        "applies_to": applies_to.strip(),
        "effectiveness": effectiveness,
        "source_objective": state.get("objective", "unknown"),
        "source_steps": len(state.get("plan", [])),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(f"[PaL] Salvando aprendizado: {payload['title']}")

    try:
        execution_knowledge.add_content(
            name=payload["title"],
            text_content=json.dumps(payload, ensure_ascii=False),
            reader=TextReader(),
            skip_if_exists=True,
        )
        return (
            f"💡 Aprendizado salvo!\n\n"
            f"**{title}**\n"
            f"{learning}\n\n"
            f"_Aplica-se a: {applies_to}_"
        )
    except Exception as e:
        logger.error(f"[PaL] Falha ao salvar aprendizado: {e}")
        return f"❌ Falha ao salvar aprendizado: {str(e)}"


# ============================================================================
# Instruções do Agente
# ============================================================================
instructions = """\
Você é **PaL** — o Agente **Planejar e Aprender**.

Você é um assistente amigável e útil que também pode lidar com tarefas complexas de múltiplos passos com disciplina. Você planeja quando é útil, não para tudo.

## QUANDO PLANEJAR

**Criar um plano** para tarefas que:
- Têm múltiplos passos distintos
- Precisam ser feitas em uma ordem específica
- Se beneficiariam do rastreamento de progresso
- São complexas o suficiente para você perder o controle

**Não planejar** para:
- Perguntas simples → apenas respondê-las
- Tarefas rápidas → apenas fazê-las
- Conversa casual → apenas conversar
- Solicitações de passo único → apenas lidar com elas

Em caso de dúvida: se você pode fazer em uma resposta sem perder o controle, pule o plano.

## ESTADO ATUAL
- Objetivo: {objective}
- Passo: {current_step} de {plan_length}
- Status: {status}

## O CICLO PaL (para tarefas complexas)

1. **PLANEJAR** — Dividir o objetivo em passos com critérios de sucesso. Chamar `create_plan()`.
2. **EXECUTAR** — Trabalhar através de passos um de cada vez. Chamar `complete_step()` com evidências.
3. **ADAPTAR** — Adicionar, revisitar ou bloquear passos conforme necessário. Planos podem evoluir.
4. **APRENDER** — Após o sucesso, propor insights reutilizáveis. Salvar apenas com aprovação do usuário.

## REGRAS DE EXECUÇÃO (ao planejar)

- Completar passo N antes de começar passo N+1
- Verificar critérios de sucesso antes de chamar `complete_step()`
- Usar ferramentas para mudar estado — não apenas descrever mudanças

## SUA BASE DE CONHECIMENTO

Você tem aprendizados de tarefas passadas. Ao planejar algo semelhante:
- Buscar padrões relevantes
- Aplicar o que funcionou antes
- Mencionar quando um aprendizado influenciou sua abordagem

## PERSONALIDADE

Você é um PaL — amigável, útil e fácil de conversar. Você:
- Conversa naturalmente para coisas simples
- Fica estruturado quando a complexidade exige
- Celebra progresso sem exagerar
- Resiste suavemente se pedido para pular passos importantes
- Aprende e melhora com o tempo

Seja útil primeiro. Seja disciplinado quando importa.\
"""


# ============================================================================
# Create the Agent
# ============================================================================
pal_agent = Agent(
    id="plan-and-learn-agent",
    name="PaL (Plan and Learn Agent)",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    # Banco de dados para persistência
    db=gemini_agents_db,
    # Base de conhecimento para aprendizados
    knowledge=execution_knowledge,
    search_knowledge=True,
    # Estrutura de estado de sessão
    session_state={
        "objective": None,
        "context": None,
        "plan": [],
        "plan_length": 0,
        "current_step": 1,
        "status": "no_plan",
        "created_at": None,
        "completed_at": None,
    },
    tools=[
        # Gerenciamento de plano
        create_plan,
        complete_step,
        update_plan,
        block_step,
        get_status,
        reset_plan,
        # Aprendizado
        save_learning,
        # Capacidades de execução
        ParallelTools(),
        YFinanceTools(),
    ],
    # Tornar estado disponível nas instruções
    add_session_state_to_context=True,
    # Habilitar memória para preferências do usuário
    enable_agentic_memory=True,
    # Gerenciamento de contexto
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    read_chat_history=True,
    # Saída
    markdown=True,
)


# ============================================================================
# Interface CLI
# ============================================================================
def run_pal(message: str, session_id: Optional[str] = None, show_state: bool = True):
    """
    Executar PaL com uma mensagem, opcionalmente continuando uma sessão.

    Args:
        message: A mensagem/solicitação do usuário
        session_id: ID de sessão opcional para continuar uma sessão anterior
        show_state: Se deve imprimir o estado após a resposta
    """
    pal_agent.print_response(message, session_id=session_id, stream=True)
    if show_state:
        state = pal_agent.get_session_state()
        print(f"\n{'─' * 50}")
        print("📊 Estado da Sessão:")
        print(f"   Status: {state.get('status', 'no_plan')}")
        if state.get("plan"):
            done = sum(1 for s in state["plan"] if s["status"] == "complete")
            print(f"   Progresso: {done}/{len(state['plan'])} passos")
        print(f"{'─' * 50}")


# ============================================================================
# Principal
# ============================================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Executar com argumento de linha de comando
        message = " ".join(sys.argv[1:])
        run_pal(message)
    else:
        # Modo interativo
        print("=" * 60)
        print("🤝 PaL — Agente Planejar e Aprender")
        print("   Planejar. Executar. Aprender. Repetir.")
        print("=" * 60)
        print("\nDigite 'quit' ou 'exit' para parar.\n")

        session_id = f"pal_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        while True:
            try:
                user_input = input("\n👤 Você: ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Até logo!")
                    break
                if not user_input:
                    continue

                print()
                run_pal(user_input, session_id=session_id)

            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
