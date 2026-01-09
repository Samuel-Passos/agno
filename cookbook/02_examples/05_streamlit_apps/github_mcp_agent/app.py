import asyncio
import os

import streamlit as st
from agents import run_github_agent
from agno.utils.streamlit import (
    COMMON_CSS,
    MODELS,
    about_section,
    add_message,
    display_chat_messages,
    export_chat_history,
)

st.set_page_config(
    page_title="GitHub MCP Agent",
    page_icon="🐙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)


def restart_agent():
    """Redefinir a sessão do agente"""
    st.session_state["messages"] = []
    st.session_state["is_new_session"] = True


def on_model_change():
    """Lidar com mudança de seleção de modelo"""
    selected_model = st.session_state.get("model_selector")
    if selected_model:
        if selected_model in MODELS:
            current_model = st.session_state.get("current_model")
            if current_model and current_model != selected_model:
                st.session_state["current_model"] = selected_model
                restart_agent()
        else:
            st.sidebar.error(f"Modelo desconhecido: {selected_model}")


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown("<h1 class='main-title'>Agente GitHub MCP</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>Explore repositórios do GitHub com linguagem natural usando o Model Context Protocol</p>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Barra lateral - Autenticação
    ####################################################################
    st.sidebar.header("🔑 Autenticação")
    github_token = st.sidebar.text_input(
        "Token do GitHub",
        type="password",
        help="Criar um token com escopo repo em github.com/settings/tokens",
    )

    if github_token:
        os.environ["GITHUB_TOKEN"] = github_token
        st.sidebar.success("✅ Token do GitHub configurado")
    else:
        st.sidebar.warning("⚠️ Token do GitHub necessário")

    ####################################################################
    # Seletor de modelo
    ####################################################################
    st.sidebar.markdown("---")
    selected_model = st.sidebar.selectbox(
        "Selecionar Modelo",
        options=MODELS,
        index=0,
        key="model_selector",
        on_change=on_model_change,
    )

    ####################################################################
    # Entrada de Repositório e Consulta
    ####################################################################
    col1, col2 = st.columns([3, 1])

    with col1:
        repo = st.text_input(
            "Repositório", value="agno-agi/agno", help="Formato: owner/repo", key="repo"
        )

    with col2:
        st.selectbox(
            "Tipo de Consulta",
            ["Issues", "Pull Requests", "Atividade do Repositório", "Personalizado"],
            key="query_type",
        )

    ####################################################################
    # Perguntas de Exemplo
    ####################################################################
    st.sidebar.markdown("#### ❓ Perguntas de Exemplo")
    if st.sidebar.button("🔍 Issues por rótulo"):
        add_message("user", f"Mostrar-me issues por rótulo em {repo}")
    if st.sidebar.button("📝 PRs Recentes"):
        add_message("user", f"Mostrar-me PRs mesclados recentes em {repo}")
    if st.sidebar.button("📊 Saúde do repositório"):
        add_message("user", f"Mostrar métricas de saúde do repositório para {repo}")

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
            if st.sidebar.download_button(
                "💾 Exportar Chat",
                export_chat_history("GitHub Agent"),
                file_name=f"github_mcp_chat_{repo.replace('/', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
            ):
                st.sidebar.success("Histórico de chat exportado!")

    # Seção sobre
    about_section(
        "Este Agente GitHub MCP ajuda você a analisar repositórios usando consultas em linguagem natural."
    )

    ####################################################################
    # Entrada de chat e processamento
    ####################################################################
    if prompt := st.chat_input("Pergunte-me qualquer coisa sobre este repositório do GitHub!"):
        add_message("user", prompt)

    ####################################################################
    # Processar entrada do usuário ou consultas de botão
    ####################################################################
    if st.session_state.get("messages"):
        last_message = st.session_state["messages"][-1]
        if last_message["role"] == "user":
            user_query = last_message["content"]

            # Garantir que repo seja mencionado na consulta
            if repo and repo not in user_query:
                full_query = f"{user_query} em {repo}"
            else:
                full_query = user_query

            with st.spinner("Analisando repositório do GitHub..."):
                try:
                    result = asyncio.run(run_github_agent(full_query, selected_model))
                    add_message("assistant", result)
                except Exception as e:
                    error_msg = f"Erro: {str(e)}"
                    add_message("assistant", error_msg)
            st.rerun()

    ####################################################################
    # Display chat messages
    ####################################################################
    display_chat_messages()


if __name__ == "__main__":
    main()
