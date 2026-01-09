from typing import Any, Dict

from agents import (
    SupportTicketClassification,
    support_agent,
    triage_agent,
)
from agno.utils.log import log_info
from agno.workflow import Step, StepInput, StepOutput, Workflow


def cache_lookup_step(
    step_input: StepInput, session_state: Dict[str, Any]
) -> StepOutput:
    """Passo 1: Verificar se temos uma solução em cache para esta consulta"""
    query = step_input.input

    cached_solution = session_state.get("solutions", {}).get(query)
    if cached_solution:
        log_info(f"Cache hit! Retornando solução em cache para consulta: {query}")
        return StepOutput(content=cached_solution, stop=True)

    log_info(f"Nenhuma solução em cache encontrada para consulta: {query}")
    return StepOutput(
        content=query,
    )


def triage_step(step_input: StepInput) -> StepOutput:
    """Passo 2: Classificar e analisar a consulta do cliente"""
    query = step_input.input

    classification_response = triage_agent.run(query)
    classification = classification_response.content

    assert isinstance(classification, SupportTicketClassification)

    log_info(f"Classificação: {classification.model_dump_json()}")

    return StepOutput(
        content=classification,
    )


def cache_storage_step(
    step_input: StepInput, session_state: Dict[str, Any]
) -> StepOutput:
    """Passo 4: Armazenar a solução em cache para uso futuro"""
    query = step_input.input
    solution = step_input.get_last_step_content()

    # Inicializar cache de soluções se não existir
    if "solutions" not in session_state:
        session_state["solutions"] = {}

    # Armazenar a solução em cache
    session_state["solutions"][query] = solution
    log_info(f"Solução em cache para consulta: {query}")

    return StepOutput(content=solution)


# Criar o workflow de suporte ao cliente com múltiplos passos
customer_support_workflow = Workflow(
    name="Customer Support Resolution Pipeline",
    description="Suporte ao cliente alimentado por IA com cache inteligente e processamento multi-passo",
    steps=[
        Step(name="Cache Lookup", executor=cache_lookup_step),
        Step(name="Query Triage", executor=triage_step),
        Step(name="Solution Generation", agent=support_agent),
        Step(name="Cache Storage", executor=cache_storage_step),
    ],
)


if __name__ == "__main__":
    test_queries = [
        "I can't log into my account, forgot my password",
        "How do I reset my password?",
        "My billing seems wrong, I was charged twice",
        "The app keeps crashing when I upload files",
        "I can't log into my account, forgot my password",  # repeat query
    ]

    for i, query in enumerate(test_queries, 1):
        response = customer_support_workflow.run(input=query)
