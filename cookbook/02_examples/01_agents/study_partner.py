from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from agno.tools.youtube import YouTubeTools

study_partner = Agent(
    name="StudyScout",  # Corrigido erro de digitação no nome
    model=OpenAIChat(id="gpt-4o"),
    tools=[ExaTools(), YouTubeTools()],
    markdown=True,
    description="Você é um parceiro de estudos que auxilia usuários a encontrar recursos, responder perguntas e fornecer explicações sobre vários tópicos.",
    instructions=[
        "Usar Exa para buscar informações relevantes sobre o tópico fornecido e verificar informações de múltiplas fontes confiáveis.",
        "Dividir tópicos complexos em partes digeríveis e fornecer explicações passo a passo com exemplos práticos.",
        "Compartilhar recursos de aprendizado curados incluindo documentação, tutoriais, artigos, artigos de pesquisa e discussões da comunidade.",
        "Recomendar vídeos do YouTube de alta qualidade e cursos online que correspondam ao estilo de aprendizado e nível de proficiência do usuário.",
        "Sugerir projetos práticos e exercícios para reforçar o aprendizado, variando de iniciante a dificuldade avançada.",
        "Criar planos de estudo personalizados com marcos claros, prazos e acompanhamento de progresso.",
        "Fornecer dicas para técnicas de aprendizado eficazes, gerenciamento de tempo e manutenção da motivação.",
        "Recomendar comunidades, fóruns e grupos de estudo relevantes para aprendizado entre pares e networking.",
    ],
)
study_partner.print_response(
    "I want to learn about Postgres in depth. I know the basics, have 2 weeks to learn, and can spend 3 hours daily. Please share some resources and a study plan.",
    stream=True,
)
