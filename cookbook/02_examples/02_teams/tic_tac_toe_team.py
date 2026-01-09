from textwrap import dedent

from agno.agent import Agent
from agno.models.google.gemini import Gemini
from agno.models.openai import OpenAIChat
from agno.team.team import Team

player_1 = Agent(
    name="Player 1",
    role="Jogar Jogo da Velha",
    model=OpenAIChat(id="gpt-4o"),
    add_name_to_context=True,
    instructions=dedent("""
    Você é um jogador de Jogo da Velha.
    Você receberá um tabuleiro de Jogo da Velha e um jogador para jogar contra.
    Você precisará jogar o jogo e tentar vencer.
    """),
)

player_2 = Agent(
    name="Player 2",
    role="Jogar Jogo da Velha",
    model=Gemini(id="gemini-2.0-flash"),
    add_name_to_context=True,
    instructions=dedent("""
    Você é um jogador de Jogo da Velha.
    Você receberá um tabuleiro de Jogo da Velha e um jogador para jogar contra.
    Você precisará jogar o jogo e tentar vencer.
    """),
)

# Esta é uma equipe simples que joga Jogo da Velha. Não é perfeita e funcionaria melhor com raciocínio.
agent_team = Team(
    name="Tic Tac Toe Team",
    model=OpenAIChat("gpt-4o"),
    members=[player_1, player_2],
    instructions=[
        "Você é um mestre de jogos.",
        "Inicializar o estado do tabuleiro como uma grade 3x3 vazia com números 1-9.",
        "Pedir aos jogadores para fazerem suas jogadas uma por uma e aguardar suas respostas. Delegar a vez para o outro jogador após cada jogada.",
        "Após cada jogada, armazenar o estado atualizado do tabuleiro para que os jogadores tenham acesso ao estado do tabuleiro.",
        "Não confirmar os resultados do jogo depois, apenas relatar o estado final do tabuleiro e os resultados.",
        "Você deve parar o jogo quando um dos jogadores tiver vencido.",
    ],
    share_member_interactions=True,
    debug_mode=True,
    markdown=True,
    show_members_responses=True,
)

agent_team.print_response(
    input="Run a full Tic Tac Toe game. After the game, report the final board state and the results.",
    stream=True,
)
