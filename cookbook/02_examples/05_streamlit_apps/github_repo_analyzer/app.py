import nest_asyncio
import streamlit as st
from agents import get_github_agent
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
)

nest_asyncio.apply()
st.set_page_config(
    page_title="GitHub Repository Analyzer",
    page_icon="👨‍💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)


def restart_agent(model_id: str = None):
    target_model = model_id or st.session_state.get("current_model", MODELS[0])

    new_agent = get_github_agent(model_id=target_model, session_id=None)

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
        "<h1 class='main-title'>Analisador de Repositório GitHub</h1>", unsafe_allow_html=True
    )
    st.markdown(
        "<p class='subtitle'>Seu assistente de análise do GitHub inteligente alimentado por Agno</p>",
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
    # Inicializar Agente e Sessão
    ####################################################################
    github_analyzer_agent = initialize_agent(selected_model, get_github_agent)
    reset_session_state(github_analyzer_agent)

    if prompt := st.chat_input("👨‍💻 Pergunte-me sobre repositórios do GitHub!"):
        add_message("user", prompt)

    ####################################################################
    # Configuração do GitHub
    ####################################################################
    st.sidebar.markdown("#### 🔑 Configuração")

    github_token = st.sidebar.text_input(
        "Token de Acesso Pessoal do GitHub",
        type="password",
        help="Opcional: Fornece acesso a repositórios privados e limites de taxa mais altos",
        placeholder="ghp_xxxxxxxxxxxx",
    )

    if github_token:
        st.sidebar.success("✅ Token do GitHub configurado")
    else:
        st.sidebar.info("💡 Adicionar seu token do GitHub para acesso aprimorado")

    st.sidebar.markdown(
        "[Como criar um PAT do GitHub?](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)"
    )

    ###############################################################
    # Perguntas de Exemplo
    ###############################################################
    st.sidebar.markdown("#### ❓ Perguntas de Exemplo")

    if st.sidebar.button("📊 Analisar agno-agi/agno"):
        add_message(
            "user",
            "Analisar o repositório 'agno-agi/agno' - mostrar-me a estrutura, principais linguagens e atividade recente",
        )

    if st.sidebar.button("🔍 Issues Mais Recentes"):
        add_message(
            "user",
            "Mostrar-me as issues mais recentes em 'microsoft/vscode'",
        )

    if st.sidebar.button("📝 Revisar PR Mais Recente"):
        add_message(
            "user",
            "Encontrar e revisar o pull request mais recente em 'facebook/react'",
        )

    if st.sidebar.button("📚 Estatísticas do Repositório"):
        add_message(
            "user",
            "Quais são as estatísticas do repositório para 'tensorflow/tensorflow'?",
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
                    session_name = github_analyzer_agent.get_session_name()
                    if session_name:
                        filename = f"github_analyzer_chat_{session_name}.md"
                    else:
                        filename = f"github_analyzer_chat_{session_id}.md"
                except Exception:
                    filename = f"github_analyzer_chat_{session_id}.md"
            else:
                filename = "github_analyzer_chat_new.md"

            if st.sidebar.download_button(
                "💾 Exportar Chat",
                export_chat_history("GitHub Repository Analyzer"),
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
        display_response(github_analyzer_agent, question)

    ####################################################################
    # About section
    ####################################################################
    about_section(
        "Este Analisador de Repositório GitHub ajuda você a analisar repositórios de código, revisar pull requests e entender estruturas de projeto usando consultas em linguagem natural."
    )


if __name__ == "__main__":
    main()
