"""
Time Multi-Agente - Time de Pesquisa de Investimentos
======================================================
Este exemplo mostra como criar um time de agentes que trabalham juntos.
Cada agente tem um papel especializado, e o líder do time coordena.

Vamos construir um time de pesquisa de investimentos com perspectivas opostas:
- Agente Bull: Faz o caso A FAVOR do investimento
- Agente Bear: Faz o caso CONTRA o investimento
- Analista Líder: Sintetiza em uma recomendação equilibrada

Esta abordagem adversarial produz melhor análise do que um único agente.

Conceitos-chave:
- Time: Um grupo de agentes coordenados por um líder
- Membros: Agentes especializados com papéis distintos
- O líder delega, sintetiza e produz a saída final

Exemplos de prompts para testar:
- "Devo investir na NVIDIA?"
- "Analise a Tesla como um investimento de longo prazo"
- "A Apple está supervalorizada agora?"
"""

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.google import Gemini
from agno.team.team import Team
from agno.tools.yfinance import YFinanceTools

# ============================================================================
# Configuração de Armazenamento
# ============================================================================
team_db = SqliteDb(db_file="tmp/agents.db")

# ============================================================================
# Agente Bull — Faz o Caso A FAVOR
# ============================================================================
bull_agent = Agent(
    name="Bull Analyst",
    role="Make the investment case FOR a stock",
    model=Gemini(id="gemini-3-flash-preview"),
    tools=[YFinanceTools()],
    db=team_db,
    instructions="""\
Você é um analista bull. Seu trabalho é fazer o caso mais forte possível
A FAVOR de investir em uma ação. Encontre os pontos positivos:
- Drivers de crescimento e catalisadores
- Vantagens competitivas
- Finanças e métricas fortes
- Oportunidades de mercado

Seja persuasivo, mas fundamentado em dados. Use as ferramentas para obter números reais.\
""",
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
)

# ============================================================================
# Agente Bear — Faz o Caso CONTRA
# ============================================================================
bear_agent = Agent(
    name="Bear Analyst",
    role="Make the investment case AGAINST a stock",
    model=Gemini(id="gemini-3-flash-preview"),
    tools=[YFinanceTools()],
    db=team_db,
    instructions="""\
Você é um analista bear. Seu trabalho é fazer o caso mais forte possível
CONTRA investir em uma ação. Encontre os riscos:
- Preocupações de avaliação
- Ameaças competitivas
- Pontos fracos nas finanças
- Riscos de mercado ou macro

Seja crítico, mas justo. Use as ferramentas para obter números reais que apoiem suas preocupações.\
""",
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
)

# ============================================================================
# Líder do Time — Sintetiza Ambas as Visões
# ============================================================================
multi_agent_team = Team(
    name="Multi-Agent Team",
    model=Gemini(id="gemini-3-flash-preview"),
    members=[bull_agent, bear_agent],
    instructions="""\
Você lidera um time de pesquisa de investimentos com um Analista Bull e um Analista Bear.

## Processo

1. Envie a ação para AMBOS os analistas
2. Deixe cada um fazer seu caso independentemente
3. Sintetize seus argumentos em uma recomendação equilibrada

## Formato de Saída

Após ouvir ambos os analistas, forneça:
- **Resumo do Caso Bull**: Pontos-chave do analista bull
- **Resumo do Caso Bear**: Pontos-chave do analista bear
- **Síntese**: Onde eles concordam? Onde discordam?
- **Recomendação**: Sua visão equilibrada (Buy/Hold/Sell) com nível de confiança
- **Métricas-Chave**: Uma tabela dos números importantes

Seja decisivo, mas reconheça a incerteza.\
""",
    db=team_db,
    show_members_responses=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

# ============================================================================
# Executar o Time
# ============================================================================
if __name__ == "__main__":
    # Primeira análise
    multi_agent_team.print_response(
        "Devo investir na NVIDIA (NVDA)?",
        stream=True,
    )

    # Pergunta de acompanhamento — o time lembra da análise anterior
    multi_agent_team.print_response(
        "Como a AMD se compara a isso?",
        stream=True,
    )

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Quando usar Times vs Agente único:

Agente Único:
- Uma tarefa coerente
- Não precisa de visões opostas
- Simples é melhor

Time:
- Múltiplas perspectivas necessárias
- Expertise especializada
- Tarefas complexas que se beneficiam da divisão de trabalho
- Raciocínio adversarial (como este exemplo)

Outros padrões de time:

1. Pipeline Pesquisa → Análise → Escrita
   researcher = Agent(role="Coletar informações")
   analyst = Agent(role="Analisar dados")
   writer = Agent(role="Escrever relatório")

2. Padrão Verificador
   worker = Agent(role="Fazer a tarefa")
   checker = Agent(role="Verificar o trabalho")

3. Roteamento de Especialista
   classifier = Agent(role="Rotear para especialista")
   specialists = [finance_agent, legal_agent, tech_agent]
"""
