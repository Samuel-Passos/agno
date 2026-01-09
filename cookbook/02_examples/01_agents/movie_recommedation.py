"""🎬 Movie Recommendation Agent - Seu Curador de Cinema Pessoal!

Este exemplo mostra como criar um sistema inteligente de recomendação de filmes que fornece
sugestões abrangentes de filmes com base em suas preferências. O agente combina bancos de dados de filmes,
avaliações, resenhas e lançamentos futuros para entregar recomendações de filmes personalizadas.

Exemplos de prompts para tentar:
- "Suggest thriller movies similar to Inception and Shutter Island"
- "What are the top-rated comedy movies from the last 2 years?"
- "Find me Korean movies similar to Parasite and Oldboy"
- "Recommend family-friendly adventure movies with good ratings"
- "What are the upcoming superhero movies in the next 6 months?"

Execute: `pip install openai exa_py agno` para instalar as dependências
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

movie_recommendation_agent = Agent(
    name="PopcornPal",
    tools=[ExaTools()],
    model=OpenAIChat(id="gpt-4o"),
    description=dedent("""\
        Você é PopcornPal, um curador de filmes apaixonado e conhecedor com expertise em cinema mundial! 🎥

        Sua missão é ajudar usuários a descobrir seus próximos filmes favoritos fornecendo recomendações
        detalhadas e personalizadas com base em suas preferências, histórico de visualização e o que há de mais recente
        no cinema. Você combina conhecimento profundo de filmes com avaliações e resenhas atuais para sugerir
        filmes que realmente ressoarão com cada espectador."""),
    instructions=dedent("""\
        Abordar cada recomendação com estes passos:
        1. Fase de Análise
           - Entender preferências do usuário a partir de sua entrada
           - Considerar temas e estilos dos filmes favoritos mencionados
           - Considerar quaisquer requisitos específicos (gênero, classificação, idioma)

        2. Buscar e Curadoria
           - Usar Exa para buscar filmes relevantes
           - Garantir diversidade nas recomendações
           - Verificar se todos os dados dos filmes estão atuais e precisos

        3. Informações Detalhadas
           - Título do filme e ano de lançamento
           - Gênero e subgêneros
           - Avaliação IMDB (focar em filmes com 7.5+ de classificação)
           - Duração e idioma principal
           - Resumo do enredo breve e envolvente
           - Aviso de conteúdo/classificação etária
           - Elenco e diretor notáveis

        4. Recursos Extras
           - Incluir trailers relevantes quando disponíveis
           - Sugerir lançamentos futuros em gêneros similares
           - Mencionar disponibilidade de streaming quando conhecida

        Estilo de Apresentação:
        - Usar formatação markdown clara
        - Apresentar recomendações principais em uma tabela estruturada
        - Agrupar filmes similares
        - Adicionar indicadores de emoji para gêneros (🎭 🎬 🎪)
        - Mínimo de 5 recomendações por consulta
        - Incluir uma breve explicação para cada recomendação
    """),
    markdown=True,
    add_datetime_to_context=True,
)

# Exemplo de uso com diferentes tipos de consultas de filmes
movie_recommendation_agent.print_response(
    "Suggest some thriller movies to watch with a rating of 8 or above on IMDB. "
    "My previous favourite thriller movies are The Dark Knight, Venom, Parasite, Shutter Island.",
    stream=True,
)

# Mais exemplos de prompts para explorar:
"""
Consultas específicas de gênero:
1. "Find me psychological thrillers similar to Black Swan and Gone Girl"
2. "What are the best animated movies from Studio Ghibli?"
3. "Recommend some mind-bending sci-fi movies like Inception and Interstellar"
4. "What are the highest-rated crime documentaries from the last 5 years?"

Cinema Internacional:
1. "Suggest Korean movies similar to Parasite and Train to Busan"
2. "What are the must-watch French films from the last decade?"
3. "Recommend Japanese animated movies for adults"
4. "Find me award-winning European drama films"

Família e Assistência em Grupo:
1. "What are good family movies for kids aged 8-12?"
2. "Suggest comedy movies perfect for a group movie night"
3. "Find educational documentaries suitable for teenagers"
4. "Recommend adventure movies that both adults and children would enjoy"

Lançamentos Futuros:
1. "What are the most anticipated movies coming out next month?"
2. "Show me upcoming superhero movie releases"
3. "What horror movies are releasing this Halloween season?"
4. "List upcoming book-to-movie adaptations"
"""
