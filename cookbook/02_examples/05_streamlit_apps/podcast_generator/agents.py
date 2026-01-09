import os
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.utils.audio import write_audio_to_file
from agno.utils.streamlit import get_model_with_provider

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"


def generate_podcast_agent(
    model_id: str = "openai:gpt-4o",
    voice: str = "alloy",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Agent:
    """Criar um Agente Gerador de Podcast"""

    os.makedirs("tmp", exist_ok=True)

    model = get_model_with_provider(model_id)

    # Se usar OpenAI, configurar para saída de áudio
    if model_id.startswith("openai:"):
        model = OpenAIChat(
            id=model_id.split("openai:")[1],
            modalities=["text", "audio"],
            audio={"voice": voice, "format": "wav"},
        )

    db = PostgresDb(
        db_url=db_url,
        session_table="sessions",
        db_schema="ai",
    )

    agent = Agent(
        name="Podcast Generator",
        model=model,
        db=db,
        id="podcast-generator",
        user_id=user_id,
        session_id=session_id,
        tools=[DuckDuckGoTools()],
        instructions=dedent("""
            Você é um roteirista de podcast especializado em narrativas concisas e envolventes.
            Sua tarefa é pesquisar um tópico fornecido e compor um roteiro de podcast convincente.

            ### Fase de Pesquisa:
            - Usar DuckDuckGo para reunir as informações mais recentes e relevantes sobre o tópico fornecido
            - Priorizar fontes confiáveis como sites de notícias, artigos acadêmicos ou publicações estabelecidas
            - Identificar pontos-chave, estatísticas, opiniões de especialistas e fatos interessantes

            ### Fase de Roteiro:
            - Escrever um roteiro de podcast conciso em tom conversacional
            - Começar com um gancho forte para capturar a atenção do ouvinte
            - Apresentar insights-chave de forma envolvente e fácil de seguir
            - Incluir transições suaves entre ideias para manter o fluxo narrativo
            - Terminar com uma observação de fechamento que resuma as principais conclusões

            ### Diretrizes de Formatação:
            - Usar linguagem simples e envolvente adequada para áudio
            - Manter o roteiro abaixo de 300 palavras (cerca de 2 minutos de áudio)
            - Escrever em formato natural e falado, evitando jargão excessivamente formal ou técnico
            - Estrutura: gancho introdutório → conteúdo principal → conclusão
            - Sem formatação especial ou markdown - apenas texto conversacional simples

            ### Estrutura de Saída de Exemplo:
            "Bem-vindo ao episódio de hoje onde exploramos [TÓPICO]. [Gancho ou fato interessante]
            
            [Conteúdo principal com 2-3 pontos-chave, transições suaves entre ideias]
            
            [Conclusão com principais conclusões e pensamentos finais]
            
            Obrigado por ouvir, e nos vemos na próxima vez!"
        """),
        markdown=True,
        debug_mode=True,
    )

    return agent


def generate_podcast(
    topic: str, voice: str = "alloy", model_id: str = "openai:gpt-4o"
) -> Optional[str]:
    """
    Gerar um roteiro de podcast e convertê-lo em áudio.

    Args:
        topic (str): O tópico do podcast
        voice (str): Modelo de voz para OpenAI TTS. Opções: ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        model_id (str): Modelo a usar para geração de roteiro

    Returns:
        str: Caminho para o arquivo de áudio gerado, ou None se a geração falhou
    """
    try:
        # Criar o agente gerador de podcast
        agent = generate_podcast_agent(model_id=model_id, voice=voice)

        # Gerar o roteiro do podcast
        response = agent.run(f"Escrever um roteiro de podcast para o tópico: {topic}")

        audio_file_path = "tmp/generated_podcast.wav"

        # Se o modelo suporta saída de áudio e áudio foi gerado
        if hasattr(response, "response_audio") and response.response_audio is not None:
            audio_content = response.response_audio.content

            if audio_content:
                write_audio_to_file(
                    audio=audio_content,
                    filename=audio_file_path,
                )
                return audio_file_path

        return None

    except Exception as e:
        print(f"Erro ao gerar podcast: {e}")
        return None
