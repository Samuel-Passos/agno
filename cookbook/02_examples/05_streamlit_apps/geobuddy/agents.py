from pathlib import Path
from typing import Optional

from agno.agent import Agent
from agno.media import Image
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.utils.streamlit import get_model_from_id


def get_geobuddy_agent(
    model_id: str = "gemini-2.0-flash-exp",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Agent:
    """Obter um Agente GeoBuddy para análise de imagens geográficas.

    Args:
        model_id: ID do modelo a usar para análise
        user_id: ID de usuário opcional para rastreamento de sessão
        session_id: ID de sessão opcional para continuidade de conversa

    Returns:
        Instância de Agent configurada para análise geográfica
    """

    model = get_model_from_id(model_id)

    # Criar o agente de análise geográfica
    geobuddy_agent = Agent(
        name="GeoBuddy",
        model=model,
        id="geography-location-detective",
        user_id=user_id,
        session_id=session_id,
        tools=[DuckDuckGoTools()],
        role="Detetive de Localização Geográfica",
        instructions="""
            Você é GeoBuddy, um especialista em geografia que ajuda a identificar localizações a partir de fotos.
            
            Ao analisar imagens, procurar por estas pistas:
            
            • **Arquitetura e Edifícios**: Que estilo? Que materiais? Moderno ou histórico?
            • **Placas e Texto**: Nomes de ruas, placas de lojas, outdoors - qualquer texto legível
            • **Marcos**: Edifícios famosos, monumentos ou estruturas reconhecíveis
            • **Características Naturais**: Montanhas, litorais, rios, paisagens distintas
            • **Detalhes Culturais**: Roupas, veículos, placas de carros, costumes locais
            • **Ambiente**: Clima, vegetação, iluminação que sugere clima/região
            
            Para cada imagem, fornecer:
            
            **Palpite de Localização**: Seja o mais específico possível (rua, cidade, país)
            **Confiança**: Quão certo você está? (Alta/Média/Baixa)
            **Pistas-Chave**: O que te fez pensar nesta localização?
            **Raciocínio**: Caminhar através do seu processo de pensamento
            **Outras Possibilidades**: Se incerto, o que mais poderia ser?
            
            Manter sua análise clara e conversacional. Focar no que você pode realmente ver, não especulação.
            Usar busca quando precisar verificar marcos ou obter mais informações.
        """,
        add_history_to_context=True,
        num_history_runs=3,
        markdown=True,
        debug_mode=True,
    )

    return geobuddy_agent


def analyze_image_location(agent: Agent, image_path: Path) -> Optional[str]:
    """Analisar uma imagem para prever sua localização geográfica.

    Args:
        agent: A instância do agente GeoBuddy
        image_path: Caminho para o arquivo de imagem

    Returns:
        Resultado da análise ou None se falhou
    """
    try:
        prompt = """
        Por favor, analise esta imagem e preveja sua localização geográfica. Use sua estrutura 
        abrangente de análise visual para identificar a localização com base em todas as pistas disponíveis.
        
        Fornecer uma análise detalhada seguindo seu formato de resposta estruturado com previsão de localização,
        análise visual, processo de raciocínio e possibilidades alternativas.
        """

        response = agent.run(prompt, images=[Image(filepath=image_path)])
        return response.content
    except Exception as e:
        raise RuntimeError(f"Error analyzing image location: {str(e)}")
