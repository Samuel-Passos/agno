"""
Agente com Armazenamento - Agente Financeiro com Armazenamento
===============================================================
Construindo sobre o Agente Financeiro do exemplo 01, este exemplo adiciona armazenamento persistente.
Seu agente agora lembra conversas entre execuções.

Pergunte sobre NVDA, feche o script, volte depois — continue de onde parou.
O histórico da conversa é salvo no SQLite e restaurado automaticamente.

Conceitos-chave:
- Execução: Cada vez que você executa o agente (via agent.print_response() ou agent.run())
- Sessão: Uma thread de conversa, identificada por session_id
- Mesmo session_id = conversa contínua, mesmo entre execuções

Exemplos de prompts para testar:
- "Qual é o preço atual da AAPL?"
- "Compare isso com a Microsoft" (ele lembra da AAPL)
- "Com base em nossa discussão, qual parece melhor?"
- "Quais ações analisamos até agora?"
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools

# ============================================================================
# Configuração de Armazenamento
# ============================================================================
agent_db = SqliteDb(db_file="tmp/agents.db")

# ============================================================================
# Instruções do Agente
# ============================================================================
instructions = """\
Você é um Agente Financeiro — um analista orientado por dados que recupera dados de mercado,
calcula relações-chave e produz insights concisos e prontos para decisão.

## Fluxo de Trabalho

1. Esclarecer
   - Identificar tickers a partir de nomes de empresas (ex: Apple → AAPL)
   - Se ambíguo, perguntar

2. Recuperar
   - Buscar: preço, variação %, capitalização de mercado, P/E, EPS, faixa de 52 semanas
   - Para comparações, buscar os mesmos campos para cada ticker

3. Analisar
   - Calcular relações (P/E, P/S, margens) quando não fornecidas
   - Principais drivers e riscos — máximo de 2-3 pontos
   - Apenas fatos, sem especulação

4. Apresentar
   - Começar com um resumo de uma linha
   - Usar tabelas para comparações de múltiplas ações
   - Manter conciso

## Regras

- Fonte: Yahoo Finance. Sempre anotar o timestamp.
- Dados faltando? Diga "N/A" e continue.
- Sem conselhos personalizados — adicione aviso quando relevante.
- Sem emojis.
- Referenciar análises anteriores quando relevante.\
"""

# ============================================================================
# Criar o Agente
# ============================================================================
agent_with_storage = Agent(
    name="Agent with Storage",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    tools=[YFinanceTools()],
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
    # Usar um session_id consistente para persistir conversa entre execuções
    # Nota: session_id é gerado automaticamente se não definido
    session_id = "finance-agent-session"

    # Turno 1: Analisar uma ação
    agent_with_storage.print_response(
        "Me dê um resumo rápido de investimento sobre a NVIDIA",
        session_id=session_id,
        stream=True,
    )

    # Turno 2: Comparar — o agente lembra da NVDA do turno 1
    agent_with_storage.print_response(
        "Compare isso com a Tesla",
        session_id=session_id,
        stream=True,
    )

    # Turno 3: Pedir uma recomendação baseada na conversa completa
    agent_with_storage.print_response(
        "Com base em nossa discussão, qual parece ser o melhor investimento?",
        session_id=session_id,
        stream=True,
    )

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Teste este fluxo:

1. Execute o script — ele analisa NVDA, compara com TSLA, depois recomenda
2. Comente todos os três prompts acima
3. Adicione: agent.print_response("E a AMD?", session_id=session_id, stream=True)
4. Execute novamente — ele lembra da conversa completa NVDA vs TSLA

A camada de armazenamento persiste o histórico da sua conversa no SQLite.
Reinicie o script a qualquer momento e continue de onde parou.
"""
