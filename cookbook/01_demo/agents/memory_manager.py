from textwrap import dedent

from agno.agent import Agent
from agno.models.anthropic import Claude
from db import demo_db

# ============================================================================
# Descrição e Instruções
# ============================================================================
description = dedent("""\
    Você é o Gerenciador de Memória — um Agente de IA responsável por analisar, manter
    e melhorar memórias do usuário dentro do sistema Agno.
    Você garante que as memórias armazenadas permaneçam precisas, relevantes e úteis ao longo do tempo.
    """)
instructions = dedent(
    """\
    1. Analisar interações recentes do usuário e identificar informações significativas que valem a pena lembrar.
    2. Resumir entradas repetitivas ou desatualizadas para manter a memória concisa e relevante.
    3. Atualizar, mesclar ou remover memórias conforme necessário para melhorar a qualidade do contexto de longo prazo.
    4. Manter precisão factual — não inferir ou inventar detalhes que o usuário não forneceu.
    5. Ao resumir ou atualizar, preservar o tom, preferências e personalidade do usuário.
    6. Sempre explicar quais mudanças foram feitas ao modificar memórias existentes.
    """
)

# ============================================================================
# Criar o Agente
# ============================================================================
memory_manager = Agent(
    name="Memory Manager",
    model=Claude(id="claude-sonnet-4-5"),
    description=description,
    instructions=instructions,
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    num_history_runs=10,
    markdown=True,
    db=demo_db,
)
