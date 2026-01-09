"""
Exemplo de fala para texto usando OpenAI. Este cookbook demonstra como transcrever arquivos de áudio usando OpenAI e obter transcrição simples.
"""

import httpx
from agno.agent import Agent, RunOutput  # noqa
from agno.media import Audio
from agno.models.openai import OpenAIChat

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
    model=OpenAIChat(id="gpt-audio-2025-08-28", modalities=["text"]),
    markdown=True,
    instructions=INSTRUCTIONS,
)
agent.print_response(
    "O que há neste áudio?", audio=[Audio(content=wav_data, format="wav")]
)
