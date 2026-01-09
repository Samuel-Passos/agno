import chainlit as cl
from agno.agent import Agent
from agno.db.in_memory import InMemoryDb
from agno.models.openai.chat import OpenAIChat

# Variáveis globais
agent = None


@cl.on_chat_start
async def on_chat_start():
    """Inicializar o agente quando uma nova sessão de chat começa."""
    # Criar um banco de dados único por sessão
    db = InMemoryDb()

    agent = Agent(
        model=OpenAIChat(
            id="gpt-4o",
        ),
        db=db,
        add_history_to_context=True,
        num_history_runs=5,
        stream=True,
        markdown=True,
        telemetry=False,
    )

    # Armazenar o agente na sessão
    cl.user_session.set("agent", agent)


@cl.on_message
async def on_message(message: cl.Message):
    # Obter o agente da sessão
    agent = cl.user_session.get("agent")

    response_msg = cl.Message(content="")
    await response_msg.send()

    async for event in agent.arun(message.content, stream=True):
        response_msg.content += event.content
        await response_msg.update()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
