import asyncio

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils.pprint import apprint_run_response

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
)


async def streaming():
    async for response in agent.arun(input="Conte-me uma piada.", stream=True):
        print(response.content, end="", flush=True)


async def streaming_print():
    await agent.aprint_response(input="Conte-me uma piada.", stream=True)


async def streaming_pprint():
    await apprint_run_response(agent.arun(input="Conte-me uma piada.", stream=True))


if __name__ == "__main__":
    asyncio.run(streaming())
    # OU
    asyncio.run(streaming_print())
    # OU
    asyncio.run(streaming_pprint())
