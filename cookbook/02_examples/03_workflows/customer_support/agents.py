from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from pydantic import BaseModel


class SupportTicketClassification(BaseModel):
    category: str
    priority: str
    tags: List[str]
    summary: str


triage_agent = Agent(
    name="Ticket Classifier",
    model=OpenAIChat(id="gpt-5-mini"),
    instructions="""
    Você é um classificador de tickets de suporte ao cliente. Seu trabalho é analisar consultas de clientes e extrair informações-chave.
    
    Para cada consulta do cliente, fornecer:
    1. Categoria (billing, technical, account_access, product_info, bug_report, feature_request)
    2. Prioridade (low, medium, high, urgent)
    3. Tags/palavras-chave principais (extrair 3-5 termos relevantes)
    4. Resumo breve do problema
    
    Formatar sua resposta como:
    Category: [category]
    Priority: [priority] 
    Tags: [tag1, tag2, tag3]
    Summary: [brief summary]
    """,
    output_schema=SupportTicketClassification,
)

support_agent = Agent(
    name="Solution Developer",
    model=OpenAIChat(id="gpt-5-mini"),
    instructions="""
    Você é um desenvolvedor de soluções para suporte ao cliente. Seu trabalho é criar soluções claras,
    passo a passo para problemas de clientes.
    
    Com base em pesquisa e informações da base de conhecimento, criar:
    1. Diagnóstico claro do problema
    2. Instruções de solução passo a passo
    3. Abordagens alternativas se a solução principal falhar
    4. Dicas de prevenção para o futuro
    
    Tornar soluções amigáveis ao cliente com passos numerados e linguagem clara.
    Incluir quaisquer capturas de tela, links ou recursos adicionais relevantes.
    """,
    markdown=True,
)
