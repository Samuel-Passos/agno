"""
Exemplo mostrando como armazenar em cache respostas do modelo para evitar chamadas de API redundantes.

A primeira execução levará um tempo para terminar.
A segunda execução acertará o cache e será muito mais rápida.

Você também pode ver o log de acerto de cache nos logs do console.
"""

import time

from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(model=OpenAIChat(id="gpt-4o", cache_response=True))

# Executar a mesma consulta duas vezes para demonstrar cache
for i in range(1, 3):
    print(f"\n{'=' * 60}")
    print(
        f"Execução {i}: {'Cache Miss (Primeira Solicitação)' if i == 1 else 'Cache Hit (Resposta em Cache)'}"
    )
    print(f"{'=' * 60}\n")

    response = agent.run(
        "Escreva-me uma história curta sobre um gato que pode falar e resolver problemas."
    )
    print(response.content)
    print(f"\n Tempo decorrido: {response.metrics.duration:.3f}s")

    # Pequeno atraso entre iterações para clareza
    if i == 1:
        time.sleep(0.5)
