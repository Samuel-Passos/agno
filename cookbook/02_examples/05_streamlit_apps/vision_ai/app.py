from pathlib import Path

import streamlit as st
from agents import get_vision_agent
from agno.media import Image
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

st.set_page_config(
    page_title="Vision AI",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(COMMON_CSS, unsafe_allow_html=True)


def restart_agent(model_id: str = None):
    target_model = model_id or st.session_state.get("current_model", MODELS[0])

    st.session_state["agent"] = None
    st.session_state["session_id"] = None
    st.session_state["messages"] = []
    st.session_state["current_model"] = target_model
    st.session_state["is_new_session"] = True

    # Clear current image
    if "current_image" in st.session_state:
        del st.session_state["current_image"]


def on_model_change():
    selected_model = st.session_state.get("model_selector")
    if selected_model:
        if selected_model in MODELS:
            new_model_id = selected_model
            current_model = st.session_state.get("current_model")

            if current_model and current_model != new_model_id:
                try:
                    st.session_state["is_loading_session"] = False
                    restart_agent(model_id=new_model_id)

                except Exception as e:
                    st.sidebar.error(f"Erro ao mudar para {selected_model}: {str(e)}")
        else:
            st.sidebar.error(f"Modelo desconhecido: {selected_model}")


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown("<h1 class='main-title'>🖼️ Vision AI</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>Análise e compreensão inteligente de imagens</p>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Seletor de modelo
    ####################################################################
    selected_model = st.sidebar.selectbox(
        "Selecionar Modelo",
        options=MODELS,
        index=0,
        key="model_selector",
        on_change=on_model_change,
        help="Escolher o modelo de IA para análise de imagem",
    )

    ####################################################################
    # Configurações Vision AI
    ####################################################################
    st.sidebar.markdown("#### 🔍 Configurações de Análise")

    analysis_mode = st.sidebar.radio(
        "Modo de Análise",
        ["Auto", "Manual", "Hybrid"],
        index=0,
        help="""
        - **Auto**: Análise abrangente automática de imagem
        - **Manual**: Análise baseada em suas instruções específicas  
        - **Hybrid**: Análise automática + suas instruções personalizadas
        """,
    )

    enable_search = st.sidebar.checkbox(
        "Habilitar Busca Web",
        value=False,
        key="enable_search",
        help="Permitir que o agente busque por contexto adicional",
    )

    ####################################################################
    # Initialize Agent and Session
    ####################################################################
    # Create unified agent with search capability
    def get_vision_agent_with_settings(model_id: str, session_id: str = None):
        return get_vision_agent(
            model_id=model_id, enable_search=enable_search, session_id=session_id
        )

    vision_agent = initialize_agent(selected_model, get_vision_agent_with_settings)
    reset_session_state(vision_agent)

    if prompt := st.chat_input("👋 Pergunte-me qualquer coisa!"):
        add_message("user", prompt)

    ####################################################################
    # Upload de arquivo
    ####################################################################
    st.sidebar.markdown("#### 🖼️ Análise de Imagem")

    uploaded_file = st.sidebar.file_uploader(
        "Enviar uma Imagem", type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        temp_dir = Path("tmp")
        temp_dir.mkdir(exist_ok=True)
        image_path = temp_dir / uploaded_file.name

        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state["current_image"] = {
            "path": str(image_path),
            "name": uploaded_file.name,
            "analysis_mode": analysis_mode,
        }

        st.sidebar.image(uploaded_file, caption=uploaded_file.name, width=200)
        st.sidebar.success(f"Imagem '{uploaded_file.name}' enviada")

    # Análise
    if st.session_state.get("current_image") and not prompt:
        if st.sidebar.button(
            "🔍 Analisar Imagem", type="primary", use_container_width=True
        ):
            image_info = st.session_state["current_image"]

            if analysis_mode == "Manual":
                custom_instructions = st.sidebar.text_area(
                    "Instruções de Análise", key="manual_instructions"
                )
                if custom_instructions:
                    add_message(
                        "user",
                        f"Analisar esta imagem com instruções: {custom_instructions}",
                    )
                else:
                    add_message("user", f"Analisar esta imagem: {image_info['name']}")
            elif analysis_mode == "Hybrid":
                custom_instructions = st.sidebar.text_area(
                    "Instruções Adicionais", key="hybrid_instructions"
                )
                if custom_instructions:
                    add_message(
                        "user",
                        f"Analisar esta imagem com foco adicional: {custom_instructions}",
                    )
                else:
                    add_message("user", f"Analisar esta imagem: {image_info['name']}")
            else:
                add_message("user", f"Analisar esta imagem: {image_info['name']}")

    ###############################################################
    # Perguntas de Exemplo
    ###############################################################
    st.sidebar.markdown("#### ❓ Perguntas de Exemplo")
    if st.sidebar.button("🔍 Quais são os principais objetos?"):
        add_message("user", "Quais são os principais objetos?")
    if st.sidebar.button("📝 Há algum texto para ler?"):
        add_message("user", "Há algum texto para ler?")
    if st.sidebar.button("🎨 Descrever as cores e o humor"):
        add_message("user", "Descrever as cores e o humor")

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

        images_to_include = []
        if st.session_state.get("current_image"):
            image_info = st.session_state["current_image"]
            images_to_include = [Image(filepath=image_info["path"])]

        if images_to_include:
            with st.chat_message("assistant"):
                response_container = st.empty()
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = vision_agent.run(question, images=images_to_include)
                        response_container.markdown(response.content)
                        add_message("assistant", response.content)
                    except Exception as e:
                        error_message = f"❌ Erro: {str(e)}"
                        response_container.error(error_message)
                        add_message("assistant", error_message)
        else:
            # Use the same unified agent for all responses (maintains session)
            display_response(vision_agent, question)

    ####################################################################
    # Botões de utilidade
    ####################################################################
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
            session_name = None

            try:
                if session_id and vision_agent:
                    session_name = vision_agent.get_session_name()
            except Exception:
                session_name = None

            if session_id and session_name:
                filename = f"vision_ai_chat_{session_name}.md"
            elif session_id:
                filename = f"vision_ai_chat_{session_id[:8]}.md"
            else:
                filename = "vision_ai_chat_new.md"

            if st.sidebar.download_button(
                "💾 Exportar Chat",
                export_chat_history("Vision AI"),
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
    # Session management widgets
    ####################################################################
    is_new_session = st.session_state.get("is_new_session", False)
    has_messages = (
        st.session_state.get("messages") and len(st.session_state["messages"]) > 0
    )

    if not is_new_session or has_messages:
        session_selector_widget(
            vision_agent, selected_model, get_vision_agent_with_settings
        )
        if is_new_session and has_messages:
            st.session_state["is_new_session"] = False
    else:
        st.sidebar.info("🆕 Novo Chat - Inicie sua conversa!")

    ####################################################################
    # Seção sobre
    ####################################################################
    about_section(
        "Este assistente Vision AI analisa imagens e responde perguntas sobre conteúdo visual usando "
        "modelos avançados de visão-linguagem."
    )


if __name__ == "__main__":
    main()
