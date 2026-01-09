"""
Humano no Loop - Confirmar Antes de Tomar Ação
===============================================
Este exemplo mostra como exigir confirmação do usuário antes de executar
certas ferramentas. Crítico para ações que são irreversíveis ou sensíveis.

Vamos construir sobre nosso agente de autoaprendizado e pedir confirmação do usuário antes de salvar um aprendizado.

Conceitos-chave:
- @tool(requires_confirmation=True): Marcar ferramentas que precisam de aprovação
- run_response.active_requirements: Verificar confirmações pendentes
- requirement.confirm() / requirement.reject(): Aprovar ou negar
- agent.continue_run(): Retomar execução após decisão

Algumas aplicações práticas:
- Confirmar operações sensíveis antes da execução
- Revisar chamadas de API antes de serem feitas
- Validar transformações de dados
- Aprovar ações automatizadas em sistemas críticos

Exemplos de prompts para testar:
- "Qual é uma boa relação P/E para ações de tecnologia? Salve esse insight."
- "Analise NVDA e salve quaisquer insights"
- "Quais aprendizados temos salvos?"
"""

import json
from datetime import datetime, timezone

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.text_reader import TextReader
from agno.models.google import Gemini
from agno.tools import tool
from agno.tools.yfinance import YFinanceTools
from agno.utils import pprint
from agno.vectordb.chroma import ChromaDb
from agno.vectordb.search import SearchType
from rich.console import Console
from rich.prompt import Prompt

# ============================================================================
# Configuração de Armazenamento
# ============================================================================
agent_db = SqliteDb(db_file="tmp/agents.db")

# ============================================================================
# Base de Conhecimento para Aprendizados
# ============================================================================
learnings_kb = Knowledge(
    name="Agent Learnings",
    vector_db=ChromaDb(
        name="learnings",
        collection="learnings",
        path="tmp/chromadb",
        persistent_client=True,
        search_type=SearchType.hybrid,
        embedder=GeminiEmbedder(id="gemini-embedding-001"),
    ),
    max_results=5,
    contents_db=agent_db,
)


# ============================================================================
# Ferramenta Personalizada: Salvar Aprendizado (requer confirmação)
# ============================================================================
@tool(requires_confirmation=True)
def save_learning(title: str, learning: str) -> str:
    """
    Salva um insight reutilizável na base de conhecimento para referência futura.
    Esta ação requer confirmação do usuário antes de executar.

    Args:
        title: Título descritivo curto (ex: "Benchmarks P/E de ações de tecnologia")
        learning: O insight a salvar — seja específico e acionável

    Returns:
        Mensagem de confirmação
    """
    if not title or not title.strip():
        return "Não é possível salvar: título é obrigatório"
    if not learning or not learning.strip():
        return "Não é possível salvar: conteúdo do aprendizado é obrigatório"

    payload = {
        "title": title.strip(),
        "learning": learning.strip(),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }

    learnings_kb.add_content(
        name=payload["title"],
        text_content=json.dumps(payload, ensure_ascii=False),
        reader=TextReader(),
        skip_if_exists=True,
    )

    return f"Salvo: '{title}'"


# ============================================================================
# Instruções do Agente
# ============================================================================
instructions = """\
Você é um Agente Financeiro que aprende e melhora com o tempo.

Você tem duas habilidades especiais:
1. Pesquisar sua base de conhecimento por aprendizados previamente salvos
2. Salvar novos insights usando a ferramenta save_learning

## Fluxo de Trabalho

1. Verificar Conhecimento Primeiro
   - Antes de responder, pesquisar aprendizados anteriores relevantes
   - Aplicar quaisquer insights relevantes à sua resposta

2. Coletar Informações
   - Usar ferramentas YFinance para dados de mercado
   - Combinar com insights da sua base de conhecimento

3. Salvar Insights Valiosos
   - Se descobrir algo reutilizável, salve com save_learning
   - O usuário será solicitado a confirmar antes de ser salvo
   - Bons aprendizados são específicos, acionáveis e generalizáveis

## O que Faz um Bom Aprendizado

- Específico: "Relações P/E de tecnologia geralmente variam 20-35x" não "P/E varia"
- Acionável: Pode ser aplicado a perguntas futuras
- Reutilizável: Útil além desta conversa

Não salvar: Dados brutos, fatos únicos ou informações óbvias.\
"""

# ============================================================================
# Criar o Agente
# ============================================================================
human_in_the_loop_agent = Agent(
    name="Agent with Human in the Loop",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    tools=[
        YFinanceTools(),
        save_learning,
    ],
    knowledge=learnings_kb,
    search_knowledge=True,
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
    console = Console()

    # Fazer uma pergunta que pode acionar um salvamento
    run_response = human_in_the_loop_agent.run(
        "Qual é uma relação P/E saudável para ações de tecnologia? Salve esse insight."
    )

    # Lidar com quaisquer requisitos de confirmação
    for requirement in run_response.active_requirements:
        if requirement.needs_confirmation:
            console.print(
                f"\n[bold yellow]🛑 Confirmação Necessária[/bold yellow]\n"
                f"Ferramenta: [bold blue]{requirement.tool_execution.tool_name}[/bold blue]\n"
                f"Args: {requirement.tool_execution.tool_args}"
            )

            choice = (
                Prompt.ask(
                    "Você deseja continuar?",
                    choices=["y", "n"],
                    default="y",
                )
                .strip()
                .lower()
            )

            if choice == "n":
                requirement.reject()
                console.print("[red]❌ Rejeitado[/red]")
            else:
                requirement.confirm()
                console.print("[green]✅ Aprovado[/green]")

    # Continuar a execução com as decisões do usuário
    run_response = human_in_the_loop_agent.continue_run(
        run_id=run_response.run_id,
        requirements=run_response.requirements,
    )

    pprint.pprint_run_response(run_response)

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Padrões de humano-no-loop:

1. Confirmação para ações sensíveis
   @tool(requires_confirmation=True)
   def delete_file(path: str) -> str:
       ...

2. Confirmação para chamadas externas
   @tool(requires_confirmation=True)
   def send_email(to: str, subject: str, body: str) -> str:
       ...

3. Confirmação para transações financeiras
   @tool(requires_confirmation=True)
   def place_order(ticker: str, quantity: int, side: str) -> str:
       ...

O padrão:
1. Marcar ferramenta com @tool(requires_confirmation=True)
2. Executar agente com agent.run()
3. Iterar por run_response.active_requirements
4. Verificar requirement.needs_confirmation
5. Chamar requirement.confirm() ou requirement.reject()
6. Chamar agent.continue_run() com requirements

Isso dá a você controle total sobre quais ações executar.
"""
