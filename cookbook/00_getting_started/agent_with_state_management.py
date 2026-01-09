"""
Agente com Gerenciamento de Estado - Agente Financeiro com Lista de Observação
================================================================================
Este exemplo mostra como dar ao seu agente estado persistente que ele pode
ler e modificar. O agente mantém uma lista de observação de ações entre conversas.

Diferente de armazenamento (histórico de conversas) e memória (preferências do usuário),
estado é dados estruturados que o agente gerencia ativamente: contadores, listas, flags.

Conceitos-chave:
- session_state: Um dict que persiste entre execuções
- Ferramentas podem ler/escrever estado via run_context.session_state
- Variáveis de estado podem ser injetadas nas instruções com {variable_name}

Exemplos de prompts para testar:
- "Adicione NVDA e AMD à minha lista de observação"
- "O que está na minha lista de observação?"
- "Remova AMD da lista"
- "Como estão minhas ações observadas hoje?"
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.run import RunContext
from agno.tools.yfinance import YFinanceTools

# ============================================================================
# Configuração de Armazenamento
# ============================================================================
agent_db = SqliteDb(db_file="tmp/agents.db")


# ============================================================================
# Ferramentas Personalizadas que Modificam Estado
# ============================================================================
def add_to_watchlist(run_context: RunContext, ticker: str) -> str:
    """
    Adiciona um ticker de ação à lista de observação.

    Args:
        ticker: Símbolo do ticker da ação (ex: NVDA, AAPL)

    Returns:
        Mensagem de confirmação
    """
    ticker = ticker.upper().strip()
    watchlist = run_context.session_state.get("watchlist", [])

    if ticker in watchlist:
        return f"{ticker} já está na sua lista de observação"

    watchlist.append(ticker)
    run_context.session_state["watchlist"] = watchlist

    return f"Adicionado {ticker} à lista de observação. Lista atual: {', '.join(watchlist)}"


def remove_from_watchlist(run_context: RunContext, ticker: str) -> str:
    """
    Remove um ticker de ação da lista de observação.

    Args:
        ticker: Símbolo do ticker da ação a remover

    Returns:
        Mensagem de confirmação
    """
    ticker = ticker.upper().strip()
    watchlist = run_context.session_state.get("watchlist", [])

    if ticker not in watchlist:
        return f"{ticker} não está na sua lista de observação"

    watchlist.remove(ticker)
    run_context.session_state["watchlist"] = watchlist

    if watchlist:
        return f"Removido {ticker}. Lista restante: {', '.join(watchlist)}"
    return f"Removido {ticker}. A lista de observação está vazia agora."


# ============================================================================
# Instruções do Agente
# ============================================================================
instructions = """\
Você é um Agente Financeiro que gerencia uma lista de observação de ações.

## Lista de Observação Atual
{watchlist}

## Capacidades

1. Gerenciar lista de observação
   - Adicionar ações: use a ferramenta add_to_watchlist
   - Remover ações: use a ferramenta remove_from_watchlist

2. Obter dados de ações
   - Use ferramentas YFinance para buscar preços e métricas das ações observadas
   - Compare ações na lista de observação

## Regras

- Sempre confirme mudanças na lista de observação
- Quando perguntado sobre "minhas ações" ou "lista de observação", refira-se ao estado atual
- Busque dados atualizados ao relatar o desempenho da lista de observação\
"""

# ============================================================================
# Criar o Agente
# ============================================================================
agent_with_state_management = Agent(
    name="Agent with State Management",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    tools=[
        add_to_watchlist,
        remove_from_watchlist,
        YFinanceTools(),
    ],
    session_state={"watchlist": []},
    add_session_state_to_context=True,
    db=agent_db,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

# ============================================================================
# Executar o Agente
# ============================================================================
if __name__ == "__main__":
    # Adicionar algumas ações
    agent_with_state_management.print_response(
        "Adicione NVDA, AAPL e GOOGL à minha lista de observação",
        stream=True,
    )

    # Verificar a lista de observação
    agent_with_state_management.print_response(
        "Como estão minhas ações observadas hoje?",
        stream=True,
    )

    # Ver o estado diretamente
    print("\n" + "=" * 60)
    print("Estado da Sessão:")
    print(
        f"  Lista de Observação: {agent_with_state_management.get_session_state().get('watchlist', [])}"
    )
    print("=" * 60)

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Estado vs Armazenamento vs Memória:

- Estado: Dados estruturados que o agente gerencia (lista de observação, contadores, flags)
- Armazenamento: Histórico de conversas ("o que discutimos?")
- Memória: Preferências do usuário ("o que eu gosto?")

Estado é perfeito para:
- Rastrear itens (listas de observação, todos, carrinhos)
- Contadores e progresso
- Workflows de múltiplas etapas
- Qualquer dado estruturado que muda durante a conversa

Acessando estado:

1. Em ferramentas: run_context.session_state["key"]
2. Em instruções: {key} (com add_session_state_to_context=True)
3. Após execução: agent.get_session_state() ou response.session_state
"""
