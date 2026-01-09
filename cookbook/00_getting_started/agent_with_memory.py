"""
Agente com Memória - Agente Financeiro que Lembra de Você
==========================================================
Este exemplo mostra como dar ao seu agente memória de preferências do usuário.
O agente lembra fatos sobre você em todas as conversas.

Diferente de armazenamento (que persiste histórico de conversas), memória
persiste informações no nível do usuário: preferências, fatos, contexto.

Conceitos-chave:
- MemoryManager: Extrai e armazena memórias do usuário das conversas
- enable_agentic_memory: Agente decide quando armazenar/recuperar via chamadas de ferramentas (eficiente)
- enable_user_memories: Gerenciador de memória executa após cada resposta (captura garantida)
- user_id: Vincula memórias a um usuário específico

Exemplos de prompts para testar:
- "Estou interessado em ações de tecnologia, especialmente empresas de IA"
- "Minha tolerância ao risco é moderada"
- "Quais ações você recomendaria para mim?"
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.memory import MemoryManager
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools
from rich.pretty import pprint

# ============================================================================
# Configuração de Armazenamento
# ============================================================================
agent_db = SqliteDb(db_file="tmp/agents.db")

# ============================================================================
# Configuração do Gerenciador de Memória
# ============================================================================
memory_manager = MemoryManager(
    model=Gemini(id="gemini-3-flash-preview"),
    db=agent_db,
    additional_instructions="""
    Capture as ações favoritas do usuário, sua tolerância ao risco e seus objetivos de investimento.
    """,
)

# ============================================================================
# Instruções do Agente
# ============================================================================
instructions = """\
Você é um Agente Financeiro — um analista orientado por dados que recupera dados de mercado,
calcula relações-chave e produz insights concisos e prontos para decisão.

## Memória

Você tem memória de preferências do usuário (fornecidas automaticamente no contexto). Use isso para:
- Personalizar recomendações aos interesses deles
- Considerar a tolerância ao risco deles
- Referenciar os objetivos de investimento deles

## Fluxo de Trabalho

1. Recuperar
   - Buscar: preço, variação %, capitalização de mercado, P/E, EPS, faixa de 52 semanas
   - Para comparações, buscar os mesmos campos para cada ticker

2. Analisar
   - Calcular relações (P/E, P/S, margens) quando não fornecidas
   - Principais drivers e riscos — máximo de 2-3 pontos
   - Apenas fatos, sem especulação

3. Apresentar
   - Começar com um resumo de uma linha
   - Usar tabelas para comparações de múltiplas ações
   - Manter conciso

## Regras

- Fonte: Yahoo Finance. Sempre anotar o timestamp.
- Dados faltando? Diga "N/A" e continue.
- Sem conselhos personalizados — adicione aviso quando relevante.
- Sem emojis.\
"""

# ============================================================================
# Criar o Agente
# ============================================================================
user_id = "investor@example.com"

agent_with_memory = Agent(
    name="Agent with Memory",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    tools=[YFinanceTools()],
    db=agent_db,
    memory_manager=memory_manager,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

# ============================================================================
# Executar o Agente
# ============================================================================
if __name__ == "__main__":
    # Conte ao agente sobre você
    agent_with_memory.print_response(
        "Estou interessado em ações de IA e semicondutores. Minha tolerância ao risco é moderada.",
        user_id=user_id,
        stream=True,
    )

    # O agente agora conhece suas preferências
    agent_with_memory.print_response(
        "Quais ações você recomendaria para mim?",
        user_id=user_id,
        stream=True,
    )

    # Ver memórias armazenadas
    memories = agent_with_memory.get_user_memories(user_id=user_id)
    print("\n" + "=" * 60)
    print("Memórias Armazenadas:")
    print("=" * 60)
    pprint(memories)

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Memória vs Armazenamento:

- Armazenamento: "O que discutimos?" (histórico de conversas)
- Memória: "O que você sabe sobre mim?" (preferências do usuário)

Memória persiste entre sessões:

1. Execute este script — agente aprende suas preferências
2. Inicie uma NOVA sessão com o mesmo user_id
3. Agente ainda lembra que você gosta de ações de IA

Útil para:
- Recomendações personalizadas
- Lembrar contexto do usuário (trabalho, objetivos, restrições)
- Construir relacionamento entre conversas

Duas formas de habilitar memória:

1. enable_agentic_memory=True (usado neste exemplo)
   - Agente decide quando armazenar/recuperar via chamadas de ferramentas
   - Mais eficiente — só executa quando necessário

2. enable_user_memories=True
   - Gerenciador de memória executa após cada resposta do agente
   - Captura garantida — nunca perde informações do usuário
   - Maior latência e custo
"""
