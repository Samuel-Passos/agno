"""
Este exemplo demonstra max_tool_calls_from_history para limitar chamadas de ferramenta enviadas ao modelo.

Como funciona:
1. Banco de dados armazena TODAS as execuções (sem limite)
2. num_history_runs carrega as últimas N execuções do banco de dados (padrão: 3)
3. max_tool_calls_from_history filtra o histórico carregado para manter apenas as M chamadas de ferramenta mais recentes

Fluxo: Banco de Dados → Carregar Histórico → Filtrar Chamadas de Ferramenta → Enviar ao Modelo

Comportamento esperado (com add_history_to_context=True, sem limite num_history_runs):
- Execução 1: Sem histórico → Modelo vê: [1] → BD tem: [1]
- Execução 2: Histórico [1] → Modelo vê: [1, 2] → BD tem: [1, 2]
- Execução 3: Histórico [1,2] → Modelo vê: [1, 2, 3] → BD tem: [1, 2, 3]
- Execução 4: Histórico [1,2,3] → Modelo vê: [1, 2, 3, 4] → BD tem: [1, 2, 3, 4]
- Execução 5: Histórico [1,2,3,4] filtrado para [2,3,4] → Modelo vê: [2, 3, 4, 5] → BD tem: [1, 2, 3, 4, 5]
- Execução 6: Histórico [2,3,4,5] filtrado para [3,4,5] → Modelo vê: [3, 4, 5, 6] → BD tem: [1, 2, 3, 4, 5, 6]

Insight chave: A filtragem afeta apenas a ENTRADA DO MODELO. O banco de dados armazena tudo, sempre.
"""

import random

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat


def get_weather_for_city(city: str) -> str:
    conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Foggy", "Windy"]
    temperature = random.randint(-10, 35)
    condition = random.choice(conditions)

    return f"{city}: {temperature}°C, {condition}"


agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[get_weather_for_city],
    instructions="Você é um assistente de clima. Obter o clima usando a ferramenta get_weather_for_city.",
    # Manter apenas as 3 chamadas de ferramenta mais recentes do histórico no contexto (reduz custos de token)
    max_tool_calls_from_history=3,
    db=SqliteDb(db_file="tmp/weather_data.db"),
    add_history_to_context=True,
    markdown=True,
    # debug_mode=True,
)

cities = [
    "Tokyo",
    "Delhi",
    "Shanghai",
    "São Paulo",
    "Mumbai",
    "Beijing",
    "Cairo",
    "London",
]

print("\n" + "=" * 90)
print("Demonstração de Filtragem de Chamadas de Ferramenta: max_tool_calls_from_history=3")
print("=" * 90)
print(
    f"{'Execução':<9} | {'Cidade':<15} | {'Histórico':<9} | {'Atual':<8} | {'No Contexto':<12} | {'No BD':<8}"
)
print("-" * 90)


for i, city in enumerate(cities, 1):
    run_response = agent.run(f"Qual é o clima em {city}?")

    # Contar chamadas de ferramenta do histórico (enviadas ao modelo após filtragem)
    history_tool_calls = sum(
        len(msg.tool_calls)
        for msg in run_response.messages
        if msg.role == "assistant"
        and msg.tool_calls
        and getattr(msg, "from_history", False)
    )

    # Contar chamadas de ferramenta da execução atual
    current_tool_calls = sum(
        len(msg.tool_calls)
        for msg in run_response.messages
        if msg.role == "assistant"
        and msg.tool_calls
        and not getattr(msg, "from_history", False)
    )

    total_in_context = history_tool_calls + current_tool_calls

    # Total de chamadas de ferramenta armazenadas no banco de dados (não filtradas)
    saved_messages = agent.get_session_messages()
    total_in_db = (
        sum(
            len(msg.tool_calls)
            for msg in saved_messages
            if msg.role == "assistant" and msg.tool_calls
        )
        if saved_messages
        else 0
    )

    print(
        f"{i:<9} | {city:<15} | {history_tool_calls:<9} | {current_tool_calls:<8} | {total_in_context:<12} | {total_in_db:<8}"
    )
