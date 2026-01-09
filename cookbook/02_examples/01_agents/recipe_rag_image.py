"""Exemplo: Agente RAG Multimodal e de Imagem

Um agente que usa Llama 4 para RAG multimodal e OpenAITools para criar um manual visual passo a passo de imagem para uma receita.

Execute: `pip install openai agno groq cohere` para instalar as dependências
"""

import asyncio
from pathlib import Path

from agno.agent import Agent
from agno.knowledge.embedder.cohere import CohereEmbedder
from agno.knowledge.knowledge import Knowledge

# from agno.models.groq import Groq
from agno.tools.openai import OpenAITools
from agno.utils.media import download_image
from agno.vectordb.pgvector import PgVector

knowledge = Knowledge(
    vector_db=PgVector(
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
        table_name="embed_vision_documents",
        embedder=CohereEmbedder(
            id="embed-v4.0",
        ),
    ),
)

asyncio.run(
    knowledge.add_content_async(
        url="https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf",
    )
)

agent = Agent(
    name="EmbedVisionRAGAgent",
    # model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    tools=[OpenAITools()],
    knowledge=knowledge,
    instructions=[
        "Você é um assistente de receitas especializado.",
        "Quando solicitado uma receita:",
        "1. Pesquisar a base de conhecimento para recuperar os detalhes relevantes da receita.",
        "2. Analisar cuidadosamente os passos da receita recuperados.",
        "3. Usar a ferramenta `generate_image` para criar um manual visual passo a passo de imagem para a receita.",
        "4. Apresentar o texto da receita claramente e mencionar que você gerou um manual de imagem acompanhante. Adicionar instruções ao gerar a imagem.",
    ],
    markdown=True,
)

agent.print_response(
    "What is the recipe for a Thai curry?",
)
response = agent.get_last_run_output()

if response.images:
    download_image(response.images[0].url, Path("tmp/recipe_image.png"))
