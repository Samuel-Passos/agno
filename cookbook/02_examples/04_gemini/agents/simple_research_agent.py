from textwrap import dedent

from agno.agent import Agent
from agno.models.google import Gemini
from db import gemini_agents_db

simple_research_agent = Agent(
    name="Simple Research Agent",
    model=Gemini(
        id="gemini-3-flash-preview",
        search=True,
    ),
    instructions=dedent("""\
    Você é um agente de pesquisa com acesso à web.
    Sua tarefa é responder perguntas pesquisando ativamente na web e sintetizando informações de múltiplas fontes.

    Ao responder:
    1. Começar com uma resposta curta e direta (máximo de 2-4 frases).
    2. Depois fornecer uma análise estruturada com cabeçalhos de seção claros.
    3. Usar resultados de busca web para apoiar afirmações e sempre incluir citações de fontes com URLs.
    4. Separar claramente entre:
        - Fatos verificados
        - Interpretações ou opiniões fundamentadas
    5. Se a informação pode estar desatualizada, incompleta ou disputada, notar isso explicitamente.
    6. Preferir fontes primárias ou autoritárias quando disponíveis.
    7. Manter respostas concisas, escaneáveis e neutras em tom.

    Regras de formatação:
    - Usar cabeçalhos markdown e marcadores.
    - Incluir uma seção "Fontes" no final com URLs vinculadas. Certificar-se de vincular as URLs às fontes reais. Você pode usar formatação markdown para tornar as URLs clicáveis.\
    """),
    db=gemini_agents_db,
    # Habilitar o agente para lembrar informações e preferências do usuário
    enable_agentic_memory=True,
    # Adicionar a data e hora atuais ao contexto
    add_datetime_to_context=True,
    # Adicionar o histórico das execuções do agente ao contexto
    add_history_to_context=True,
    # Número de execuções históricas para incluir no contexto
    num_history_runs=3,
    markdown=True,
)


if __name__ == "__main__":
    simple_research_agent.print_response(
        "What are the differences between the Gemini 3 and GPT-5 family of models. When should each be used?",
        stream=True,
    )
