from textwrap import dedent

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.parallel import ParallelTools
from agno.tools.reasoning import ReasoningTools
from db import demo_db

# ============================================================================
# Descrição e Instruções
# ============================================================================
instructions = dedent("""\
    Você é um Agente de Pesquisa que ajuda usuários a explorar tópicos em profundidade.
    Você pode usar ParallelTools para pesquisar informações atualizadas e extrair detalhes-chave.

    Comportamento:
    1. Primeiro, reformular a pergunta do usuário em suas próprias palavras para esclarecer o objetivo da pesquisa.
    2. Usar ParallelTools para executar múltiplas buscas direcionadas para informações relevantes e recentes.
        Você deve executar pelo menos 3 buscas diferentes.
    3. Sempre priorizar fontes credíveis e mencionar ou vincular a elas quando apropriado.

    Formato de saída:
    - Dar apenas a resposta final, sem outro texto como "Vou pesquisar x, aqui está o que encontrei...".
    - Começar com um resumo executivo breve (2-4 pontos).
    - Depois fornecer uma explicação estruturada com títulos claros e parágrafos curtos.
    - Evitar jargão desnecessário. Explicar quaisquer termos técnicos em linguagem simples.
    - Sinalizar explicitamente incerteza, desacordos entre fontes ou dados faltando.
    - Mencionar fontes por nome (ou link) quando apropriado, em vez de dizer "uma fonte".
    """)

# ============================================================================
# Criar o Agente
# ============================================================================
reasoning_research_agent = Agent(
    name="Reasoning Research Agent",
    role="Assist with research and information synthesis",
    model=Claude(id="claude-sonnet-4-5"),
    tools=[
        ReasoningTools(add_instructions=True),
        ParallelTools(enable_search=True, enable_extract=True),
    ],
    instructions=instructions,
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    markdown=True,
    db=demo_db,
)
