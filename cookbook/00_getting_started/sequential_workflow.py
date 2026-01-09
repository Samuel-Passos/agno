"""
Workflow Sequencial - Pipeline de Pesquisa de Ações
====================================================
Este exemplo mostra como criar um workflow com etapas sequenciais.
Cada etapa é tratada por um agente especializado, e as saídas fluem para a próxima etapa.

Diferente de Times (agentes colaboram dinamicamente), Workflows dão a você
controle explícito sobre a ordem de execução e o fluxo de dados.

Conceitos-chave:
- Workflow: Orquestra uma sequência de etapas
- Step: Envolve um agente com uma tarefa específica
- Etapas executam em ordem, cada uma construindo sobre a anterior

Exemplos de prompts para testar:
- "Analise NVDA"
- "Pesquise Tesla para investimento"
- "Me dê um relatório sobre a Apple"
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools
from agno.workflow import Step, Workflow

# ============================================================================
# Configuração de Armazenamento
# ============================================================================
workflow_db = SqliteDb(db_file="tmp/agents.db")

# ============================================================================
# Etapa 1: Coletor de Dados — Busca dados brutos de mercado
# ============================================================================
data_agent = Agent(
    name="Data Gatherer",
    model=Gemini(id="gemini-3-flash-preview"),
    tools=[YFinanceTools()],
    instructions="""\
Você é um agente coletor de dados. Seu trabalho é buscar dados abrangentes de mercado.

Para a ação solicitada, colete:
- Preço atual e variação diária
- Capitalização de mercado e volume
- Relação P/E, EPS e outras relações-chave
- Máximo e mínimo de 52 semanas
- Tendências de preço recentes

Apresente os dados brutos claramente. Não analise — apenas colete e organize.\
""",
    db=workflow_db,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
)

data_step = Step(
    name="Data Gathering",
    agent=data_agent,
    description="Buscar dados abrangentes de mercado para a ação",
)

# ============================================================================
# Etapa 2: Analista — Interpreta os dados
# ============================================================================
analyst_agent = Agent(
    name="Analyst",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions="""\
Você é um analista financeiro. Você recebe dados brutos de mercado da equipe de dados.

Seu trabalho é:
- Interpretar as métricas-chave (o P/E está alto ou baixo para este setor?)
- Identificar pontos fortes e fracos
- Notar quaisquer sinais de alerta ou sinais positivos
- Comparar com benchmarks típicos da indústria

Forneça análise, não recomendações. Seja objetivo e orientado por dados.\
""",
    db=workflow_db,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
)

analysis_step = Step(
    name="Analysis",
    agent=analyst_agent,
    description="Analisar os dados de mercado e identificar insights-chave",
)

# ============================================================================
# Etapa 3: Escritor de Relatório — Produz saída final
# ============================================================================
report_agent = Agent(
    name="Report Writer",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions="""\
Você é um escritor de relatórios. Você recebe análise da equipe de pesquisa.

Seu trabalho é:
- Sintetizar a análise em um resumo de investimento claro
- Começar com um resumo de uma linha
- Incluir uma recomendação (Buy/Hold/Sell) com justificativa
- Manter conciso — máximo 200 palavras
- Terminar com métricas-chave em uma pequena tabela

Escreva para um investidor ocupado que quer a conclusão rapidamente.\
""",
    db=workflow_db,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

report_step = Step(
    name="Report Writing",
    agent=report_agent,
    description="Produzir um resumo de investimento conciso",
)

# ============================================================================
# Criar o Workflow
# ============================================================================
sequential_workflow = Workflow(
    name="Sequential Workflow",
    description="Pipeline de pesquisa de três etapas: Dados → Análise → Relatório",
    steps=[
        data_step,  # Etapa 1: Coletar dados
        analysis_step,  # Etapa 2: Analisar dados
        report_step,  # Etapa 3: Escrever relatório
    ],
)

# ============================================================================
# Executar o Workflow
# ============================================================================
if __name__ == "__main__":
    sequential_workflow.print_response(
        "Analise NVIDIA (NVDA) para investimento",
        stream=True,
    )

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Workflow vs Time:

- Workflow: Ordem explícita de etapas, execução previsível, fluxo de dados claro
- Time: Colaboração dinâmica, líder decide quem faz o quê

Use Workflow quando:
- Etapas devem acontecer em uma ordem específica
- Cada etapa tem um papel claro e especializado
- Você quer execução previsível e repetível
- Saída da etapa N alimenta a etapa N+1

Use Time quando:
- Agentes precisam colaborar dinamicamente
- O líder deve decidir quem envolver
- Tarefas se beneficiam de discussão de ida e volta

Recursos avançados de workflow (não mostrados aqui):
- Paralelo: Executar etapas simultaneamente
- Condição: Executar etapas apenas se critérios atendidos
- Loop: Repetir etapas até condição atendida
- Router: Selecionar dinamicamente qual etapa executar
"""
