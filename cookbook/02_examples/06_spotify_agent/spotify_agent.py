from os import getenv

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.os import AgentOS
from agno.tools.spotify import SpotifyTools

# Seu token de acesso do Spotify (obtenha um em https://developer.spotify.com/)
SPOTIFY_TOKEN = getenv("SPOTIFY_TOKEN")

# Inicializar o toolkit do Spotify
spotify = SpotifyTools(
    access_token=SPOTIFY_TOKEN,
    default_market="US",
)

# Criar um agente com o toolkit do Spotify
agent = Agent(
    name="Spotify Agent",
    model=Claude(id="claude-sonnet-4-5"),
    tools=[spotify],
    instructions=[
        "Você é um assistente musical útil que pode pesquisar músicas, gerenciar playlists e controlar a reprodução.",
        "Ao criar uma playlist:",
        "1. Usar get_artist_top_tracks para solicitações sobre artistas específicos",
        "2. Usar get_track_recommendations com parâmetros de humor (target_valence para felicidade, target_energy para intensidade) para solicitações baseadas em humor",
        "3. Usar search_tracks para músicas específicas ou consultas gerais",
        "4. Usar get_album_tracks quando o usuário quiser um álbum inteiro adicionado",
        "5. Coletar URIs de faixas e chamar create_playlist com elas",
        "Ao atualizar uma playlist:",
        "1. Usar get_user_playlists para encontrar a playlist pelo nome",
        "2. Usar o ID da playlist para adicionar ou remover faixas",
        "Para recomendações, usar faixas/artistas seed do que você já encontrou para get_track_recommendations.",
        "Sempre fornecer a URL da playlist quando criada ou modificada.",
    ],
    markdown=True,
    db=SqliteDb(db_file="tmp/spotify_agent.db"),
    add_history_to_context=True,
    num_history_runs=5,
)

agent_os = AgentOS(
    description="Spotify Agent",
    agents=[agent],
)

app = agent_os.get_app()

# Exemplo de uso
if __name__ == "__main__":
    agent_os.serve(app="spotify_agent:app", reload=True)
