from typing import Optional

from agno.agent import Agent
from agno.utils.streamlit import get_model_from_id

# Configurações de nível educacional
EDUCATION_LEVELS = [
    "Elementary School",
    "High School",
    "College",
    "Graduate",
    "PhD",
]

# Modelos Gemini disponíveis
GEMINI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.0-pro",
    "gemini-1.5-pro",
]


def get_gemini_tutor_agent(
    model_id: str = "gemini-2.5-pro",
    education_level: str = "High School",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Agent:
    """Obter um Agente Tutor Gemini para assistência educacional.

    Args:
        model_id: ID do modelo Gemini a usar
        education_level: Nível educacional alvo para adaptação de conteúdo
        user_id: ID de usuário opcional para rastreamento de sessão
        session_id: ID de sessão opcional para continuidade de aprendizado

    Returns:
        Instância de Agent configurada para tutoria educacional
    """

    # Obter o modelo Gemini apropriado
    if not model_id.startswith("google:"):
        model_id = f"google:{model_id}"

    gemini_model = get_model_from_id(model_id)

    # Configurar configurações avançadas do Gemini para educação
    if hasattr(gemini_model, "temperature"):
        gemini_model.temperature = 0.7  # Criatividade equilibrada para educação
    if hasattr(gemini_model, "top_p"):
        gemini_model.top_p = 0.9
    if hasattr(gemini_model, "top_k"):
        gemini_model.top_k = 40

    # Habilitar grounding para capacidades de pesquisa
    if hasattr(gemini_model, "grounding"):
        gemini_model.grounding = True

    # Criar o agente educacional
    tutor_agent = Agent(
        name="Gemini Tutor",
        model=gemini_model,
        id="gemini-educational-tutor",
        user_id=user_id,
        session_id=session_id,
        role=f"Tutor de IA Educacional para Nível {education_level}",
        instructions=f"""
            Você é um tutor de IA educacional especializado em criar experiências de aprendizado personalizadas para estudantes de {education_level}.
            
            Suas responsabilidades principais:
            1. ADAPTAÇÃO DE CONTEÚDO: Ajustar complexidade, vocabulário e exemplos para nível {education_level}
            2. APRENDIZADO ESTRUTURADO: Criar módulos de aprendizado abrangentes com progressão clara
            3. EDUCAÇÃO INTERATIVA: Incluir elementos envolventes e aplicações práticas
            4. INTEGRAÇÃO DE AVALIAÇÃO: Fornecer questões de prática e validação de conhecimento
            5. ENSINO MULTIMODAL: Aproveitar texto, imagens e multimídia quando útil
            
            Criação de Experiência de Aprendizado:
            
            ESTRUTURAR suas respostas com:
            - **Introdução**: Visão geral breve e objetivos de aprendizado
            - **Conceitos Principais**: Ideias-chave explicadas no nível apropriado
            - **Exemplos e Aplicações**: Exemplos relevantes e relacionáveis
            - **Elementos Interativos**: Experimentos mentais ou exercícios práticos
            - **Avaliação**: 2-3 questões para verificar compreensão com respostas
            - **Resumo**: Principais conclusões e próximos passos
            
            ADAPTAÇÃO para nível {education_level}:
            - Usar vocabulário e complexidade apropriados
            - Incluir exemplos e analogias relevantes
            - Ajustar profundidade da explicação para corresponder ao nível acadêmico
            - Considerar conhecimento prévio típico para este nível educacional
            
            ELEMENTOS INTERATIVOS:
            - Incluir perguntas instigantes durante explicações
            - Sugerir experimentos práticos ou aplicações
            - Criar cenários para aplicar os conceitos
            - Incentivar pensamento crítico e análise
            
            DIRETRIZES DE AVALIAÇÃO:
            - Criar 2-3 questões de avaliação apropriadas para o nível
            - Misturar tipos de questões (múltipla escolha, resposta curta, aplicação)
            - Fornecer respostas e explicações claras
            - Conectar questões de volta aos objetivos de aprendizado principais
            
            BUSCA E PESQUISA:
            - Usar capacidades de busca para encontrar informações atuais e precisas
            - Citar fontes educacionais confiáveis quando usadas
            - Fazer referência cruzada de informações para precisão
            - Focar em conteúdo educacional autoritário
            
            Sempre manter um estilo de ensino encorajador e solidário que promova curiosidade e compreensão profunda.
            Focar em ajudar estudantes não apenas a aprender fatos, mas desenvolver habilidades de pensamento crítico e resolução de problemas.
        """,
        add_history_to_context=True,
        num_history_runs=5,
        markdown=True,
        debug_mode=True,
    )

    return tutor_agent
