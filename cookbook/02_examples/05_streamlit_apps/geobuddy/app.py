import os
import tempfile
from pathlib import Path

import streamlit as st
from agents import analyze_image_location, get_geobuddy_agent
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
    page_title="GeoBuddy",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)


def restart_geobuddy(model_id: str = None):
    """Reiniciar GeoBuddy com novas configurações."""
    target_model = model_id or st.session_state.get("current_model", MODELS[0])

    new_agent = get_geobuddy_agent(
        model_id=target_model,
        session_id=None,
    )

    st.session_state["agent"] = new_agent
    st.session_state["session_id"] = new_agent.session_id
    st.session_state["messages"] = []
    st.session_state["current_model"] = target_model
    st.session_state["is_new_session"] = True


def on_model_change():
    """Lidar com mudanças de modelo."""
    selected_model = st.session_state.get("model_selector")
    if selected_model:
        if selected_model in MODELS:
            current_model = st.session_state.get("current_model")
            if current_model and current_model != selected_model:
                try:
                    st.session_state["is_loading_session"] = False
                    restart_geobuddy(model_id=selected_model)
                except Exception as e:
                    st.sidebar.error(f"Erro ao mudar para {selected_model}: {str(e)}")


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown("<h1 class='main-title'>GeoBuddy</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>Seu detetive geográfico alimentado por IA para identificação de localização</p>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Seletor de modelo
    ####################################################################
    st.sidebar.header("🔧 Configuração")
    selected_model = st.sidebar.selectbox(
        "Selecionar Modelo",
        options=MODELS,
        index=0,
        key="model_selector",
        on_change=on_model_change,
    )

    ####################################################################
    # Barra lateral - Autenticação
    ####################################################################
    st.sidebar.markdown("---")
    st.sidebar.header("🔑 Autenticação")

    if "api_keys" not in st.session_state:
        st.session_state["api_keys"] = {}

    if "gpt" in selected_model.lower() or "openai" in selected_model.lower():
        api_key_label = "Chave de API OpenAI"
        api_key_env = "OPENAI_API_KEY"
        api_key_help = "Definir sua chave de API OpenAI"
    elif "gemini" in selected_model.lower() or "google" in selected_model.lower():
        api_key_label = "Chave de API Google"
        api_key_env = "GOOGLE_API_KEY"
        api_key_help = "Definir sua chave de API Google"
    else:
        api_key_label = "Chave de API OpenAI"  # Padrão para OpenAI
        api_key_env = "OPENAI_API_KEY"
        api_key_help = "Definir sua chave de API OpenAI"

    current_api_key = st.session_state["api_keys"].get(api_key_env, "")

    api_key = st.sidebar.text_input(
        api_key_label,
        value=current_api_key,
        type="password",
        help=api_key_help,
    )

    if api_key:
        st.session_state["api_keys"][api_key_env] = api_key
        os.environ[api_key_env] = api_key
        st.sidebar.success(f"✅ {api_key_label} configurada")
    else:
        st.sidebar.warning(f"⚠️ {api_key_label} necessária")

    ####################################################################
    # Initialize GeoBuddy Agent and Session
    ####################################################################
    geobuddy_agent = initialize_agent(
        selected_model,
        lambda model_id, session_id: get_geobuddy_agent(
            model_id=model_id,
            session_id=session_id,
        ),
    )
    reset_session_state(geobuddy_agent)

    if prompt := st.chat_input(
        "🗺️ Pergunte-me qualquer coisa sobre geografia ou análise de localização!"
    ):
        add_message("user", prompt)

    ####################################################################
    # Seção de Upload de Imagem
    ####################################################################
    st.markdown("### 📷 Análise de Imagem")

    # Criar uma área de upload limpa
    with st.container():
        uploaded_file = st.file_uploader(
            "Escolher uma imagem para analisar",
            type=["jpg", "jpeg", "png", "webp"],
            help="Enviar uma imagem clara com marcos visíveis, arquitetura ou características geográficas",
        )

    if uploaded_file is not None:
        col1, col2 = st.columns([3, 2], gap="large")

        with col1:
            st.markdown("#### 🖼️ Imagem Enviada")
            st.image(
                uploaded_file, caption="Imagem para Análise", use_container_width=True
            )

        with col2:
            st.markdown("#### 🔍 Controles")

            st.markdown("")
            analyze_button = st.button(
                "🌍 Analisar Localização",
                type="primary",
                use_container_width=True,
                help="Clicar para analisar a localização geográfica desta imagem",
            )

            if analyze_button:
                if not api_key:
                    st.error(
                        f"❌ Por favor, forneça sua {api_key_label} na barra lateral primeiro!"
                    )
                else:
                    with st.spinner("🔍 Analisando imagem para pistas geográficas..."):
                        try:
                            # Salvar arquivo enviado temporariamente
                            with tempfile.NamedTemporaryFile(
                                delete=False,
                                suffix=f".{uploaded_file.name.split('.')[-1]}",
                            ) as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_path = Path(tmp_file.name)

                            # Analisar a imagem
                            result = analyze_image_location(geobuddy_agent, tmp_path)

                            # Limpar arquivo temporário
                            tmp_path.unlink()

                            if result:
                                add_message(
                                    "user",
                                    "Por favor, analise esta imagem enviada para identificação de localização geográfica.",
                                )
                                add_message("assistant", result)
                                st.success(
                                    "✅ Análise completa! Verifique os resultados abaixo."
                                )
                                st.rerun()
                            else:
                                st.warning(
                                    "⚠️ Não foi possível analisar a imagem. Por favor, tente uma imagem diferente."
                                )

                        except Exception as e:
                            st.error(f"❌ Erro durante análise: {str(e)}")
                            # Limpar em caso de erro
                            if "tmp_path" in locals() and tmp_path.exists():
                                tmp_path.unlink()

    ####################################################################
    # Opções de Análise de Exemplo
    ####################################################################
    st.sidebar.markdown("#### 🌍 Localizações de Exemplo")

    if st.sidebar.button("🗽 Marcos Famosos"):
        add_message(
            "user",
            "Gostaria de testar GeoBuddy com marcos famosos. Você pode fornecer dicas para analisar fotos de marcos?",
        )

    if st.sidebar.button("🏛️ Estilos Arquitetônicos"):
        add_message(
            "user",
            "Como GeoBuddy pode identificar localizações com base em estilos arquitetônicos? O que devo procurar em edifícios?",
        )

    if st.sidebar.button("🏔️ Características Naturais"):
        add_message(
            "user",
            "Quais características geográficas naturais ajudam GeoBuddy a identificar localizações? Como você analisa paisagens?",
        )

    if st.sidebar.button("🌆 Análise Urbana"):
        add_message(
            "user",
            "Como GeoBuddy analisa ambientes urbanos e características de cidades para identificação de localização?",
        )

    ####################################################################
    # Botões de utilidade
    ####################################################################
    st.sidebar.markdown("#### 🛠️ Utilitários")
    col1, col2 = st.sidebar.columns([1, 1])

    with col1:
        if st.sidebar.button("🔄 Nova Sessão de Análise", use_container_width=True):
            restart_geobuddy()
            st.rerun()

    with col2:
        has_messages = (
            st.session_state.get("messages") and len(st.session_state["messages"]) > 0
        )

        if has_messages:
            session_id = st.session_state.get("session_id")
            if session_id:
                try:
                    session_name = geobuddy_agent.get_session_name()
                    if session_name:
                        filename = f"geobuddy_analysis_{session_name}.md"
                    else:
                        filename = f"geobuddy_analysis_{session_id}.md"
                except Exception:
                    filename = f"geobuddy_analysis_{session_id}.md"
            else:
                filename = "geobuddy_analysis_new.md"

            if st.sidebar.download_button(
                "💾 Exportar Análise",
                export_chat_history("GeoBuddy"),
                file_name=filename,
                mime="text/markdown",
                use_container_width=True,
                help=f"Exportar {len(st.session_state['messages'])} resultados de análise",
            ):
                st.sidebar.success("Análise exportada!")
        else:
            st.sidebar.button(
                "💾 Exportar Análise",
                disabled=True,
                use_container_width=True,
                help="Nenhuma análise para exportar",
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
        display_response(geobuddy_agent, question)

    ####################################################################
    # Session management widgets
    ####################################################################
    session_selector_widget(
        geobuddy_agent,
        selected_model,
        lambda model_id, session_id: get_geobuddy_agent(
            model_id=model_id,
            session_id=session_id,
        ),
    )

    ####################################################################
    # About section
    ####################################################################
    about_section(
        "Este agente GeoBuddy analisa imagens para prever localizações geográficas usando análise visual avançada de marcos, arquitetura e pistas culturais."
    )


if __name__ == "__main__":
    main()
