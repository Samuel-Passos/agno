"""♟️ Batalha de Equipe de Xadrez

Este exemplo demonstra como construir um jogo de xadrez multi-agente sofisticado onde diferentes modelos de IA
competem entre si. O sistema coordena múltiplos agentes especializados trabalhando juntos para jogar xadrez.

A Equipe de Xadrez inclui:
- Agente Jogador Branco: Estratégia e faz jogadas para peças brancas
- Agente Jogador Preto: Estratégia e faz jogadas para peças pretas
- Agente Mestre do Jogo: Coordena a jogabilidade e fornece análise de posição

Fluxo de Jogabilidade de Exemplo:
- Mestre do Jogo coordena entre agentes Branco e Preto
- Cada agente analisa a posição atual e jogadas legais
- Agentes tomam decisões estratégicas baseadas em princípios de xadrez
- python-chess valida todas as jogadas e mantém o estado do jogo
- Jogo continua até xeque-mate, empate ou condições de empate

A Equipe de Xadrez usa:
- Funções de agente especializadas para diferentes aspectos do jogo
- Coordenação baseada em turnos para jogabilidade sequencial
- Validação de jogadas em tempo real e atualizações do tabuleiro
- Análise estratégica e avaliação de posição

Ver o README para instruções sobre como executar a aplicação.
"""

from typing import Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.team.team import Team
from agno.utils.streamlit import get_model_with_provider

db_url = "postgresql+psycopg://db_user:wc6%40YU8evhm1234@localhost:5433/ai"


def get_chess_team(
    white_model: str = "gpt-4o",
    black_model: str = "claude-4-sonnet",
    master_model: str = "gpt-4o",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Team:
    """Obter uma Equipe de Xadrez com agentes jogadores especializados.

    Args:
        white_model: ID do modelo para o agente jogador branco
        black_model: ID do modelo para o agente jogador preto
        master_model: ID do modelo para o agente mestre do jogo
        user_id: ID de usuário opcional para rastreamento de sessão
        session_id: ID de sessão opcional para continuidade do jogo

    Returns:
        Instância de Team configurada para jogabilidade de xadrez
    """

    # Obter instâncias de modelo com detecção automática de provedor correta
    white_model_instance = get_model_with_provider(white_model)
    black_model_instance = get_model_with_provider(black_model)
    master_model_instance = get_model_with_provider(master_model)

    db = PostgresDb(
        db_url=db_url,
        session_table="sessions",
        db_schema="ai",
    )

    # Criar agentes de xadrez especializados
    white_player_agent = Agent(
        name="White Player",
        model=white_model_instance,
        db=db,
        id="white-chess-player",
        user_id=user_id,
        session_id=session_id,
        role="White Chess Strategist",
        instructions="""
            Você é um estrategista de xadrez jogando como peças BRANCAS.
            
            Suas responsabilidades:
            1. Analisar a posição atual do tabuleiro e jogadas legais
            2. Aplicar princípios de xadrez: desenvolvimento de peças, controle do centro, segurança do rei
            3. Considerar oportunidades táticas: espetos, garfos, descobertas, ataques descobertos
            4. Planejar objetivos estratégicos: estrutura de peões, coordenação de peças, preparação de fim de jogo
            5. Escolher a melhor jogada das opções legais fornecidas
            
            Formato de resposta:
            - Responder APENAS com sua jogada escolhida em notação UCI (ex: 'e2e4')
            - Não incluir nenhuma explicação ou texto adicional
            - Garantir que sua jogada está na lista de jogadas legais fornecida
            
            Princípios de xadrez a seguir:
            - Controlar o centro (casas e4, d4, e5, d5)
            - Desenvolver peças antes de movê-las duas vezes
            - Fazer roque cedo para segurança do rei
            - Não trazer a dama muito cedo
            - Considerar atividade e coordenação de peças
        """,
        markdown=True,
        debug_mode=True,
    )

    black_player_agent = Agent(
        name="Black Player",
        model=black_model_instance,
        db=db,
        id="black-chess-player",
        user_id=user_id,
        session_id=session_id,
        role="Black Chess Strategist",
        instructions="""
            Você é um estrategista de xadrez jogando como peças PRETAS.
            
            Suas responsabilidades:
            1. Analisar a posição atual do tabuleiro e jogadas legais
            2. Aplicar princípios de xadrez: desenvolvimento de peças, controle do centro, segurança do rei
            3. Considerar oportunidades táticas: espetos, garfos, descobertas, ataques descobertos
            4. Planejar objetivos estratégicos: estrutura de peões, coordenação de peças, preparação de fim de jogo
            5. Escolher a melhor jogada das opções legais fornecidas
            
            Formato de resposta:
            - Responder APENAS com sua jogada escolhida em notação UCI (ex: 'e7e5')
            - Não incluir nenhuma explicação ou texto adicional
            - Garantir que sua jogada está na lista de jogadas legais fornecida
            
            Princípios de xadrez a seguir:
            - Controlar o centro (casas e4, d4, e5, d5)
            - Desenvolver peças antes de movê-las duas vezes
            - Fazer roque cedo para segurança do rei
            - Não trazer a dama muito cedo
            - Considerar atividade e coordenação de peças
            - Reagir à estratégia de abertura das brancas apropriadamente
        """,
        markdown=True,
        debug_mode=True,
    )

    # Criar a equipe de xadrez com coordenação do mestre do jogo
    chess_team = Team(
        name="Chess Team",
        model=master_model_instance,
        db=db,
        id="chess-game-team",
        user_id=user_id,
        session_id=session_id,
        members=[white_player_agent, black_player_agent],
        mode="route",
        instructions="""
            Você é o Mestre do Jogo de Xadrez coordenando uma partida de xadrez IA vs IA.
            
            Seus papéis:
            1. COORDENAÇÃO DE JOGADAS: Rotear solicitações de jogada para o agente jogador apropriado
            2. ANÁLISE DO JOGO: Fornecer avaliação de posição e comentários quando solicitado
            3. ESTADO DO JOGO: Monitorar progresso do jogo e detectar condições especiais
            
            Ao lidar com solicitações:
            
            PARA SOLICITAÇÕES DE JOGADA:
            - Verificar 'current_player' no contexto/dependências
            - Se current_player é 'white_piece_agent': rotear para White Player
            - Se current_player é 'black_piece_agent': rotear para Black Player
            - Retornar a resposta de jogada do jogador EXATAMENTE sem modificação
            
            PARA SOLICITAÇÕES DE ANÁLISE:
            - Quando nenhum current_player for especificado, fornecer análise do jogo
            - Avaliar atividade de peças, segurança do rei, equilíbrio material
            - Avaliar temas táticos e estratégicos na posição
            - Comentar sobre jogadas recentes e planejamento futuro
            
            Diretrizes importantes:
            - Nunca modificar ou interpretar respostas dos agentes jogadores
            - Rotear solicitações de jogada diretamente para o agente apropriado
            - Apenas fornecer análise quando explicitamente solicitado
            - Manter fluxo do jogo e coordenar transições suaves de turno
        """,
        markdown=True,
        debug_mode=True,
        show_members_responses=True,
    )

    return chess_team
