from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.models.mistral.mistral import MistralChat
from agno.models.openai import OpenAIChat
from agno.team.team import Team

english_agent = Agent(
    name="English Agent",
    role="Você só responde em inglês",
    model=OpenAIChat(id="gpt-4o"),
)
chinese_agent = Agent(
    name="Chinese Agent",
    role="Você só responde em chinês",
    model=DeepSeek(id="deepseek-chat"),
)
french_agent = Agent(
    name="French Agent",
    role="Você só pode responder em francês",
    model=MistralChat(id="mistral-large-latest"),
)

multi_language_team = Team(
    name="Multi Language Team",
    model=OpenAIChat("gpt-4o"),
    members=[english_agent, chinese_agent, french_agent],
    markdown=True,
    description="Você é um roteador de idiomas que direciona perguntas para o agente de idioma apropriado.",
    instructions=[
        "Identificar o idioma da pergunta do usuário e direcioná-la para o agente de idioma apropriado.",
        "Deixar o agente de idioma responder a pergunta no idioma da pergunta do usuário.",
        "Se o usuário perguntar em um idioma cujo agente não é membro da equipe, responder em inglês com:",
        "'I can only answer in the following languages: English, Chinese, French. Please ask your question in one of these languages.'",
        "Sempre verificar o idioma da entrada do usuário antes de rotear para um agente.",
        "Para idiomas não suportados como italiano, responder em inglês com a mensagem acima.",
    ],
    respond_directly=True,
    determine_input_for_members=False,
    show_members_responses=True,
)


if __name__ == "__main__":
    # Perguntar "Como você está?" em todos os idiomas suportados
    multi_language_team.print_response("Comment allez-vous?", stream=True)  # French
    multi_language_team.print_response("How are you?", stream=True)  # English
    multi_language_team.print_response("你好吗？", stream=True)  # Chinese
    multi_language_team.print_response("Come stai?", stream=True)  # Italian

    multi_language_team.print_response("What are you capable of?", stream=True)
    multi_language_team.print_response("Tell me about the history of AI?", stream=True)
