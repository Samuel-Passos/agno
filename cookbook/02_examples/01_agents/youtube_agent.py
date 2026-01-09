"""🎥 YouTube Agent - Seu Especialista em Conteúdo de Vídeo!

Este exemplo mostra como criar um analisador de conteúdo do YouTube inteligente que fornece
quebras detalhadas de vídeo, timestamps e resumos. Perfeito para criadores de conteúdo,
pesquisadores e espectadores que querem navegar eficientemente pelo conteúdo de vídeo.

Exemplos de prompts para tentar:
- "Analyze this tech review: [video_url]"
- "Get timestamps for this coding tutorial: [video_url]"
- "Break down the key points of this lecture: [video_url]"
- "Summarize the main topics in this documentary: [video_url]"
- "Create a study guide from this educational video: [video_url]"

Execute: `pip install openai youtube_transcript_api agno` para instalar as dependências
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.youtube import YouTubeTools

youtube_agent = Agent(
    name="YouTube Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YouTubeTools()],
    instructions=dedent("""\
        Você é um analista especialista de conteúdo do YouTube com olho afiado para detalhes! 🎓
        Siga estes passos para análise abrangente de vídeo:
        1. Visão Geral do Vídeo
           - Verificar duração do vídeo e metadados básicos
           - Identificar tipo de vídeo (tutorial, review, palestra, etc.)
           - Observar a estrutura do conteúdo
        2. Criação de Timestamps
           - Criar timestamps precisos e significativos
           - Focar em transições principais de tópicos
           - Destacar momentos-chave e demonstrações
           - Formato: [start_time, end_time, detailed_summary]
        3. Organização de Conteúdo
           - Agrupar segmentos relacionados
           - Identificar temas principais
           - Rastrear progressão de tópicos

        Seu estilo de análise:
        - Comece com uma visão geral do vídeo
        - Use títulos de segmentos claros e descritivos
        - Inclua emojis relevantes para tipos de conteúdo:
          📚 Educacional
          💻 Técnico
          🎮 Jogos
          📱 Review de Tecnologia
          🎨 Criativo
        - Destaque pontos-chave de aprendizado
        - Observe demonstrações práticas
        - Marque referências importantes

        Diretrizes de Qualidade:
        - Verificar precisão dos timestamps
        - Evitar alucinação de timestamps
        - Garantir cobertura abrangente
        - Manter nível de detalhe consistente
        - Focar em marcadores de conteúdo valiosos
    """),
    add_datetime_to_context=True,
    markdown=True,
)

# Exemplo de uso com diferentes tipos de vídeos
youtube_agent.print_response(
    "Analyze this video: https://www.youtube.com/watch?v=zjkBMFhNj_g",
    stream=True,
)

# Mais exemplos de prompts para explorar:
"""
Análise de Tutoriais:
1. "Break down this Python tutorial with focus on code examples"
2. "Create a learning path from this web development course"
3. "Extract all practical exercises from this programming guide"
4. "Identify key concepts and implementation examples"

Conteúdo Educacional:
1. "Create a study guide with timestamps for this math lecture"
2. "Extract main theories and examples from this science video"
3. "Break down this historical documentary into key events"
4. "Summarize the main arguments in this academic presentation"

Reviews de Tecnologia:
1. "List all product features mentioned with timestamps"
2. "Compare pros and cons discussed in this review"
3. "Extract technical specifications and benchmarks"
4. "Identify key comparison points and conclusions"

Conteúdo Criativo:
1. "Break down the techniques shown in this art tutorial"
2. "Create a timeline of project steps in this DIY video"
3. "List all tools and materials mentioned with timestamps"
4. "Extract tips and tricks with their demonstrations"
"""
