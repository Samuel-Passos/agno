import json

import nest_asyncio
import pandas as pd
import streamlit as st
from agents import (
    ArxivSearchResults,
    SearchTerms,
    WebSearchResults,
    get_paperpal_agents,
)
from agno.utils.streamlit import (
    COMMON_CSS,
    MODELS,
    about_section,
    add_message,
    display_chat_messages,
    display_response,
    export_chat_history,
    reset_session_state,
    session_selector_widget,
)

nest_asyncio.apply()
st.set_page_config(
    page_title="Paperpal Research Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)


def get_main_agent(model_id: str = None, session_id: str = None):
    """Get the main research editor agent for session management"""
    agents = get_paperpal_agents(model_id=model_id, session_id=session_id)
    return agents["research_editor"]


def restart_session(model_id: str = None):
    target_model = model_id or st.session_state.get("current_model", MODELS[0])

    # Clear all research-related session state
    keys_to_clear = [
        "research_topic",
        "search_terms",
        "arxiv_results",
        "exa_results",
        "final_blog",
        "research_agents",
        "messages",
        "session_id",
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)

    # Initialize new agents
    st.session_state["research_agents"] = get_paperpal_agents(model_id=target_model)
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
                    restart_session(model_id=new_model_id)
                except Exception as e:
                    st.sidebar.error(f"Error switching to {selected_model}: {str(e)}")
        else:
            st.sidebar.error(f"Unknown model: {selected_model}")


def main():
    ####################################################################
    # App header
    ####################################################################
    st.markdown(
        "<h1 class='main-title'>Assistente de Pesquisa Paperpal</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='subtitle'>Fluxo de trabalho de pesquisa alimentado por IA para geração de blog técnico</p>",
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
    # Inicializar Agentes de Pesquisa
    ####################################################################
    if (
        "research_agents" not in st.session_state
        or not st.session_state["research_agents"]
    ):
        st.session_state["research_agents"] = get_paperpal_agents(
            model_id=selected_model
        )
        st.session_state["current_model"] = selected_model

    # Obter agente principal para gerenciamento de sessão
    main_agent = get_main_agent(selected_model)
    reset_session_state(main_agent)

    if prompt := st.chat_input(
        "💭 Pergunte-me qualquer coisa sobre pesquisa ou inicie um novo projeto de pesquisa!"
    ):
        add_message("user", prompt)

    ####################################################################
    # Configuração de Pesquisa
    ####################################################################
    st.sidebar.markdown("#### 🔍 Configuração de Pesquisa")

    # Entrada de tópico
    research_topic = st.sidebar.text_input(
        "Tópico de Pesquisa",
        value=st.session_state.get("research_topic", ""),
        placeholder="Digite seu tópico de pesquisa...",
        help="Fornecer um tópico de pesquisa específico que você deseja explorar",
    )

    # Opções de pesquisa
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        enable_arxiv = st.sidebar.checkbox(
            "📚 Busca ArXiv", value=True, help="Buscar artigos acadêmicos"
        )
    with col2:
        enable_exa = st.sidebar.checkbox(
            "🌐 Busca Web", value=True, help="Buscar conteúdo web"
        )

    num_search_terms = st.sidebar.number_input(
        "Termos de Busca",
        value=2,
        min_value=2,
        max_value=3,
        help="Número de termos de busca estratégicos a gerar",
    )

    # Botão de gerar pesquisa
    if st.sidebar.button("🚀 Iniciar Pesquisa", type="primary", use_container_width=True):
        if research_topic.strip():
            st.session_state["research_topic"] = research_topic.strip()
            st.session_state["enable_arxiv"] = enable_arxiv
            st.session_state["enable_exa"] = enable_exa
            st.session_state["num_search_terms"] = num_search_terms
            add_message("user", f"🔬 Solicitação de Pesquisa: {research_topic}")
        else:
            st.sidebar.error("Por favor, digite um tópico de pesquisa")

    ####################################################################
    # Tópicos em Tendência
    ####################################################################
    st.sidebar.markdown("#### 🔥 Tópicos em Tendência")
    trending_topics = [
        "Multimodal AI in autonomous systems",
        "Quantum machine learning algorithms",
        "LLM safety and alignment research",
        "Neural symbolic reasoning frameworks",
        "Federated learning in edge computing",
    ]

    for topic in trending_topics:
        if st.sidebar.button(f"📖 {topic}", use_container_width=True):
            st.session_state["research_topic"] = topic
            add_message("user", f"🔬 Research Request: {topic}")

    ###############################################################
    # Botões de utilidade
    ###############################################################
    st.sidebar.markdown("#### 🛠️ Utilitários")
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        if st.sidebar.button("🔄 Nova Pesquisa", use_container_width=True):
            restart_session()
            st.rerun()

    with col2:
        has_messages = (
            st.session_state.get("messages") and len(st.session_state["messages"]) > 0
        )

        if has_messages:
            session_id = st.session_state.get("session_id")
            if session_id:
                try:
                    session_name = main_agent.get_session_name()
                    if session_name:
                        filename = f"paperpal_research_{session_name}.md"
                    else:
                        filename = f"paperpal_research_{session_id}.md"
                except Exception:
                    filename = f"paperpal_research_{session_id}.md"
            else:
                filename = "paperpal_research_new.md"

            if st.sidebar.download_button(
                "💾 Exportar Pesquisa",
                export_chat_history("Paperpal Research"),
                file_name=filename,
                mime="text/markdown",
                use_container_width=True,
                help=f"Exportar {len(st.session_state['messages'])} mensagens",
            ):
                st.sidebar.success("Pesquisa exportada!")
        else:
            st.sidebar.button(
                "💾 Exportar Pesquisa",
                disabled=True,
                use_container_width=True,
                help="Nenhuma pesquisa para exportar",
            )

    ####################################################################
    # Display Chat Messages
    ####################################################################
    display_chat_messages()

    ####################################################################
    # Process Research Request
    ####################################################################
    last_message = (
        st.session_state["messages"][-1] if st.session_state["messages"] else None
    )
    if last_message and last_message.get("role") == "user":
        question = last_message["content"]

        # Check if this is a research request
        if question.startswith("🔬 Research Request:") and st.session_state.get(
            "research_topic"
        ):
            process_research_workflow()
        else:
            # Regular chat interaction
            display_response(main_agent, question)

    ####################################################################
    # Session management widgets
    ####################################################################
    session_selector_widget(main_agent, selected_model, get_main_agent)

    ####################################################################
    # About section
    ####################################################################
    about_section(
        "Paperpal é um assistente de pesquisa alimentado por IA que ajuda você a criar blogs técnicos abrangentes "
        "sintetizando informações de artigos acadêmicos e fontes web."
    )


def process_research_workflow():
    """Processar o fluxo de trabalho de pesquisa completo"""
    topic = st.session_state.get("research_topic")
    if not topic:
        return

    agents = st.session_state.get("research_agents", {})
    if not agents:
        st.error("Agentes de pesquisa não inicializados. Por favor, atualize a página.")
        return

    with st.chat_message("assistant"):
        # Etapa 1: Gerar Termos de Busca
        if not st.session_state.get("search_terms"):
            with st.status(
                "🔍 Gerando termos de busca estratégicos...", expanded=True
            ) as status:
                try:
                    search_input = {
                        "topic": topic,
                        "num_terms": st.session_state.get("num_search_terms", 2),
                    }

                    response = agents["search_term_generator"].run(
                        json.dumps(search_input)
                    )
                    if isinstance(response.content, SearchTerms):
                        st.session_state["search_terms"] = response.content
                        st.json(response.content.model_dump())
                        status.update(
                            label="✅ Termos de busca gerados",
                            state="complete",
                            expanded=False,
                        )
                    else:
                        raise ValueError(
                            "Formato de resposta inválido do gerador de termos de busca"
                        )

                except Exception as e:
                    st.error(f"Erro ao gerar termos de busca: {str(e)}")
                    status.update(
                        label="❌ Geração de termos de busca falhou", state="error"
                    )
                    return

        search_terms = st.session_state.get("search_terms")
        if not search_terms:
            return

        # Etapa 2: Busca ArXiv
        if st.session_state.get("enable_arxiv", True) and not st.session_state.get(
            "arxiv_results"
        ):
            with st.status(
                "📚 Buscando no ArXiv por artigos de pesquisa...", expanded=True
            ) as status:
                try:
                    arxiv_response = agents["arxiv_search_agent"].run(
                        search_terms.model_dump_json(indent=2)
                    )
                    if isinstance(arxiv_response.content, ArxivSearchResults):
                        st.session_state["arxiv_results"] = arxiv_response.content

                        # Display results as table
                        if arxiv_response.content.results:
                            df_data = []
                            for result in arxiv_response.content.results:
                                df_data.append(
                                    {
                                        "Title": result.title[:80] + "..."
                                        if len(result.title) > 80
                                        else result.title,
                                        "Authors": ", ".join(result.authors[:3])
                                        + ("..." if len(result.authors) > 3 else ""),
                                        "ID": result.id,
                                        "Reasoning": result.reasoning[:100] + "..."
                                        if len(result.reasoning) > 100
                                        else result.reasoning,
                                    }
                                )

                            df = pd.DataFrame(df_data)
                            st.dataframe(df, use_container_width=True)
                            status.update(
                                label="✅ Busca ArXiv concluída",
                                state="complete",
                                expanded=False,
                            )

                except Exception as e:
                    st.error(f"Erro na busca ArXiv: {str(e)}")
                    status.update(label="❌ Busca ArXiv falhou", state="error")

        # Etapa 3: Busca Web
        if st.session_state.get("enable_exa", True) and not st.session_state.get(
            "exa_results"
        ):
            with st.status(
                "🌐 Buscando na web por insights atuais...", expanded=True
            ) as status:
                try:
                    exa_response = agents["exa_search_agent"].run(
                        search_terms.model_dump_json(indent=2)
                    )
                    if isinstance(exa_response.content, WebSearchResults):
                        st.session_state["exa_results"] = exa_response.content

                        # Display results
                        if exa_response.content.results:
                            for i, result in enumerate(exa_response.content.results, 1):
                                st.write(f"**{i}. {result.title}**")
                                st.write(
                                    result.summary[:200] + "..."
                                    if len(result.summary) > 200
                                    else result.summary
                                )
                                st.write(f"*Reasoning:* {result.reasoning}")
                                if result.links:
                                    st.write(f"🔗 [Read more]({result.links[0]})")
                                st.write("---")

                            status.update(
                                label="✅ Busca web concluída",
                                state="complete",
                                expanded=False,
                            )

                except Exception as e:
                    st.error(f"Erro na busca web: {str(e)}")
                    status.update(label="❌ Busca web falhou", state="error")

        # Exibir resultados de busca web concluídos
        exa_results = st.session_state.get("exa_results")
        arxiv_results = st.session_state.get("arxiv_results")

        # Etapa 4: Gerar Blog Final
        if (arxiv_results or exa_results) and not st.session_state.get("final_blog"):
            with st.status(
                "📝 Gerando blog de pesquisa abrangente...", expanded=True
            ) as status:
                try:
                    # Preparar conteúdo de pesquisa
                    research_content = f"# Tópico de Pesquisa: {topic}\n\n"
                    research_content += (
                        f"## Termos de Busca\n{search_terms.model_dump_json(indent=2)}\n\n"
                    )

                    if arxiv_results:
                        research_content += "## Artigos de Pesquisa ArXiv\n\n"
                        research_content += (
                            f"{arxiv_results.model_dump_json(indent=2)}\n\n"
                        )

                    if exa_results:
                        research_content += "## Conteúdo de Pesquisa Web\n\n"
                        research_content += (
                            f"{exa_results.model_dump_json(indent=2)}\n\n"
                        )

                    # Gerar blog
                    blog_response = agents["research_editor"].run(research_content)
                    st.session_state["final_blog"] = blog_response.content

                    status.update(
                        label="✅ Blog de pesquisa gerado",
                        state="complete",
                        expanded=False,
                    )

                except Exception as e:
                    st.error(f"Erro na geração do blog: {str(e)}")
                    status.update(label="❌ Geração do blog falhou", state="error")


if __name__ == "__main__":
    main()
