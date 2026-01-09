from textwrap import dedent

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.youtube import YouTubeTools
from db import demo_db

# ============================================================================
# Descrição e Instruções
# ============================================================================
description = dedent("""\
    Você é o Agente YouTube — um Agente de IA que analisa vídeos do YouTube
    e responde perguntas sobre seu conteúdo com precisão e clareza.
    """)
instructions = dedent("""
    1. Quando receber uma URL do YouTube, usar as ferramentas `get_youtube_video_data` e `get_youtube_video_captions`
       para recuperar informações do vídeo e legendas.
    2. Usar esses dados para responder à pergunta do usuário de forma clara e concisa.
    3. Se a resposta não estiver no vídeo, dizer isso e pedir mais detalhes.
    4. Manter respostas curtas, envolventes e focadas em insights-chave.
    """)

# ============================================================================
# Criar o Agente
# ============================================================================
youtube_agent = Agent(
    name="YouTube Agent",
    model=Claude(id="claude-sonnet-4-5"),
    tools=[YouTubeTools()],
    description=description,
    instructions=instructions,
    add_history_to_context=True,
    add_datetime_to_context=True,
    markdown=True,
    db=demo_db,
)
