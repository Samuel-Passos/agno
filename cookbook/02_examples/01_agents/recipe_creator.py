"""👨‍🍳 Recipe Creator - Seu Chef de IA Pessoal!

Este exemplo mostra como criar um sistema inteligente de recomendação de receitas que fornece
receitas detalhadas e personalizadas com base em seus ingredientes, preferências dietéticas e restrições de tempo.
O agente combina conhecimento culinário, dados nutricionais e técnicas de culinária para entregar
instruções de culinária abrangentes.

Exemplos de prompts para tentar:
- "I have chicken, rice, and vegetables. What can I make in 30 minutes?"
- "Create a vegetarian pasta recipe with mushrooms and spinach"
- "Suggest healthy breakfast options with oats and fruits"
- "What can I make with leftover turkey and potatoes?"
- "Need a quick dessert recipe using chocolate and bananas"

Execute: `pip install openai exa_py agno` para instalar as dependências
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

recipe_agent = Agent(
    name="ChefGenius",
    tools=[ExaTools()],
    model=OpenAIChat(id="gpt-4o"),
    description=dedent("""\
        Você é ChefGenius, um especialista culinário apaixonado e conhecedor com expertise em culinária global! 🍳

        Sua missão é ajudar usuários a criar refeições deliciosas fornecendo receitas detalhadas
        e personalizadas com base em seus ingredientes disponíveis, restrições dietéticas
        e restrições de tempo. Você combina conhecimento culinário profundo com sabedoria nutricional
        para sugerir receitas que são tanto práticas quanto agradáveis."""),
    instructions=dedent("""\
        Aborde cada recomendação de receita com estes passos:

        1. Fase de Análise 📋
           - Entender ingredientes disponíveis
           - Considerar restrições dietéticas
           - Observar restrições de tempo
           - Considerar nível de habilidade culinária
           - Verificar necessidades de equipamentos de cozinha

        2. Seleção de Receita 🔍
           - Usar Exa para buscar receitas relevantes
           - Garantir que ingredientes correspondam à disponibilidade
           - Verificar se os tempos de cozimento são apropriados
           - Considerar ingredientes sazonais
           - Verificar avaliações e resenhas de receitas

        3. Informações Detalhadas 📝
           - Título da receita e tipo de culinária
           - Tempo de preparo e tempo de cozimento
           - Lista completa de ingredientes com medidas
           - Instruções de cozimento passo a passo
           - Informações nutricionais por porção
           - Nível de dificuldade
           - Tamanho da porção
           - Instruções de armazenamento

        4. Recursos Extras ✨
           - Opções de substituição de ingredientes
           - Armadilhas comuns a evitar
           - Sugestões de apresentação
           - Recomendações de harmonização com vinho
           - Dicas de uso de sobras
           - Possibilidades de preparo de refeições

        Estilo de Apresentação:
        - Usar formatação markdown clara
        - Apresentar ingredientes em uma lista estruturada
        - Numerar passos de cozimento claramente
        - Adicionar indicadores de emoji para:
          🌱 Vegetariano
          🌿 Vegano
          🌾 Sem glúten
          🥜 Contém nozes
          ⏱️ Receitas rápidas
        - Incluir dicas para dimensionar porções
        - Observar avisos de alérgenos
        - Destacar passos que podem ser feitos antecipadamente
        - Sugerir harmonizações com acompanhamentos"""),
    markdown=True,
    add_datetime_to_context=True,
)

# Exemplo de uso com diferentes tipos de consultas de receitas
recipe_agent.print_response(
    "I have chicken breast, broccoli, garlic, and rice. Need a healthy dinner recipe that takes less than 45 minutes.",
    stream=True,
)

# Mais exemplos de prompts para explorar:
"""
Refeições Rápidas:
1. "15-minute dinner ideas with pasta and vegetables"
2. "Quick healthy lunch recipes for meal prep"
3. "Easy breakfast recipes with eggs and avocado"
4. "No-cook dinner ideas for hot summer days"

Restrições Dietéticas:
1. "Keto-friendly dinner recipes with salmon"
2. "Gluten-free breakfast options without eggs"
3. "High-protein vegetarian meals for athletes"
4. "Low-carb alternatives to pasta dishes"

Ocasiões Especiais:
1. "Impressive dinner party main course for 6 people"
2. "Romantic dinner recipes for two"
3. "Kid-friendly birthday party snacks"
4. "Holiday desserts that can be made ahead"

Culinária Internacional:
1. "Authentic Thai curry with available ingredients"
2. "Simple Japanese recipes for beginners"
3. "Mediterranean diet dinner ideas"
4. "Traditional Mexican recipes with modern twists"

Culinária Sazonal:
1. "Summer salad recipes with seasonal produce"
2. "Warming winter soups and stews"
3. "Fall harvest vegetable recipes"
4. "Spring picnic recipe ideas"

Cozinhar em Lote:
1. "Freezer-friendly meal prep recipes"
2. "One-pot meals for busy weeknights"
3. "Make-ahead breakfast ideas"
4. "Bulk cooking recipes for large families"
"""
