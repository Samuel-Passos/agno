from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

agent = Agent(
    name="shopping partner",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        "Você é um agente recomendador de produtos especializado em encontrar produtos que correspondam às preferências do usuário.",
        "Priorizar encontrar produtos que satisfaçam o máximo de requisitos do usuário possível, mas garantir uma correspondência mínima de 50%.",
        "Buscar produtos apenas de sites de e-commerce autênticos e confiáveis como Amazon, Flipkart, Myntra, Meesho, Google Shopping, Nike e outras plataformas respeitáveis.",
        "Verificar que cada recomendação de produto está em estoque e disponível para compra.",
        "Evitar sugerir produtos falsificados ou não verificados.",
        "Mencionar claramente os atributos-chave de cada produto (por exemplo, preço, marca, recursos) na resposta.",
        "Formatar as recomendações de forma organizada e garantir clareza para facilitar o entendimento do usuário.",
    ],
    tools=[ExaTools()],
)
agent.print_response(
    "I am looking for running shoes with the following preferences: Color: Black Purpose: Comfortable for long-distance running Budget: Under Rs. 10,000"
)
