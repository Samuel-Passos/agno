"""
Exemplo de fala para texto usando Gemini. Este cookbook demonstra como transcrever arquivos de áudio usando Gemini e obter saída estruturada.
"""

import httpx
from agno.agent import Agent, RunOutput  # noqa
from agno.media import Audio
from agno.models.google import Gemini
from pydantic import BaseModel, Field

INSTRUCTIONS = """
Transcrever o áudio com precisão e completamente.

Identificação de falante:
- Usar o nome do falante se mencionado na conversa
- Caso contrário, usar 'Falante 1', 'Falante 2', etc. consistentemente

Áudio não-fala:
- Notar elementos não-fala significativos (ex: [pausa longa], [música], [ruído de fundo]) apenas quando relevantes para entender a conversa
- Ignorar pausas naturais breves

Incluir tudo que foi falado, mesmo falsos começos e palavras de preenchimento (um, uh, etc.).
"""


class Utterance(BaseModel):
    speaker: str = Field(..., description="Nome ou identificador do falante")
    text: str = Field(..., description="O que foi dito pelo falante")


class Transcription(BaseModel):
    description: str = Field(..., description="Uma descrição da conversa de áudio")
    utterances: list[Utterance] = Field(
        ..., description="Lista sequencial de enunciados na ordem da conversa"
    )


# Buscar o arquivo de áudio e convertê-lo para uma string codificada em base64
# Arquivo de áudio simples com um único falante
# url = "https://openaiassets.blob.core.windows.net/$web/API/docs/audio/alloy.wav"
# Arquivo de áudio com múltiplos falantes
url = "https://agno-public.s3.us-east-1.amazonaws.com/demo_data/sample_audio.wav"

try:
    response = httpx.get(url)
    response.raise_for_status()
    wav_data = response.content
except httpx.HTTPStatusError as e:
    raise ValueError(f"Erro ao buscar arquivo de áudio: {url}") from e

# Fornecer o arquivo de áudio ao agente e obter resultado como texto
agent = Agent(
    model=Gemini(id="gemini-3-flash-preview"),
    markdown=True,
    instructions=INSTRUCTIONS,
    output_schema=Transcription,
)

agent.print_response(
    "Fornecer uma transcrição da conversa de áudio",
    audio=[Audio(content=wav_data)],
)
