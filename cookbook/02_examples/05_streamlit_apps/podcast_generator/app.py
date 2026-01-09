import streamlit as st
from agents import generate_podcast, generate_podcast_agent
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
    page_title="Podcast Generator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)


def restart_agent(model_id: str = None):
    target_model = model_id or st.session_state.get("current_model", "openai:gpt-4o")

    new_agent = generate_podcast_agent(model_id=target_model, session_id=None)

    st.session_state["agent"] = new_agent
    st.session_state["session_id"] = new_agent.session_id
    st.session_state["messages"] = []
    st.session_state["current_model"] = target_model
    st.session_state["is_new_session"] = True


def on_model_change():
    selected_model = st.session_state.get("model_selector")
    if selected_model:
        new_model_id = selected_model
        current_model = st.session_state.get("current_model")

        if current_model and current_model != new_model_id:
            try:
                st.session_state["is_loading_session"] = False
                # Iniciar novo chat
                restart_agent(model_id=new_model_id)
            except Exception as e:
                st.sidebar.error(f"Erro ao mudar para {selected_model}: {str(e)}")


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown(
        "<h1 class='main-title'>🎙️ Gerador de Podcast</h1>", unsafe_allow_html=True
    )
    st.markdown(
        "<p class='subtitle'>Criar podcasts de IA envolventes sobre qualquer tópico</p>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Seletor de modelo (filtrar apenas modelos OpenAI)
    ####################################################################
    openai_models = [
        model
        for model in MODELS
        if model in ["gpt-4o", "o3-mini", "gpt-5", "gemini-2.5-pro"]
    ]
    selected_model = st.sidebar.selectbox(
        "Selecionar Modelo",
        options=openai_models,
        index=0,
        key="model_selector",
        on_change=on_model_change,
        help="Apenas modelos OpenAI suportam geração de áudio",
    )

    ####################################################################
    # Inicializar Agente e Sessão
    ####################################################################
    podcast_agent = initialize_agent(selected_model, generate_podcast_agent)
    reset_session_state(podcast_agent)

    if prompt := st.chat_input("💬 Pergunte sobre podcasts ou solicite um tópico específico!"):
        add_message("user", prompt)

    ####################################################################
    # Seleção de Voz
    ####################################################################
    st.sidebar.markdown("#### 🎤 Configurações de Voz")
    voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    selected_voice = st.sidebar.selectbox(
        "Escolher Voz",
        options=voice_options,
        index=0,
        help="Selecionar a voz de IA para seu podcast",
    )

    ####################################################################
    # Tópicos de Exemplo
    ####################################################################
    st.sidebar.markdown("#### 🔥 Tópicos Sugeridos")
    sample_topics = [
        "🎭 Impact of AI on Creativity",
        "💡 Future of Renewable Energy",
        "🏥 AI in Healthcare Revolution",
        "� Space Exploration Updates",
        "🌱 Climate Change Solutions",
        "💻 Quantum Computing Explained",
    ]

    # Handle sample topic selection
    for sample_topic in sample_topics:
        if st.sidebar.button(
            sample_topic, key=f"topic_{sample_topic}", use_container_width=True
        ):
            add_message("user", sample_topic[2:])  # Remove emoji and add to chat
            st.rerun()

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
            if session_id:
                try:
                    session_name = podcast_agent.get_session_name()
                    if session_name:
                        filename = f"podcast_chat_{session_name}.md"
                    else:
                        filename = f"podcast_chat_{session_id}.md"
                except Exception:
                    filename = f"podcast_chat_{session_id}.md"
            else:
                filename = "podcast_chat_new.md"

            if st.sidebar.download_button(
                "💾 Exportar Chat",
                export_chat_history("Podcast Generator"),
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
    # Gerar Podcast
    ####################################################################
    st.sidebar.markdown("#### 🎬 Gerar")

    if st.sidebar.button("🎙️ Criar Podcast", type="primary", use_container_width=True):
        # Obter a última mensagem do usuário como tópico
        user_messages = [
            msg
            for msg in st.session_state.get("messages", [])
            if msg.get("role") == "user"
        ]
        if user_messages:
            latest_topic = user_messages[-1]["content"]
            with st.spinner(
                "⏳ Gerando podcast... Isso pode levar até 2 minutos..."
            ):
                try:
                    audio_path = generate_podcast(
                        latest_topic, selected_voice, selected_model
                    )

                    if audio_path:
                        st.success("✅ Podcast gerado com sucesso!")

                        st.subheader("🎧 Seu Podcast de IA")
                        st.audio(audio_path, format="audio/wav")

                        # Botão de download
                        with open(audio_path, "rb") as audio_file:
                            st.download_button(
                                "⬇️ Baixar Podcast",
                                audio_file,
                                file_name=f"podcast_{latest_topic[:30].replace(' ', '_')}.wav",
                                mime="audio/wav",
                                use_container_width=True,
                            )
                    else:
                        st.error("❌ Falha ao gerar podcast. Por favor, tente novamente.")

                except Exception as e:
                    st.error(f"❌ Erro ao gerar podcast: {str(e)}")
        else:
            st.sidebar.warning("⚠️ Por favor, digite um tópico no chat primeiro.")

    ####################################################################
    # Guia de Introdução
    ####################################################################
    if not st.session_state.get("messages"):
        st.markdown("### 🎯 Como Começar")
        st.markdown("""
        1. **Escolher um Modelo** - Selecione seu modelo de IA preferido
        2. **Escolher uma Voz** - Escolha entre 6 vozes de IA realistas  
        3. **Digitar um Tópico** - Digite o tópico do podcast no chat abaixo ou clique em um tópico sugerido
        4. **Gerar** - Clique em 'Criar Podcast' e aguarde a mágica!
        """)

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
        display_response(podcast_agent, question)

    ####################################################################
    # Session management widgets
    ####################################################################
    session_selector_widget(podcast_agent, selected_model, generate_podcast_agent)

    ####################################################################
    # Seção de Recursos
    ####################################################################
    st.markdown("---")
    st.markdown("### 🌟 Recursos")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **🔬 Pesquisa de IA**
        - Pesquisa de tópico em tempo real
        - Análise de fontes credíveis
        - Coleta de informações mais recentes
        """)

    with col2:
        st.markdown("""
        **📝 Geração de Roteiro**
        - Narrativas envolventes
        - Estrutura profissional
        - Tom conversacional
        """)

    with col3:
        st.markdown("""
        **🎵 Criação de Áudio**
        - 6 vozes de IA realistas
        - Áudio de alta qualidade
        - Download instantâneo
        """)

    ####################################################################
    # Seção sobre
    ####################################################################
    about_section(
        "Este Gerador de Podcast cria podcasts profissionais sobre qualquer tópico usando pesquisa de IA, "
        "escrita de roteiro e tecnologia de texto para fala."
    )


if __name__ == "__main__":
    main()
