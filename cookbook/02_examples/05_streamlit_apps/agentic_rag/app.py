import tempfile
from os import unlink

import nest_asyncio
import streamlit as st
from agentic_rag import get_agentic_rag_agent
from agno.utils.streamlit import (
    COMMON_CSS,
    MODELS,
    about_section,
    add_message,
    display_chat_messages,
    display_response,
    export_chat_history,
    initialize_agent,
    knowledge_base_info_widget,
    reset_session_state,
    session_selector_widget,
)

nest_asyncio.apply()
st.set_page_config(
    page_title="Agentic RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)


def restart_agent(model_id: str = None):
    target_model = model_id or st.session_state.get("current_model", MODELS[0])

    new_agent = get_agentic_rag_agent(model_id=target_model, session_id=None)

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
                    # Start new chat
                    restart_agent(model_id=new_model_id)

                except Exception as e:
                    st.sidebar.error(f"Error switching to {selected_model}: {str(e)}")
        else:
            st.sidebar.error(f"Unknown model: {selected_model}")


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown("<h1 class='main-title'>Agentic RAG</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>Seu Agente RAG inteligente alimentado por Agno</p>",
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
    )

    ####################################################################
    # Initialize Agent and Session
    ####################################################################
    agentic_rag_agent = initialize_agent(selected_model, get_agentic_rag_agent)
    reset_session_state(agentic_rag_agent)

    if prompt := st.chat_input("👋 Pergunte-me qualquer coisa!"):
        add_message("user", prompt)

    ####################################################################
    # Gerenciamento de Documentos
    ####################################################################
    st.sidebar.markdown("#### 📚 Gerenciamento de Documentos")
    knowledge_base_info_widget(agentic_rag_agent)

    # Entrada de URL
    input_url = st.sidebar.text_input("Adicionar URL à Base de Conhecimento")
    if input_url and not prompt:
        alert = st.sidebar.info("Processando URL...", icon="ℹ️")
        try:
            agentic_rag_agent.knowledge.add_content(
                name=f"URL: {input_url}",
                url=input_url,
                description=f"Conteúdo de {input_url}",
            )
            st.sidebar.success("URL adicionada à base de conhecimento")
        except Exception as e:
            st.sidebar.error(f"Erro ao processar URL: {str(e)}")
        finally:
            alert.empty()

    # Upload de arquivo
    uploaded_file = st.sidebar.file_uploader(
        "Adicionar um Documento (.pdf, .csv ou .txt)", key="file_upload"
    )
    if uploaded_file and not prompt:
        alert = st.sidebar.info("Processando documento...", icon="ℹ️")
        try:
            with tempfile.NamedTemporaryFile(
                suffix=f".{uploaded_file.name.split('.')[-1]}", delete=False
            ) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            agentic_rag_agent.knowledge.add_content(
                name=uploaded_file.name,
                path=tmp_path,
                description=f"Arquivo enviado: {uploaded_file.name}",
            )

            unlink(tmp_path)
            st.sidebar.success(f"{uploaded_file.name} adicionado à base de conhecimento")
        except Exception as e:
            st.sidebar.error(f"Erro ao processar arquivo: {str(e)}")
        finally:
            alert.empty()

    if st.sidebar.button("Limpar Base de Conhecimento"):
        if agentic_rag_agent.knowledge.vector_db:
            agentic_rag_agent.knowledge.vector_db.delete()
        st.sidebar.success("Base de conhecimento limpa")

    ###############################################################
    # Pergunta de Exemplo
    ###############################################################
    st.sidebar.markdown("#### ❓ Perguntas de Exemplo")
    if st.sidebar.button("🖼️ O que você pode fazer?"):
        add_message(
            "user",
            "O que você pode fazer?",
        )
    if st.sidebar.button("📝 Resumir"):
        add_message(
            "user",
            "Você pode resumir o que está atualmente na base de conhecimento (usar a ferramenta `search_knowledge_base`)?",
        )
    if st.sidebar.button("🔍 O que é Agentic RAG?"):
        add_message(
            "user",
            "O que é Agentic RAG?",
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
            if session_id and agentic_rag_agent.get_session_name():
                filename = f"agentic_rag_chat_{agentic_rag_agent.get_session_name()}.md"
            elif session_id:
                filename = f"agentic_rag_chat_{session_id}.md"
            else:
                filename = "agentic_rag_chat_new.md"

            if st.sidebar.download_button(
                "💾 Exportar Chat",
                export_chat_history("Agentic RAG"),
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
    # Exibir Mensagens do Chat
    ####################################################################
    display_chat_messages()

    ####################################################################
    # Gerar resposta para mensagem do usuário
    ####################################################################
    last_message = (
        st.session_state["messages"][-1] if st.session_state["messages"] else None
    )
    if last_message and last_message.get("role") == "user":
        question = last_message["content"]
        display_response(agentic_rag_agent, question)

    ####################################################################
    # Widgets de gerenciamento de sessão
    ####################################################################
    session_selector_widget(agentic_rag_agent, selected_model, get_agentic_rag_agent)

    ####################################################################
    # Seção sobre
    ####################################################################
    about_section(
        "Este Assistente Agentic RAG ajuda você a analisar documentos e conteúdo web usando consultas em linguagem natural."
    )


main()
