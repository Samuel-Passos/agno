"""Exemplo: Agente Resumidor e Visualizador de Reuniões

Este script usa OpenAITools (transcribe_audio, generate_image, generate_speech)
para processar uma gravação de reunião, resumi-la, visualizá-la e criar um resumo de áudio.

Requer: pip install openai agno
"""

import base64
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.openai import OpenAITools
from agno.tools.reasoning import ReasoningTools
from agno.utils.media import download_file, save_base64_data

input_audio_url: str = (
    "https://agno-public.s3.us-east-1.amazonaws.com/demo_data/sample_audio.mp3"
)

local_audio_path = Path("tmp/meeting_recording.mp3")
print(f"Baixando arquivo para o caminho local: {local_audio_path}")
download_file(input_audio_url, local_audio_path)

meeting_agent: Agent = Agent(
    model=Gemini(id="gemini-2.0-flash"),
    tools=[OpenAITools(), ReasoningTools()],
    description=dedent("""\
        Você é uma IA Assistente de Reuniões eficiente.
        Seu propósito é processar gravações de áudio de reuniões, extrair informações-chave,
        criar uma representação visual e fornecer um resumo de áudio.
    """),
    instructions=dedent("""\
        Siga estes passos precisamente:
        1. Receber o caminho para um arquivo de áudio.
        2. Usar a ferramenta `transcribe_audio` para obter a transcrição de texto.
        3. Analisar a transcrição e escrever um resumo conciso destacando pontos-chave de discussão, decisões e itens de ação.
        4. Com base *apenas* no resumo criado na etapa 3, gerar pontos importantes da reunião. Isso deve ser essencialmente uma visão geral do conteúdo do resumo adequadamente ordenado e formatado na forma de atas de reunião.
        5. Converter as atas de reunião em um resumo de áudio usando a ferramenta `generate_speech`.
    """),
    markdown=True,
)

response = meeting_agent.run(
    f"Please process the meeting recording located at '{local_audio_path}'"
)
if response.audio:
    base64_audio = base64.b64encode(response.audio[0].content).decode("utf-8")
    save_base64_data(base64_audio, Path("tmp/meeting_summary.mp3"))
    print(f"Resumo da reunião salvo em: {Path('tmp/meeting_summary.mp3')}")
