from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.mistral import MistralChat
from agno.models.openai import OpenAIChat
from agno.team.team import Team

japanese_agent = Agent(
    name="Japanese Agent",
    role="Você só responde em japonês",
    model=DeepSeek(id="deepseek-chat"),
)
chinese_agent = Agent(
    name="Chinese Agent",
    role="Você só responde em chinês",
    model=DeepSeek(id="deepseek-chat"),
)
spanish_agent = Agent(
    name="Spanish Agent",
    role="Você só responde em espanhol",
    model=OpenAIChat(id="gpt-4o"),
)
french_agent = Agent(
    name="French Agent",
    role="Você só responde em francês",
    model=MistralChat(id="mistral-large-latest"),
)
german_agent = Agent(
    name="German Agent",
    role="Você só responde em alemão",
    model=Claude("claude-3-5-sonnet-20241022"),
)

multi_language_team = Team(
    name="Multi Language Team",
    respond_directly=True,
    determine_input_for_members=False,
    model=OpenAIChat("gpt-4o"),
    members=[
        spanish_agent,
        japanese_agent,
        french_agent,
        german_agent,
        chinese_agent,
    ],
    description="Você é um roteador de idiomas que direciona perguntas para o agente de idioma apropriado.",
    instructions=[
        "Identificar o idioma da pergunta do usuário e direcioná-la para o agente de idioma apropriado.",
        "Deixar o agente de idioma responder a pergunta no idioma da pergunta do usuário.",
        "Se o usuário fizer uma pergunta em inglês, responder diretamente em inglês com:",
        "Se o usuário perguntar em um idioma que não é inglês ou você não tiver um agente membro para esse idioma, responder em inglês com:",
        "'I only answer in the following languages: English, Spanish, Japanese, Chinese, French and German. Please ask your question in one of these languages.'",
        "Sempre verificar o idioma da entrada do usuário antes de rotear para um agente.",
        "Para idiomas não suportados como italiano, responder em inglês com a mensagem acima.",
    ],
    markdown=True,
    show_members_responses=True,
)

if __name__ == "__main__":
    # Perguntar "Como você está?" em todos os idiomas suportados
    multi_language_team.print_response("Comment allez-vous?", stream=True)  # French
    multi_language_team.print_response("How are you?", stream=True)  # English
    multi_language_team.print_response("你好吗？", stream=True)  # Chinese
    multi_language_team.print_response("お元気ですか?", stream=True)  # Japanese
    multi_language_team.print_response("Wie geht es Ihnen?", stream=True)  # German
    multi_language_team.print_response("Hola, ¿cómo estás?", stream=True)  # Spanish
    multi_language_team.print_response("Come stai?", stream=True)  # Italian
