import base64
from textwrap import dedent

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.cartesia import CartesiaTools
from agno.utils.media import save_base64_data

agent_instructions = dedent(
    """Siga estes passos SEQUENCIALMENTE para traduzir texto e gerar uma nota de voz localizada:
    1. Identificar o texto a traduzir e o idioma de destino da solicitação do usuário.
    2. Traduzir o texto com precisão para o idioma de destino. Manter este texto traduzido para a etapa final de geração de áudio.
    3. Analisar a emoção transmitida pelo texto *traduzido* (por exemplo, neutro, feliz, triste, irritado, etc.).
    4. Determinar o código de idioma padrão de 2 letras para o idioma de destino (por exemplo, 'fr' para francês, 'es' para espanhol).
    5. Chamar a ferramenta 'list_voices' para obter uma lista de vozes Cartesia disponíveis. Aguardar o resultado.
    6. Examinar a lista de vozes do resultado de 'list_voices'. Selecionar o 'id' de uma voz *existente* que:
       a) Corresponda ao código de idioma de destino (da etapa 4).
       b) Reflita melhor a emoção analisada (da etapa 3).
    7. Chamar a ferramenta 'localize_voice' para criar uma nova voz. Fornecer os seguintes argumentos:
       - 'voice_id': O 'base_voice_id' selecionado na etapa 6.
       - 'name': Um nome adequado para a nova voz (por exemplo, "French Happy Female").
       - 'description': Uma descrição refletindo o idioma e a emoção.
       - 'language': O código de idioma de destino (da etapa 4).
       - 'original_speaker_gender': Gênero especificado pelo usuário ou o gênero da voz base selecionada.
       Aguardar o resultado desta chamada de ferramenta.
    8. Verificar o resultado da chamada da ferramenta 'localize_voice' da etapa 8:
       a) Se a chamada foi bem-sucedida e retornou os detalhes da voz recém-criada, extrair o 'id' desta voz **nova**. Este é o 'final_voice_id'.
    9. Chamar a ferramenta 'text_to_speech' para gerar o áudio. Fornecer:
        - 'transcript': O texto traduzido da etapa 2.
        - 'voice_id': O 'final_voice_id' determinado na etapa 9.
    """
)

agent = Agent(
    name="Emotion-Aware Translator Agent",
    description="Traduz texto, analisa emoção, seleciona uma voz adequada, cria uma voz localizada e gera uma nota de voz (arquivo de áudio) usando ferramentas TTS do Cartesia.",
    instructions=agent_instructions,
    model=Gemini(id="gemini-2.5-pro"),
    tools=[CartesiaTools()],
)

response = agent.run(
    "Convert this phrase 'hello! how are you? Tell me more about the weather in Paris?' to French and create a voice note"
)

print("\nVerificando Artefatos de Áudio no Agente...")
if response.audio:
    base64_audio = base64.b64encode(response.audio[0].content).decode("utf-8")
    save_base64_data(base64_data=base64_audio, output_path="tmp/greeting.mp3")
    print("Áudio salvo em tmp/greeting.mp3")
