import tempfile
from os import unlink

import nest_asyncio
import streamlit as st
from agno.media import Image as AgnoImage
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
from medical_agent import get_medical_imaging_agent

nest_asyncio.apply()
st.set_page_config(
    page_title="Medical Imaging Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)

MODELS = [
    "gemini-2.0-flash-exp",
    "gpt-4o",
]


def restart_agent(model_id: str = None):
    target_model = model_id or st.session_state.get("current_model", MODELS[0])

    new_agent = get_medical_imaging_agent(model_id=target_model, session_id=None)

    st.session_state["agent"] = new_agent
    st.session_state["session_id"] = new_agent.session_id
    st.session_state["messages"] = []
    st.session_state["current_model"] = target_model
    st.session_state["is_new_session"] = True


def on_model_change():
    selected_model = st.session_state.get("model_selector")
    if selected_model:
        if selected_model in MODELS:
            new_model_id = selected_model
            current_model = st.session_state.get("current_model")

            if current_model and current_model != new_model_id:
                try:
                    st.session_state["is_loading_session"] = False
                    # Iniciar novo chat
                    restart_agent(model_id=new_model_id)

                except Exception as e:
                    st.sidebar.error(f"Erro ao mudar para {selected_model}: {str(e)}")
        else:
            st.sidebar.error(f"Modelo desconhecido: {selected_model}")


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown(
        "<h1 class='main-title'>Análise de Imagens Médicas</h1>", unsafe_allow_html=True
    )
    st.markdown(
        "<p class='subtitle'>Análise de imagens médicas alimentada por IA com insights profissionais</p>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Aviso Médico
    ####################################################################
    st.warning(
        "⚠️ **AVISO MÉDICO**: Esta ferramenta é apenas para fins educacionais e informativos. "
        "Todas as análises devem ser revisadas por profissionais de saúde qualificados. "
        "Não tome decisões médicas baseadas apenas nesta análise."
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
    )

    ####################################################################
    # Inicializar Agente e Sessão
    ####################################################################
    medical_agent = initialize_agent(selected_model, get_medical_imaging_agent)
    reset_session_state(medical_agent)

    if prompt := st.chat_input("👋 Envie uma imagem ou pergunte-me sobre imagens médicas!"):
        add_message("user", prompt)

    ####################################################################
    # Upload e Análise de Imagem
    ####################################################################
    st.sidebar.markdown("#### 🖼️ Upload de Imagem")
    uploaded_file = st.sidebar.file_uploader(
        "Enviar Imagem Médica",
        type=["jpg", "jpeg", "png", "dicom", "dcm"],
        help="Formatos suportados: JPG, JPEG, PNG, DICOM",
        key="medical_image_upload",
    )

    additional_context = st.sidebar.text_area(
        "Contexto Adicional",
        placeholder="Histórico do paciente, sintomas, áreas específicas de preocupação...",
        help="Fornecer qualquer informação clínica relevante para melhorar a análise",
    )

    if uploaded_file and not prompt:
        alert = st.sidebar.info("Processing medical image...", icon="🔄")
        try:
            # Process the uploaded image
            with tempfile.NamedTemporaryFile(
                suffix=f".{uploaded_file.name.split('.')[-1]}", delete=False
            ) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            # Read image for AgnoImage
            with open(tmp_path, "rb") as f:
                image_bytes = f.read()

            agno_image = AgnoImage(
                content=image_bytes, format=uploaded_file.name.split(".")[-1]
            )

            # Criar prompt de análise
            base_prompt = (
                "Por favor, analise esta imagem médica e forneça achados abrangentes."
            )
            if additional_context.strip():
                analysis_prompt = (
                    f"{base_prompt}\n\nContexto adicional: {additional_context.strip()}"
                )
            else:
                analysis_prompt = base_prompt

            # Adicionar mensagem e acionar análise
            add_message("user", f"🖼️ Análise de Imagem Médica: {uploaded_file.name}")

            # Armazenar imagem para análise
            st.session_state["pending_image"] = agno_image
            st.session_state["pending_prompt"] = analysis_prompt

            unlink(tmp_path)
            st.sidebar.success(f"Imagem {uploaded_file.name} pronta para análise")

        except Exception as e:
            st.sidebar.error(f"Error processing image: {str(e)}")
        finally:
            alert.empty()

    ###############################################################
    # Perguntas de Exemplo
    ###############################################################
    st.sidebar.markdown("#### ❓ Perguntas de Exemplo")
    if st.sidebar.button("🩻 O que você pode analisar?"):
        add_message(
            "user",
            "Quais tipos de imagens médicas você pode analisar e que insights pode fornecer?",
        )
    if st.sidebar.button("🫁 Guia de Raio-X de Tórax"):
        add_message(
            "user",
            "O que devo procurar ao revisar um raio-X de tórax?",
        )
    if st.sidebar.button("🦴 Análise de Fratura Óssea"):
        add_message(
            "user",
            "Como você identifica e classifica fraturas ósseas em imagens médicas?",
        )
    if st.sidebar.button("🧠 Fundamentos de Neuroimagem"):
        add_message(
            "user",
            "Quais são as estruturas-chave e achados a avaliar em imagens do cérebro?",
        )

    ###############################################################
    # Utility buttons
    ###############################################################
    st.sidebar.markdown("#### 🛠️ Utilities")
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        if st.sidebar.button("🔄 New Chat", use_container_width=True):
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
                    session_name = medical_agent.get_session_name()
                    if session_name:
                        filename = f"medical_imaging_chat_{session_name}.md"
                    else:
                        filename = f"medical_imaging_chat_{session_id}.md"
                except Exception:
                    filename = f"medical_imaging_chat_{session_id}.md"
            else:
                filename = "medical_imaging_chat_new.md"

            if st.sidebar.download_button(
                "💾 Export Chat",
                export_chat_history("Medical Imaging Analysis"),
                file_name=filename,
                mime="text/markdown",
                use_container_width=True,
                help=f"Export {len(st.session_state['messages'])} messages",
            ):
                st.sidebar.success("Chat history exported!")
        else:
            st.sidebar.button(
                "💾 Export Chat",
                disabled=True,
                use_container_width=True,
                help="No messages to export",
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

        # Verificar se temos uma imagem pendente para analisar
        pending_image = st.session_state.get("pending_image")
        pending_prompt = st.session_state.get("pending_prompt")

        if pending_image and pending_prompt:
            # Exibir resposta de análise de imagem
            with st.chat_message("assistant"):
                with st.spinner("🔄 Analisando imagem médica... Por favor, aguarde."):
                    try:
                        response = medical_agent.run(
                            pending_prompt, images=[pending_image]
                        )

                        if hasattr(response, "content"):
                            content = response.content
                        elif isinstance(response, str):
                            content = response
                        elif isinstance(response, dict) and "content" in response:
                            content = response["content"]
                        else:
                            content = str(response)

                        st.markdown(content)
                        add_message("assistant", content)

                    except Exception as e:
                        error_msg = f"Erro ao analisar imagem: {str(e)}"
                        st.error(error_msg)
                        add_message("assistant", error_msg)

            # Limpar dados de imagem pendente
            st.session_state.pop("pending_image", None)
            st.session_state.pop("pending_prompt", None)

        else:
            # Regular text response
            display_response(medical_agent, question)

    ####################################################################
    # Session management widgets
    ####################################################################
    session_selector_widget(medical_agent, selected_model, get_medical_imaging_agent)

    ####################################################################
    # About section
    ####################################################################
    about_section(
        "Este Assistente de Análise de Imagens Médicas ajuda profissionais de saúde e estudantes "
        "a analisar imagens médicas usando insights alimentados por IA, mantendo padrões médicos profissionais."
    )


if __name__ == "__main__":
    main()
