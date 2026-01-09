import asyncio

import nest_asyncio
import streamlit as st
from agno.utils.streamlit import (
    COMMON_CSS,
    MODELS,
    about_section,
    add_message,
    display_chat_messages,
    display_tool_calls,
    export_chat_history,
    initialize_agent,
    reset_session_state,
    session_selector_widget,
)
from mcp_client import MCPClient, MCPServerConfig

from mcp_agent import get_mcp_agent

nest_asyncio.apply()
st.set_page_config(
    page_title="Universal MCP Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)

# MCP Server configurations
MCP_SERVERS = {
    "GitHub": MCPServerConfig(
        id="github", command="npx", args=["-y", "@modelcontextprotocol/server-github"]
    ),
}


async def initialize_mcp_client(server_config: MCPServerConfig):
    """Inicializar cliente MCP e conectar ao servidor."""
    try:
        if (
            "mcp_client" not in st.session_state
            or st.session_state.get("mcp_server_id") != server_config.id
            or getattr(st.session_state.get("mcp_client", None), "session", None)
            is None
        ):
            # Initialize new MCP client
            st.session_state["mcp_client"] = MCPClient()

        mcp_client = st.session_state["mcp_client"]
        mcp_tools = await mcp_client.connect_to_server(server_config)
        st.session_state["mcp_server_id"] = server_config.id

        return mcp_tools
    except Exception as e:
        st.error(f"Falha ao conectar ao servidor MCP {server_config.id}: {str(e)}")
        return None


def restart_agent(model_id: str = None, mcp_server: str = None):
    """Reiniciar agente com nova configuração."""
    target_model = model_id or st.session_state.get("current_model", MODELS[0])
    target_server = mcp_server or st.session_state.get("current_mcp_server", "GitHub")

    # Clear MCP client to force reconnection
    if "mcp_client" in st.session_state:
        del st.session_state["mcp_client"]

    st.session_state["current_model"] = target_model
    st.session_state["current_mcp_server"] = target_server
    st.session_state["messages"] = []
    st.session_state["is_new_session"] = True


def on_model_change():
    """Lidar com mudança de seleção de modelo."""
    selected_model = st.session_state.get("model_selector")
    if selected_model:
        if selected_model in MODELS:
            current_model = st.session_state.get("current_model")
            if current_model and current_model != selected_model:
                try:
                    restart_agent(model_id=selected_model)
                except Exception as e:
                    st.sidebar.error(f"Erro ao mudar para {selected_model}: {str(e)}")
        else:
            st.sidebar.error(f"Modelo desconhecido: {selected_model}")


def on_mcp_server_change():
    """Lidar com mudança de seleção de servidor MCP."""
    selected_server = st.session_state.get("mcp_server_selector")
    if selected_server:
        current_server = st.session_state.get("current_mcp_server", "GitHub")
        if current_server != selected_server:
            try:
                restart_agent(mcp_server=selected_server)
            except Exception as e:
                st.sidebar.error(f"Erro ao mudar para {selected_server}: {str(e)}")


async def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown(
        "<h1 class='main-title'>Agente MCP Universal</h1>", unsafe_allow_html=True
    )
    st.markdown(
        "<p class='subtitle'>Sua interface inteligente para servidores MCP alimentada por Agno</p>",
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
    # Seletor de servidor MCP
    ####################################################################
    selected_mcp_server = st.sidebar.selectbox(
        "Selecionar Servidor MCP",
        options=list(MCP_SERVERS.keys()),
        index=0,
        key="mcp_server_selector",
        on_change=on_mcp_server_change,
    )

    # Get current server configuration
    current_server = st.session_state.get("current_mcp_server", selected_mcp_server)
    server_config = MCP_SERVERS[current_server]

    ####################################################################
    # Initialize MCP Client and Tools
    ####################################################################
    mcp_tools = await initialize_mcp_client(server_config)
    if not mcp_tools:
        st.error("Falha ao inicializar servidor MCP. Por favor, verifique a configuração.")
        return

    ####################################################################
    # Initialize Agent
    ####################################################################
    def create_agent(model_id: str, session_id: str = None):
        return get_mcp_agent(
            model_id=model_id,
            session_id=session_id,
            mcp_tools=[mcp_tools],
            mcp_server_ids=[server_config.id],
        )

    mcp_agent = initialize_agent(selected_model, create_agent)

    # Update agent tools if they've changed
    if hasattr(mcp_agent, "tools"):
        mcp_agent.tools = [mcp_tools]

    reset_session_state(mcp_agent)

    if prompt := st.chat_input("✨ Como posso ajudá-lo com MCP?"):
        add_message("user", prompt)

    ####################################################################
    # Informações do Servidor MCP
    ####################################################################
    st.sidebar.markdown("#### 🔗 Informações do Servidor MCP")
    st.sidebar.info(f"**Conectado a:** {server_config.id}")
    st.sidebar.info(f"**Comando:** {server_config.command}")
    if server_config.args:
        st.sidebar.info(f"**Argumentos:** {' '.join(server_config.args)}")

    ####################################################################
    # Perguntas de Exemplo
    ####################################################################
    st.sidebar.markdown("#### ❓ Perguntas de Exemplo")

    if current_server == "GitHub":
        if st.sidebar.button("🔍 Buscar repositórios"):
            add_message("user", "Buscar repositórios relacionados a machine learning")
        if st.sidebar.button("📊 Informações do repositório"):
            add_message("user", "Conte-me sobre um repositório Python popular")
        if st.sidebar.button("🗂️ Listar issues"):
            add_message("user", "Mostrar-me issues recentes em um repositório")

    elif current_server == "Filesystem":
        if st.sidebar.button("📁 Listar arquivos"):
            add_message("user", "Listar arquivos no diretório atual")
        if st.sidebar.button("📄 Ler arquivo"):
            add_message("user", "Mostrar-me o conteúdo de um arquivo de texto")
        if st.sidebar.button("✍️ Criar arquivo"):
            add_message("user", "Criar um novo arquivo com algum conteúdo de exemplo")

    if st.sidebar.button("❓ O que é MCP?"):
        add_message("user", "O que é o Model Context Protocol e como funciona?")

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
            if session_id and mcp_agent.get_session_name():
                filename = f"mcp_agent_chat_{mcp_agent.get_session_name()}.md"
            elif session_id:
                filename = f"mcp_agent_chat_{session_id}.md"
            else:
                filename = "mcp_agent_chat_new.md"

            if st.sidebar.download_button(
                "💾 Exportar Chat",
                export_chat_history("Universal MCP Agent"),
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

        # Custom response handling for MCP agent (async)
        with st.chat_message("assistant"):
            tool_calls_container = st.empty()
            resp_container = st.empty()
            with st.spinner("🤔 Thinking..."):
                response = ""
                try:
                    # Run the agent asynchronously and stream the response
                    async for resp_chunk in mcp_agent.arun(question, stream=True):
                        try:
                            # Display tool calls if available
                            if hasattr(resp_chunk, "tool") and resp_chunk.tool:
                                display_tool_calls(
                                    tool_calls_container, [resp_chunk.tool]
                                )
                        except Exception:
                            pass  # Continue even if tool display fails

                        if resp_chunk.content is not None:
                            content = str(resp_chunk.content)
                            if not (
                                content.strip().endswith("completed in")
                                or "completed in" in content
                                and "s." in content
                            ):
                                response += content
                                resp_container.markdown(response)

                    if resp_chunk and hasattr(resp_chunk, "tools") and resp_chunk.tools:
                        add_message("assistant", response, resp_chunk.tools)
                    else:
                        add_message("assistant", response)

                except Exception as e:
                    st.error(f"Desculpe, encontrei um erro: {str(e)}")

    ####################################################################
    # Session management widgets
    ####################################################################
    session_selector_widget(mcp_agent, selected_model, create_agent)

    ####################################################################
    # About section
    ####################################################################
    about_section(
        "Este Agente MCP Universal fornece uma interface unificada para interagir com servidores MCP, permitindo acesso perfeito a várias fontes de dados e ferramentas."
    )


def run_app():
    """Executar o aplicativo streamlit assíncrono."""
    asyncio.run(main())


if __name__ == "__main__":
    run_app()
