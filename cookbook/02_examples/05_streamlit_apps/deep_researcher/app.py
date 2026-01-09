import nest_asyncio
import streamlit as st
from agents import get_deep_researcher_workflow
from agno.utils.streamlit import (
    COMMON_CSS,
    about_section,
    add_message,
    display_chat_messages,
    export_chat_history,
)

nest_asyncio.apply()
st.set_page_config(
    page_title="Deep Researcher",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown("<h1 class='main-title'>Pesquisador Profundo</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>Seu assistente de pesquisa alimentado por IA com workflow multi-agente</p>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Initialize Workflow
    ####################################################################
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if prompt := st.chat_input("🔎 Sobre o que você gostaria que eu pesquisasse?"):
        add_message("user", prompt)

    ####################################################################
    # Configuração de API
    ####################################################################
    st.sidebar.markdown("#### 🔑 Configuração")

    nebius_api_key = st.sidebar.text_input(
        "Chave de API Nebius",
        type="password",
        help="Necessária para alimentar os agentes de pesquisa",
        placeholder="nebius_xxxxxxxxxxxx",
    )

    scrapegraph_api_key = st.sidebar.text_input(
        "Chave de API ScrapeGraph",
        type="password",
        help="Necessária para web scraping e extração de conteúdo",
        placeholder="sgai_xxxxxxxxxxxx",
    )

    if nebius_api_key and scrapegraph_api_key:
        st.sidebar.success("✅ Chaves de API configuradas")
    else:
        st.sidebar.warning("⚠️ Por favor, configure suas chaves de API para começar a pesquisar")

    ###############################################################
    # Tópicos de Pesquisa de Exemplo
    ###############################################################
    st.sidebar.markdown("#### 🔍 Tópicos de Exemplo")

    if st.sidebar.button("🚀 Desenvolvimentos de IA e ML 2024"):
        add_message("user", "Últimos desenvolvimentos em IA e aprendizado de máquina em 2024")

    if st.sidebar.button("🌱 Energia Sustentável"):
        add_message("user", "Tendências atuais em tecnologias de energia sustentável")

    if st.sidebar.button("💊 Medicina Personalizada"):
        add_message(
            "user", "Descobertas recentes em medicina personalizada e genômica"
        )

    if st.sidebar.button("🔒 Cibersegurança Quântica"):
        add_message("user", "Impacto da computação quântica na cibersegurança")

    ###############################################################
    # Botões de utilidade
    ###############################################################
    st.sidebar.markdown("#### 🛠️ Utilitários")
    col1, col2 = st.sidebar.columns([1, 1])

    with col1:
        if st.sidebar.button("🔄 Nova Pesquisa", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

    with col2:
        has_messages = (
            st.session_state.get("messages") and len(st.session_state["messages"]) > 0
        )

        if has_messages:
            if st.sidebar.download_button(
                "💾 Exportar Relatório",
                export_chat_history("Deep Research Report"),
                file_name="research_report.md",
                mime="text/markdown",
                use_container_width=True,
                help=f"Exportar {len(st.session_state['messages'])} mensagens",
            ):
                st.sidebar.success("Relatório de pesquisa exportado!")
        else:
            st.sidebar.button(
                "💾 Exportar Relatório",
                disabled=True,
                use_container_width=True,
                help="Nenhuma pesquisa para exportar",
            )

    ####################################################################
    # Display Chat Messages
    ####################################################################
    display_chat_messages()

    ####################################################################
    # Generate research response
    ####################################################################
    last_message = (
        st.session_state["messages"][-1] if st.session_state["messages"] else None
    )
    if last_message and last_message.get("role") == "user":
        if not (nebius_api_key and scrapegraph_api_key):
            st.error(
                "🔑 Por favor, configure suas chaves de API na barra lateral para começar a pesquisa."
            )
            return

        research_topic = last_message["content"]

        with st.chat_message("assistant"):
            # Criar containers para diferentes fases
            response_container = st.empty()

            try:
                # Obter o workflow
                app = get_deep_researcher_workflow()

                # Executar o workflow de pesquisa com atualizações de status
                with st.status(
                    "🔎 Executando workflow de pesquisa...", expanded=True
                ) as status:
                    status.write(
                        "🧠 **Fase 1: Pesquisando** - Encontrando e extraindo informações relevantes..."
                    )
                    status.write(
                        "📊 **Fase 2: Analisando** - Sintetizando e interpretando as descobertas da pesquisa..."
                    )
                    status.write(
                        "📝 **Fase 3: Escrevendo** - Criando o relatório final..."
                    )

                    result = app.run(topic=research_topic)

                    full_report = ""
                    if result and result.content:
                        full_report = result.content
                        response_container.markdown(full_report)
                    else:
                        full_report = (
                            "❌ Falha ao gerar relatório de pesquisa. Por favor, tente novamente."
                        )
                        response_container.markdown(full_report)

                    status.update(label="✅ Pesquisa concluída!", state="complete")

                # Adicionar a resposta completa às mensagens
                add_message("assistant", full_report)

            except Exception as e:
                st.error(f"❌ Pesquisa falhou: {str(e)}")
                st.info("💡 Por favor, verifique suas chaves de API e tente novamente.")

    ####################################################################
    # About section
    ####################################################################
    about_section(
        "Este Pesquisador Profundo usa um workflow multi-agente para conduzir pesquisa abrangente, análise e geração de relatórios. Construído com Agno, ScrapeGraph e Nebius AI."
    )


if __name__ == "__main__":
    main()
