from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.google.gemini import Gemini
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.calculator import CalculatorTools
from agno.tools.dalle import DalleTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.e2b import E2BTools
from agno.tools.yfinance import YFinanceTools

web_agent = Agent(
    name="Web Agent",
    role="Buscar informações na web",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions=["Sempre incluir fontes"],
)

finance_agent = Agent(
    name="Finance Agent",
    role="Obter dados financeiros",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools()],
    instructions=["Usar tabelas para exibir dados"],
)

image_agent = Agent(
    name="Image Agent",
    role="Analisar ou gerar imagens",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DalleTools()],
    description="Você é um agente de IA que pode analisar imagens ou criar imagens usando DALL-E.",
    instructions=[
        "Quando o usuário perguntar sobre uma imagem, fazer seu melhor esforço para analisar a imagem e retornar uma descrição da imagem.",
        "Quando o usuário pedir para criar uma imagem, usar a ferramenta DALL-E para criar uma imagem.",
        "A ferramenta DALL-E retornará uma URL de imagem.",
        "Retornar a URL da imagem em sua resposta no seguinte formato: `![image description](image URL)`",
    ],
)

file_analysis_agent = Agent(
    name="File Analysis Agent",
    role="Analisar arquivos",
    model=Claude(id="claude-3-7-sonnet-latest"),
    description="Você é um agente de IA que pode analisar arquivos.",
    instructions=[
        "Você é um agente de IA que pode analisar arquivos.",
        "Você recebe um arquivo e precisa responder perguntas sobre o arquivo.",
    ],
)

writer_agent = Agent(
    name="Write Agent",
    role="Escrever conteúdo",
    model=OpenAIChat(id="gpt-4o"),
    description="Você é um agente de IA que pode escrever conteúdo.",
    instructions=[
        "Você é um escritor versátil que pode criar conteúdo sobre qualquer tópico.",
        "Quando receber um tópico, escrever conteúdo envolvente e informativo no formato e estilo solicitados.",
        "Se receber expressões matemáticas ou cálculos do agente calculadora, convertê-los em texto escrito claro.",
        "Garantir que sua escrita seja clara, precisa e adaptada à solicitação específica.",
        "Manter um tom natural e envolvente enquanto é factualmente preciso.",
    ],
)

audio_agent = Agent(
    name="Audio Agent",
    role="Analisar áudio",
    model=Gemini(id="gemini-2.0-flash-exp"),
)

calculator_agent = Agent(
    name="Calculator Agent",
    model=OpenAIChat(id="gpt-4o"),
    role="Calcular",
    tools=[CalculatorTools()],
    markdown=True,
)

calculator_writer_team = Team(
    name="Calculator Writer Team",
    model=OpenAIChat("gpt-4o"),
    members=[calculator_agent, writer_agent],
    instructions=[
        "Você é uma equipe de dois agentes. O agente calculadora e o agente escritor.",
        "O agente calculadora é responsável por calcular o resultado da expressão matemática.",
        "O agente escritor é responsável por escrever o resultado da expressão matemática de forma clara e envolvente."
        "Você precisa coordenar o trabalho entre os dois agentes e dar a resposta final ao usuário.",
        "Você precisa dar a resposta final ao usuário no formato e estilo solicitados.",
    ],
    markdown=True,
    show_members_responses=True,
)

reasoning_agent = Agent(
    name="Reasoning Agent",
    role="Raciocinar sobre Matemática",
    model=OpenAIChat(id="gpt-4o"),
    reasoning_model=DeepSeek(id="deepseek-reasoner"),
    instructions=["Você é um agente de raciocínio que pode raciocinar sobre matemática."],
    markdown=True,
    debug_mode=True,
)

code_execution_agent = Agent(
    name="Code Execution Sandbox",
    id="e2b-sandbox",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[E2BTools()],
    markdown=True,
    instructions=[
        "Você é um especialista em escrever e validar código Python usando um ambiente sandbox E2B seguro.",
        "Seu propósito principal é:",
        "1. Escrever código Python claro e eficiente com base nas solicitações do usuário",
        "2. Executar e verificar o código no sandbox E2B",
        "3. Compartilhar o código completo com o usuário, pois este é o caso de uso principal",
        "4. Fornecer explicações detalhadas de como o código funciona",
        "",
    ],
)

agent_team = Team(
    name="Agent Team",
    model=Claude(id="claude-3-7-sonnet-latest"),
    members=[
        web_agent,
        finance_agent,
        image_agent,
        audio_agent,
        calculator_writer_team,
        reasoning_agent,
        file_analysis_agent,
        code_execution_agent,
    ],
    instructions=[
        "Você é uma equipe de agentes que pode responder perguntas sobre web, finanças, imagens, áudio e arquivos.",
        "Você pode usar seus agentes membros para responder as perguntas.",
        "se você for perguntado sobre um arquivo, usar o agente de análise de arquivos para analisar o arquivo.",
        "Você também pode responder diretamente, não PRECISA encaminhar a pergunta para um agente membro.",
    ],
    respond_directly=True,
    markdown=True,
    show_members_responses=True,
)

# Use the reasoning agent to reason about the result
agent_team.print_response(
    "What is the square root of 6421123 times the square root of 9485271", stream=True
)
agent_team.print_response(
    "Calculate the sum of 10 and 20 and give write something about how you did the calculation",
    stream=True,
)

# Usar agentes web e finance para responder a pergunta
agent_team.print_response(
    "Summarize analyst recommendations and share the latest news for NVDA", stream=True
)

# image_path = Path(__file__).parent.joinpath("res/sample.jpg")
# # # Use image agent to analyze the image
# agent_team.print_response(
#     "Write a 3 sentence fiction story about the image",
#     images=[Image(filepath=image_path)],
# )

# Use audio agent to analyze the audio
# url = "https://agno-public.s3.amazonaws.com/demo_data/sample_conversation.wav"
# response = requests.get(url)
# audio_content = response.content
# # Give a sentiment analysis of this audio conversation. Use speaker A, speaker B to identify speakers.
# agent_team.print_response(
#     "Give a sentiment analysis of this audio conversation. Use speaker A, speaker B to identify speakers.",
#     audio=[Audio(content=audio_content)],
# )

# Use image agent to generate an image
# agent_team.print_response(
#     "Generate an image of a cat", stream=True
# )

# Use the calculator writer team to calculate the result
# agent_team.print_response(
#     "What is the square root of 6421123 times the square root of 9485271", stream=True
# )

# Use the code execution agent to write and execute code
# agent_team.print_response(
#     "write a python code to calculate the square root of 6421123 times the square root of 9485271",
#     stream=True,
# )


# # Use the reasoning agent to reason about the result
# agent_team.print_response("9.11 and 9.9 -- which is bigger?", stream=True)


# pdf_path = Path(__file__).parent.joinpath("res/ThaiRecipes.pdf")

# # Download the file using the download_file function
# download_file(
#     "https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf", str(pdf_path)
# )
# # Use file analysis agent to analyze the file
# agent_team.print_response(
#     "Summarize the contents of the attached file.",
#     files=[
#         File(
#             filepath=pdf_path,
#         ),
#     ],
# )
