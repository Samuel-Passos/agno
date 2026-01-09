from agno.agent import Agent
from agno.models.google.gemini import Gemini
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools

# Criar agentes especializados individuais
researcher = Agent(
    name="Researcher",
    role="Especialista em encontrar informações",
    tools=[DuckDuckGoTools()],
    model=Gemini("gemini-2.0-flash-001"),
)

writer = Agent(
    name="Writer",
    role="Especialista em escrever conteúdo claro e envolvente",
    model=Gemini("gemini-2.0-flash-001"),
)

# Criar uma equipe com esses agentes
content_team = Team(
    name="Content Team",
    model=Gemini("gemini-2.5-flash"),
    # model=Gemini("gemini-2.0-flash-lite"),  # Tentar um modelo pequeno para resposta mais rápida
    members=[researcher, writer],
    instructions="Você é uma equipe de pesquisadores e escritores que trabalham juntos para criar conteúdo de alta qualidade.",
    show_members_responses=True,
)

# Executar a equipe com uma tarefa
content_team.print_response("Create a short article about quantum computing")
