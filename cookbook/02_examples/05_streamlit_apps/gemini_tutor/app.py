import nest_asyncio
import streamlit as st
from agents import EDUCATION_LEVELS, GEMINI_MODELS, get_gemini_tutor_agent
from agno.utils.streamlit import (
    COMMON_CSS,
    about_section,
    add_message,
    display_chat_messages,
    display_response,
    export_chat_history,
    initialize_agent,
    reset_session_state,
    session_selector_widget,
)

nest_asyncio.apply()
st.set_page_config(
    page_title="Gemini Tutor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)

# Educational-specific CSS
st.markdown(
    """
<style>
    .education-level {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    .learning-objective {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .assessment-box {
        background-color: rgba(33, 150, 243, 0.1);
        border-left: 4px solid #2196F3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .interactive-element {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 4px solid #FF9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""",
    unsafe_allow_html=True,
)


def restart_tutor(model_id: str = None, education_level: str = None):
    """Reiniciar o tutor com novas configurações."""
    target_model = model_id or st.session_state.get("current_model", GEMINI_MODELS[0])
    target_level = education_level or st.session_state.get(
        "education_level", EDUCATION_LEVELS[1]
    )

    new_agent = get_gemini_tutor_agent(
        model_id=target_model,
        education_level=target_level,
        session_id=None,
    )

    st.session_state["agent"] = new_agent
    st.session_state["session_id"] = new_agent.session_id
    st.session_state["messages"] = []
    st.session_state["current_model"] = target_model
    st.session_state["education_level"] = target_level
    st.session_state["is_new_session"] = True


def on_education_level_change():
    """Lidar com mudanças de nível educacional."""
    selected_level = st.session_state.get("education_level_selector")
    if selected_level:
        current_level = st.session_state.get("education_level")
        if current_level and current_level != selected_level:
            try:
                st.session_state["is_loading_session"] = False
                restart_tutor(education_level=selected_level)
            except Exception as e:
                st.sidebar.error(f"Erro ao mudar nível educacional: {str(e)}")


def on_model_change():
    """Lidar com mudanças de modelo."""
    selected_model = st.session_state.get("model_selector")
    if selected_model:
        if selected_model in GEMINI_MODELS:
            current_model = st.session_state.get("current_model")
            if current_model and current_model != selected_model:
                try:
                    st.session_state["is_loading_session"] = False
                    restart_tutor(model_id=selected_model)
                except Exception as e:
                    st.sidebar.error(f"Erro ao mudar para {selected_model}: {str(e)}")


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown("<h1 class='main-title'>Tutor Gemini</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>Seu assistente educacional de IA inteligente alimentado por Google Gemini</p>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Barra lateral - Autenticação
    ####################################################################
    st.sidebar.header("🔑 Autenticação")
    google_api_key = st.sidebar.text_input(
        "Chave de API Google",
        type="password",
        help="Obter sua chave de API do Google AI Studio (makersuite.google.com)",
    )

    if google_api_key:
        import os

        os.environ["GOOGLE_API_KEY"] = google_api_key
        st.sidebar.success("✅ Chave de API Google configurada")
    else:
        st.sidebar.warning("⚠️ Chave de API Google necessária para modelos Gemini")
        st.sidebar.info(
            "💡 Obter sua chave de API gratuita do [Google AI Studio](https://makersuite.google.com)"
        )

    ####################################################################
    # Seletores de Modelo e Nível Educacional
    ####################################################################
    st.sidebar.markdown("---")
    selected_model = st.sidebar.selectbox(
        "Selecionar Modelo Gemini",
        options=GEMINI_MODELS,
        index=0,
        key="model_selector",
        on_change=on_model_change,
    )

    selected_education_level = st.sidebar.selectbox(
        "Selecionar Nível Educacional",
        options=EDUCATION_LEVELS,
        index=1,  # Padrão para High School
        key="education_level_selector",
        on_change=on_education_level_change,
    )

    ####################################################################
    # Initialize Tutor Agent and Session
    ####################################################################
    gemini_tutor_agent = initialize_agent(
        selected_model,
        lambda model_id, session_id: get_gemini_tutor_agent(
            model_id=model_id,
            education_level=selected_education_level,
            session_id=session_id,
        ),
    )
    reset_session_state(gemini_tutor_agent)

    # Exibir nível educacional atual
    st.sidebar.markdown(
        f"**Nível Atual:** <span class='education-level'>{selected_education_level}</span>",
        unsafe_allow_html=True,
    )

    if prompt := st.chat_input("🎓 Sobre o que você gostaria de aprender hoje?"):
        add_message("user", prompt)

    ####################################################################
    # Modelos de Aprendizado
    ####################################################################
    st.sidebar.markdown("#### 📚 Modelos de Aprendizado")

    if st.sidebar.button("🔬 Conceitos de Ciência"):
        add_message(
            "user",
            f"Explicar um conceito fundamental de ciência apropriado para nível {selected_education_level} com exemplos interativos e questões de prática.",
        )

    if st.sidebar.button("📊 Resolução de Problemas de Matemática"):
        add_message(
            "user",
            f"Ensinar-me um conceito de matemática com exemplos de resolução de problemas passo a passo adequados para estudantes de {selected_education_level}.",
        )

    if st.sidebar.button("🌍 História e Cultura"):
        add_message(
            "user",
            f"Criar um módulo de aprendizado sobre um evento histórico ou tópico cultural, adaptado para nível {selected_education_level}.",
        )

    if st.sidebar.button("💻 Tecnologia e Programação"):
        add_message(
            "user",
            f"Explicar um conceito de tecnologia ou programação com exemplos práticos para aprendizes de {selected_education_level}.",
        )

    ####################################################################
    # Perguntas de Aprendizado de Exemplo
    ####################################################################
    st.sidebar.markdown("#### ❓ Perguntas de Exemplo")

    if st.sidebar.button("🧬 Como o DNA funciona?"):
        add_message(
            "user",
            "Como o DNA funciona? Por favor, explique com exemplos e crie uma experiência de aprendizado interativa.",
        )

    if st.sidebar.button("🚀 Física das Viagens Espaciais"):
        add_message(
            "user",
            "Explicar a física por trás das viagens espaciais com exemplos práticos e experimentos mentais.",
        )

    if st.sidebar.button("🎨 Visão Geral da História da Arte"):
        add_message(
            "user",
            "Dar-me uma visão geral da arte renascentista com análise visual e elementos interativos.",
        )

    ####################################################################
    # Ferramentas de Estudo
    ####################################################################
    st.sidebar.markdown("#### 🛠️ Ferramentas de Estudo")

    if st.sidebar.button("📝 Criar Guia de Estudo"):
        add_message(
            "user",
            "Criar um guia de estudo abrangente para meu último tópico de aprendizado com pontos-chave, questões de prática e materiais de revisão.",
        )

    if st.sidebar.button("🧪 Questionário de Prática"):
        add_message(
            "user",
            "Gerar um questionário de prática baseado em nossa sessão de aprendizado recente com diferentes tipos de questões e explicações detalhadas.",
        )

    if st.sidebar.button("🔍 Análise Profunda"):
        add_message(
            "user",
            "Vamos fazer uma análise profunda do tópico mais complexo que discutimos, dividindo-o em componentes mais simples.",
        )

    ####################################################################
    # Botões de utilidade
    ####################################################################
    st.sidebar.markdown("#### 🛠️ Utilitários")
    col1, col2 = st.sidebar.columns([1, 1])

    with col1:
        if st.sidebar.button("🔄 Nova Sessão de Aprendizado", use_container_width=True):
            restart_tutor()
            st.rerun()

    with col2:
        has_messages = (
            st.session_state.get("messages") and len(st.session_state["messages"]) > 0
        )

        if has_messages:
            session_id = st.session_state.get("session_id")
            if session_id and gemini_tutor_agent.get_session_name():
                filename = (
                    f"gemini_tutor_session_{gemini_tutor_agent.get_session_name()}.md"
                )
            elif session_id:
                filename = f"gemini_tutor_session_{session_id}.md"
            else:
                filename = "gemini_tutor_session_new.md"

            if st.sidebar.download_button(
                "💾 Exportar Aprendizado",
                export_chat_history("Gemini Tutor"),
                file_name=filename,
                mime="text/markdown",
                use_container_width=True,
                help=f"Exportar {len(st.session_state['messages'])} interações de aprendizado",
            ):
                st.sidebar.success("Sessão de aprendizado exportada!")
        else:
            st.sidebar.button(
                "💾 Exportar Aprendizado",
                disabled=True,
                use_container_width=True,
                help="Nenhum conteúdo de aprendizado para exportar",
            )

    ####################################################################
    # Display Chat Messages
    ####################################################################
    display_chat_messages()

    ####################################################################
    # Generate response for user message
    ####################################################################
    last_message = (
        st.session_state["messages"][-1] if st.session_state["messages"] else None
    )
    if last_message and last_message.get("role") == "user":
        question = last_message["content"]
        display_response(gemini_tutor_agent, question)

    ####################################################################
    # Session management widgets
    ####################################################################
    session_selector_widget(
        gemini_tutor_agent,
        selected_model,
        lambda model_id, session_id: get_gemini_tutor_agent(
            model_id=model_id,
            education_level=selected_education_level,
            session_id=session_id,
        ),
    )

    ####################################################################
    # About section
    ####################################################################
    about_section(
        f"Este Tutor Gemini fornece experiências educacionais personalizadas para estudantes de {selected_education_level} usando os modelos avançados de IA Gemini do Google com capacidades de aprendizado multimodal."
    )


if __name__ == "__main__":
    main()
