import nest_asyncio
import streamlit as st
from agents import get_llama_tutor_agent
from agno.utils.streamlit import (
    COMMON_CSS,
    MODELS,
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
    page_title="Llama Tutor",
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)

# Extended models list including Groq models for Llama Tutor
TUTOR_MODELS = MODELS + [
    "groq:llama-3.3-70b-versatile",
    "groq:llama-3.1-70b-versatile",
    "groq:mixtral-8x7b-32768",
]


def restart_agent(model_id: str = None, education_level: str = None):
    target_model = model_id or st.session_state.get("current_model", TUTOR_MODELS[0])
    target_education_level = education_level or st.session_state.get(
        "education_level", "High School"
    )

    new_agent = get_llama_tutor_agent(
        model_id=target_model, education_level=target_education_level, session_id=None
    )

    st.session_state["agent"] = new_agent
    st.session_state["session_id"] = new_agent.session_id
    st.session_state["messages"] = []
    st.session_state["current_model"] = target_model
    st.session_state["education_level"] = target_education_level
    st.session_state["is_new_session"] = True


def on_model_change():
    selected_model = st.session_state.get("model_selector")
    if selected_model:
        if selected_model in TUTOR_MODELS:
            new_model_id = selected_model
            current_model = st.session_state.get("current_model")

            if current_model and current_model != new_model_id:
                try:
                    st.session_state["is_loading_session"] = False
                    # Iniciar novo chat com novo modelo
                    restart_agent(model_id=new_model_id)

                except Exception as e:
                    st.sidebar.error(f"Erro ao mudar para {selected_model}: {str(e)}")
        else:
            st.sidebar.error(f"Modelo desconhecido: {selected_model}")


def on_education_level_change():
    selected_level = st.session_state.get("education_level_selector")
    current_level = st.session_state.get("education_level", "High School")

    if selected_level and selected_level != current_level:
        try:
            # Iniciar novo chat com novo nível educacional
            restart_agent(education_level=selected_level)
        except Exception as e:
            st.sidebar.error(f"Erro ao mudar para {selected_level}: {str(e)}")


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown("<h1 class='main-title'>Tutor Llama</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>Seu assistente educacional inteligente alimentado por Agno</p>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Seletor de modelo
    ####################################################################
    selected_model = st.sidebar.selectbox(
        "Selecionar Modelo",
        options=TUTOR_MODELS,
        index=len(MODELS),  # Padrão para primeiro modelo Groq
        key="model_selector",
        on_change=on_model_change,
    )

    ####################################################################
    # Seletor de nível educacional
    ####################################################################
    education_levels = [
        "Elementary School",
        "Middle School",
        "High School",
        "College",
        "Undergrad",
        "Graduate",
    ]

    selected_education_level = st.sidebar.selectbox(
        "Nível Educacional",
        options=education_levels,
        index=2,  # Padrão para High School
        key="education_level_selector",
        on_change=on_education_level_change,
    )

    ####################################################################
    # Initialize Agent and Session
    ####################################################################
    # Store the education level in session state for agent creation
    if "education_level" not in st.session_state:
        st.session_state["education_level"] = selected_education_level

    llama_tutor_agent = initialize_agent(
        selected_model,
        lambda model_id, session_id: get_llama_tutor_agent(
            model_id=model_id,
            education_level=st.session_state.get("education_level", "High School"),
            session_id=session_id,
        ),
    )
    reset_session_state(llama_tutor_agent)

    if prompt := st.chat_input("✨ Sobre o que você gostaria de aprender?"):
        add_message("user", prompt)

    ###############################################################
    # Perguntas de Exemplo
    ###############################################################
    st.sidebar.markdown("#### ❓ Perguntas de Exemplo")
    if st.sidebar.button("🧬 Como funciona a fotossíntese?"):
        add_message(
            "user",
            "Como funciona a fotossíntese?",
        )
    if st.sidebar.button("📚 Explicar fundamentos de cálculo"):
        add_message(
            "user",
            "O que é cálculo e como é usado na vida real?",
        )
    if st.sidebar.button("🌍 Causas da Primeira Guerra Mundial"):
        add_message(
            "user",
            "Quais foram as principais causas da Primeira Guerra Mundial?",
        )
    if st.sidebar.button("⚛️ O que é física quântica?"):
        add_message(
            "user",
            "Explicar física quântica em termos simples",
        )

    ###############################################################
    # Botões de utilidade
    ###############################################################
    st.sidebar.markdown("#### 🛠️ Utilitários")
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        if st.sidebar.button("🔄 Novo Chat", use_container_width=True):
            restart_agent()
            st.rerun()

    with col2:
        has_messages = (
            st.session_state.get("messages") and len(st.session_state["messages"]) > 0
        )

        if has_messages:
            session_id = st.session_state.get("session_id")
            if session_id:
                try:
                    session_name = llama_tutor_agent.get_session_name()
                    if session_name:
                        filename = f"llama_tutor_analysis_{session_name}.md"
                    else:
                        filename = f"llama_tutor_analysis_{session_id}.md"
                except Exception:
                    filename = f"llama_tutor_analysis_{session_id}.md"
            else:
                filename = "llama_tutor_analysis_new.md"

            if st.sidebar.download_button(
                "💾 Exportar Chat",
                export_chat_history("Llama Tutor"),
                file_name=filename,
                mime="text/markdown",
                use_container_width=True,
                help=f"Exportar {len(st.session_state['messages'])} mensagens",
            ):
                st.sidebar.success("Histórico de chat exportado!")
        else:
            st.sidebar.button(
                "💾 Exportar Chat",
                disabled=True,
                use_container_width=True,
                help="Nenhuma mensagem para exportar",
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
        display_response(llama_tutor_agent, question)

    ####################################################################
    # Session management widgets
    ####################################################################
    session_selector_widget(
        llama_tutor_agent,
        selected_model,
        lambda model_id, session_id: get_llama_tutor_agent(
            model_id=model_id,
            education_level=st.session_state.get("education_level", "High School"),
            session_id=session_id,
        ),
    )

    ####################################################################
    # About section
    ####################################################################
    about_section(
        "Este Tutor Llama fornece assistência educacional personalizada em todas as matérias e níveis educacionais."
    )


if __name__ == "__main__":
    main()
