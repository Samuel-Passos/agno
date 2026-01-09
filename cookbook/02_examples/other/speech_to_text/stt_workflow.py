"""
Este cookbook demonstra como usar um Workflow Agno com AgentOS para transcrever arquivos de áudio. Há quatro passos no workflow:
1. Ecoar o arquivo de entrada
2. Obter o conteúdo de áudio
3. Transcrever o conteúdo de áudio
4. Converter a transcrição para saída estruturada
"""

import io
from textwrap import dedent
from typing import Optional

import httpx
import requests
from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.media import Audio
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.utils.log import log_error, log_info
from agno.workflow import Step, Workflow
from agno.workflow.types import StepInput, StepOutput
from pydantic import BaseModel, Field
from pydub import AudioSegment

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

db = PostgresDb(
    db_url=db_url,
    db_schema="ai",
    session_table="invoice_processing_sessions",
)


class Transcription(BaseModel):
    transcript: list[str] = Field(
        ...,
        description="A transcrição da conversa de áudio. Formatada como uma lista de strings com rótulos de falantes e parágrafos lógicos e quebras de linha.",
    )
    description: str = Field(..., description="Uma descrição da conversa de áudio")
    speakers: list[str] = Field(
        ..., description="Os falantes na conversa de áudio"
    )


def get_transcription_agent(additional_instructions: Optional[str] = None):
    transcription_agent = Agent(
        model=Gemini(id="gemini-3-flash-preview"),
        markdown=True,
        description="Agente de transcrição de arquivo de áudio",
        instructions=dedent(f"""Sua tarefa é transcrever com precisão o áudio em texto. Você receberá um arquivo de áudio e precisa transcrevê-lo em texto. 
            Na transcrição, certifique-se de identificar os falantes. Se um nome for mencionado, usar o nome na transcrição. Se um nome não for mencionado, usar um placeholder como 'Falante 1', 'Falante 2', etc.
            Certificar-se de incluir todo o conteúdo do áudio na transcrição.
            Para qualquer áudio que não seja fala, usar o placeholder 'ruído de fundo' ou 'silêncio' ou 'música' ou 'outro'.
            Apenas retornar a transcrição, nenhum outro texto ou formatação.
            {additional_instructions if additional_instructions else ""}"""),
    )
    return transcription_agent


class TranscriptionRequest(BaseModel):
    audio_file: str = (
        "https://agno-public.s3.us-east-1.amazonaws.com/demo_data/sample_audio.wav"
    )
    model_id: str = "gpt-audio-2025-08-28"
    additional_instructions: Optional[str] = None


def echo_input_file(step_input: StepInput) -> StepOutput:
    request = step_input.input
    log_info(f"Echoing input file: {request.audio_file}")
    return StepOutput(
        content={
            "file_link": request.audio_file,
            "model_id": request.model_id,
        },
        success=True,
    )


# TODO: Encontrar uma maneira mais limpa de criar arquivos wav
def get_audio_content(step_input: StepInput, session_state) -> StepOutput:
    request = step_input.input
    url = request.audio_file
    if url.endswith(".wav"):
        response = httpx.get(url)
        response.raise_for_status()
        wav_data = response.content
        session_state["audio_content"] = wav_data
        return StepOutput(
            success=True,
        )
    elif url.endswith(".mp3"):
        response = requests.get(url)
        response.raise_for_status()
        mp3_audio = io.BytesIO(response.content)
        audio_segment = AudioSegment.from_file(mp3_audio, format="mp3")
        # Garantir mono e taxa de amostragem padrão para compatibilidade com OpenAI
        if audio_segment.channels > 1:
            audio_segment = audio_segment.set_channels(1)
        if audio_segment.frame_rate != 16000:
            audio_segment = audio_segment.set_frame_rate(16000)
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)  # Redefinir para o início antes de ler
        audio_content = wav_io.read()
        session_state["audio_content"] = audio_content
        return StepOutput(success=True)
    else:
        log_error(f"Tipo de arquivo não suportado: {url}")
        return StepOutput(success=False)


async def transcription_agent_executor(
    step_input: StepInput, session_state
) -> StepOutput:
    audio_content = session_state["audio_content"]
    transcription_agent = get_transcription_agent(
        additional_instructions=step_input.input.additional_instructions
    )
    response = await transcription_agent.arun(
        input="Fornecer uma transcrição da conversa de áudio",
        audio=[Audio(content=audio_content, format="wav")],
    )
    print(response.content)
    session_state["transcription"] = response.content
    return StepOutput(
        success=True,
    )


async def convert_transcription_to_output(
    step_input: StepInput, session_state
) -> StepOutput:
    transcription = session_state["transcription"]
    agent = Agent(
        model=OpenAIChat(id="gpt-5-mini"),
        instructions="""Você é um assistente útil que converte uma transcrição de uma conversa de áudio em uma saída estruturada.""",
        output_schema=Transcription,
    )

    response = await agent.arun(input=transcription)

    return StepOutput(content=response.content, success=True)


# Definir passos do workflow
echo_input_step = Step(name="Echo Input", executor=echo_input_file)
get_audio_content_step = Step(name="Get Audio Content", executor=get_audio_content)
transcription_step = Step(name="Transcription", executor=transcription_agent_executor)
conversion_step = Step(name="Conversion", executor=convert_transcription_to_output)

# Definição do workflow
speech_to_text_workflow = Workflow(
    name="Speech to text workflow",
    description="""
        Transcrever arquivo de áudio usando agente de transcrição
        """,
    input_schema=TranscriptionRequest,
    steps=[
        echo_input_step,
        get_audio_content_step,
        transcription_step,
        conversion_step,
    ],
    db=db,
)


agent_os = AgentOS(
    workflows=[speech_to_text_workflow],
)

app = agent_os.get_app()
if __name__ == "__main__":
    # Serve um aplicativo FastAPI exposto pelo AgentOS. Usar reload=True para desenvolvimento local.
    agent_os.serve(app="stt_workflow:app", reload=True)
