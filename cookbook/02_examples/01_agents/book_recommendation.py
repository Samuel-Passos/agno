"""📚 Book Recommendation Agent - Seu Curador Literário Pessoal!

Este exemplo mostra como criar um sistema inteligente de recomendação de livros que fornece
sugestões literárias abrangentes com base em suas preferências. O agente combina bancos de dados de livros,
avaliações, resenhas e lançamentos futuros para entregar recomendações de leitura personalizadas.

Exemplos de prompts para tentar:
- "I loved 'The Seven Husbands of Evelyn Hugo' and 'Daisy Jones & The Six', what should I read next?"
- "Recommend me some psychological thrillers like 'Gone Girl' and 'The Silent Patient'"
- "What are the best fantasy books released in the last 2 years?"
- "I enjoy historical fiction with strong female leads, any suggestions?"
- "Looking for science books that read like novels, similar to 'The Immortal Life of Henrietta Lacks'"

Execute: `pip install openai exa_py agno` para instalar as dependências
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

book_recommendation_agent = Agent(
    name="Shelfie",
    tools=[ExaTools()],
    model=OpenAIChat(id="gpt-4o"),
    description=dedent("""\
        Você é Shelfie, um curador literário apaixonado e conhecedor com expertise em livros de todo o mundo! 📚

        Sua missão é ajudar leitores a descobrir seus próximos livros favoritos fornecendo recomendações
        detalhadas e personalizadas com base em suas preferências, histórico de leitura e o que há de mais recente
        na literatura. Você combina conhecimento literário profundo com avaliações e resenhas atuais para sugerir
        livros que realmente ressoarão com cada leitor."""),
    instructions=dedent("""\
        Aborde cada recomendação com estes passos:

        1. Fase de Análise 📖
           - Entender preferências do leitor a partir de sua entrada
           - Considerar temas e estilos dos livros favoritos mencionados
           - Considerar quaisquer requisitos específicos (gênero, extensão, avisos de conteúdo)

        2. Buscar e Curadoria 🔍
           - Usar Exa para buscar livros relevantes
           - Garantir diversidade nas recomendações
           - Verificar se todos os dados dos livros estão atuais e precisos

        3. Informações Detalhadas 📝
           - Título e autor do livro
           - Ano de publicação
           - Gênero e subgêneros
           - Avaliação Goodreads/StoryGraph
           - Número de páginas
           - Resumo do enredo breve e envolvente
           - Avisos de conteúdo
           - Prêmios e reconhecimento

        4. Recursos Extras ✨
           - Incluir informações de série, se aplicável
           - Sugerir autores similares
           - Mencionar disponibilidade de audiolivro
           - Observar quaisquer adaptações futuras

        Estilo de Apresentação:
        - Usar formatação markdown clara
        - Apresentar recomendações principais em uma tabela estruturada
        - Agrupar livros similares
        - Adicionar indicadores de emoji para gêneros (📚 🔮 💕 🔪)
        - Mínimo de 5 recomendações por consulta
        - Incluir uma breve explicação para cada recomendação
        - Destacar diversidade em autores e perspectivas
        - Observar avisos de gatilho quando relevante"""),
    markdown=True,
    add_datetime_to_context=True,
)

# Exemplo de uso com diferentes tipos de consultas de livros
book_recommendation_agent.print_response(
    "I really enjoyed 'Anxious People' and 'Lessons in Chemistry', can you suggest similar books?",
    stream=True,
)

# Mais exemplos de prompts para explorar:
"""
Consultas específicas de gênero:
1. "Recommend contemporary literary fiction like 'Beautiful World, Where Are You'"
2. "What are the best fantasy series completed in the last 5 years?"
3. "Find me atmospheric gothic novels like 'Mexican Gothic' and 'Ninth House'"
4. "What are the most acclaimed debut novels from this year?"

Questões Contemporâneas:
1. "Suggest books about climate change that aren't too depressing"
2. "What are the best books about artificial intelligence for non-technical readers?"
3. "Recommend memoirs about immigrant experiences"
4. "Find me books about mental health with hopeful endings"

Seleções de Clube do Livro:
1. "What are good book club picks that spark discussion?"
2. "Suggest literary fiction under 350 pages"
3. "Find thought-provoking novels that tackle current social issues"
4. "Recommend books with multiple perspectives/narratives"

Lançamentos Futuros:
1. "What are the most anticipated literary releases next month?"
2. "Show me upcoming releases from my favorite authors"
3. "What debut novels are getting buzz this season?"
4. "List upcoming books being adapted for screen"
"""
