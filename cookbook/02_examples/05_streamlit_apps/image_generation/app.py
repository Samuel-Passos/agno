import io
import tempfile
from os import unlink

import nest_asyncio
import streamlit as st
from agents import get_recipe_image_agent
from agno.utils.streamlit import (
    COMMON_CSS,
    MODELS,
    about_section,
    add_message,
    display_chat_messages,
    display_tool_calls,
    export_chat_history,
    initialize_agent,
    knowledge_base_info_widget,
    reset_session_state,
    session_selector_widget,
)
from PIL import Image

nest_asyncio.apply()
st.set_page_config(
    page_title="Recipe Image Generator",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown(COMMON_CSS, unsafe_allow_html=True)


def restart_agent(model_id: str = None):
    target_model = model_id or st.session_state.get("current_model", MODELS[0])

    new_agent = get_recipe_image_agent(model_id=target_model, session_id=None)

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
        "<h1 class='main-title'>Gerador de Imagem de Receita</h1>", unsafe_allow_html=True
    )
    st.markdown(
        "<p class='subtitle'>Seu companheiro de culinária de IA - Envie receitas ou use padrões, depois obtenha guias visuais passo a passo de culinária!</p>",
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
    recipe_image_agent = initialize_agent(selected_model, get_recipe_image_agent)
    reset_session_state(recipe_image_agent)

    if prompt := st.chat_input("👋 Pergunte-me uma receita (ex: 'Receita de Pad Thai')"):
        add_message("user", prompt)

    ####################################################################
    # Gerenciamento de Receitas
    ####################################################################
    st.sidebar.markdown("#### 📚 Gerenciamento de Receitas")
    knowledge_base_info_widget(recipe_image_agent)

    # Upload de arquivo
    uploaded_file = st.sidebar.file_uploader(
        "Enviar PDF de Receita (.pdf)", type=["pdf"], key="recipe_upload"
    )
    if uploaded_file and not prompt:
        alert = st.sidebar.info("Processando PDF de receita...", icon="ℹ️")
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            recipe_image_agent.knowledge.add_content(
                name=f"Receita Enviada: {uploaded_file.name}",
                path=tmp_path,
                description=f"PDF de receita personalizado: {uploaded_file.name}",
            )

            unlink(tmp_path)
            st.sidebar.success(f"{uploaded_file.name} adicionado à coleção de receitas")
        except Exception as e:
            st.sidebar.error(f"Erro ao processar PDF de receita: {str(e)}")
        finally:
            alert.empty()

    if st.sidebar.button("Limpar Coleção de Receitas"):
        if recipe_image_agent.knowledge.vector_db:
            recipe_image_agent.knowledge.vector_db.delete()
        st.sidebar.success("Coleção de receitas limpa")

    ###############################################################
    # Receitas de Exemplo
    ###############################################################
    st.sidebar.markdown("#### 🍜 Receitas de Exemplo")
    if st.sidebar.button("🍝 Receita de Pad Thai"):
        add_message("user", "Receita de Pad Thai com passos visuais")
    if st.sidebar.button("🥗 Receita de Som Tum"):
        add_message("user", "Receita de Som Tum (Salada de Mamão)")
    if st.sidebar.button("🍲 Receita de Tom Kha Gai"):
        add_message("user", "Receita de sopa Tom Kha Gai")

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
                    session_name = recipe_image_agent.get_session_name()
                    if session_name:
                        filename = f"recipe_chat_{session_name}.md"
                    else:
                        filename = f"recipe_chat_{session_id}.md"
                except Exception:
                    filename = f"recipe_chat_{session_id}.md"
            else:
                filename = "recipe_chat_new.md"

            if st.sidebar.download_button(
                "💾 Exportar Chat",
                export_chat_history("Recipe Image Generator"),
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
    # Generate response for user message with image handling
    ####################################################################
    last_message = (
        st.session_state["messages"][-1] if st.session_state["messages"] else None
    )
    if last_message and last_message.get("role") == "user":
        question = last_message["content"]

        with st.chat_message("assistant"):
            tool_calls_container = st.empty()
            resp_container = st.empty()
            with st.spinner("🤔 Thinking..."):
                response = ""
                try:
                    # Run the agent and stream the response
                    run_response = recipe_image_agent.run(question, stream=True)
                    for resp_chunk in run_response:
                        try:
                            # Display tool calls if available
                            if hasattr(resp_chunk, "tool") and resp_chunk.tool:
                                display_tool_calls(
                                    tool_calls_container, [resp_chunk.tool]
                                )
                        except Exception:
                            pass

                        if resp_chunk.content is not None:
                            content = str(resp_chunk.content)
                            if not (
                                content.strip().endswith("completed in")
                                or "completed in" in content
                                and "s." in content
                            ):
                                response += content
                                resp_container.markdown(response)

                        if hasattr(resp_chunk, "images") and getattr(
                            resp_chunk, "images", None
                        ):
                            captured_run_output = resp_chunk

                    # Display generated images
                    if captured_run_output and hasattr(captured_run_output, "images"):
                        for i, img in enumerate(captured_run_output.images or []):
                            try:
                                if hasattr(img, "content") and img.content:
                                    image = Image.open(io.BytesIO(img.content))
                                    st.image(
                                        image,
                                        caption=f"Guia de culinária passo a passo {i + 1}",
                                        use_container_width=True,
                                    )
                                elif hasattr(img, "url") and img.url:
                                    st.image(
                                        img.url,
                                        caption=f"Guia de culinária passo a passo {i + 1}",
                                        use_container_width=True,
                                    )
                            except Exception as img_error:
                                st.warning(
                                    f"Não foi possível exibir imagem {i + 1}: {str(img_error)}"
                                )

                    # Add message with tools
                    try:
                        if captured_run_output and hasattr(
                            captured_run_output, "tools"
                        ):
                            add_message(
                                "assistant", response, captured_run_output.tools
                            )
                        else:
                            add_message("assistant", response)
                    except Exception:
                        add_message("assistant", response)

                except Exception as e:
                    error_message = f"Desculpe, encontrei um erro: {str(e)}"
                    add_message("assistant", error_message)
                    st.error(error_message)

    ####################################################################
    # Session management widgets
    ####################################################################
    session_selector_widget(recipe_image_agent, selected_model, get_recipe_image_agent)

    ####################################################################
    # About section
    ####################################################################
    about_section(
        "Este Gerador de Imagem de Receita cria guias visuais passo a passo de culinária a partir de coleções de receitas. Envie suas próprias receitas ou use a coleção de receitas tailandesas integrada."
    )


if __name__ == "__main__":
    main()
