"""📝 Assistente de Escrita Interativo - Exemplo de App CLI

Este exemplo mostra como criar um app CLI interativo com um agente.

Execute `pip install openai agno duckduckgo-search` para instalar as dependências.
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

writing_assistant = Agent(
    name="Writing Assistant",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions=dedent("""\
        Você é um assistente de escrita amigável e profissional! 
        
        Suas capacidades incluem:
        - **Brainstorming**: Ajudar a gerar ideias, tópicos e conceitos criativos
        - **Pesquisa**: Encontrar informações e fatos atuais para apoiar a escrita
        - **Edição**: Melhorar gramática, estilo, clareza e fluxo
        - **Feedback**: Fornecer sugestões construtivas para melhoria
        - **Criação de Conteúdo**: Ajudar a escrever artigos, emails, histórias e mais
        
        Sempre:
        - Fazer perguntas esclarecedoras para entender melhor as necessidades do usuário
        - Fornecer sugestões específicas e acionáveis
        - Manter um tom encorajador e de apoio
        - Usar busca na web quando informações atuais forem necessárias
        - Formatar suas respostas claramente com cabeçalhos e listas quando útil
        
        Iniciar conversas perguntando em qual projeto de escrita estão trabalhando!
        """),
    markdown=True,
)

if __name__ == "__main__":
    print("🔍 Posso pesquisar tópicos, ajudar no brainstorming, editar texto e muito mais!")
    print("✏️ Digite 'exit', 'quit' ou 'bye' para encerrar nossa sessão.\n")

    writing_assistant.cli_app(
        input="Hello! What writing project are you working on today? I'm here to help with brainstorming, research, editing, or any other writing needs you have!",
        user="Writer",
        emoji="✍️",
        stream=True,
    )

    ###########################################################################
    # ASYNC CLI APP
    ###########################################################################
    # import asyncio

    # asyncio.run(writing_assistant.acli_app(
    #     input="Hello! What writing project are you working on today? I'm here to help with brainstorming, research, editing, or any other writing needs you have!",
    #     user="Writer",
    #     emoji="✍️",
    #     stream=True,
    # ))
