from typing import Optional

from agno.agent import Agent
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFImageReader
from agno.tools.openai import OpenAITools
from agno.utils.streamlit import get_model_from_id
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

DEFAULT_RECIPE_URL = "https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"


def get_recipe_image_agent(
    model_id: str = "openai:gpt-4o",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    local_pdf_path: Optional[str] = None,
) -> Agent:
    """Obter um Agente de Geração de Imagem de Receita com Base de Conhecimento"""

    # Escolher a base de conhecimento apropriada
    if local_pdf_path:
        knowledge = Knowledge(
            name="Recipe Knowledge Base",
            description="Coleção de receitas personalizadas enviadas",
            vector_db=PgVector(
                db_url=db_url,
                table_name="recipe_image_documents",
                embedder=OpenAIEmbedder(id="text-embedding-3-small"),
            ),
            max_results=3,
        )
        knowledge.add_content(
            name=f"Receita Enviada: {local_pdf_path.split('/')[-1]}",
            path=local_pdf_path,
            reader=PDFImageReader(),
            description="PDF de receita personalizado enviado",
        )
    else:
        knowledge = Knowledge(
            name="Recipe Knowledge Base",
            description="Coleção de receitas tailandesas com instruções passo a passo",
            vector_db=PgVector(
                db_url=db_url,
                table_name="recipe_image_documents",
                embedder=OpenAIEmbedder(id="text-embedding-3-small"),
            ),
            max_results=3,
        )
        knowledge.add_content(
            name="Thai Recipes Collection",
            url=DEFAULT_RECIPE_URL,
            description="Livro abrangente de receitas tailandesas com pratos tradicionais",
        )

    agent = Agent(
        name="Recipe Image Generator",
        model=get_model_from_id(model_id),
        id="recipe-image-agent",
        user_id=user_id,
        knowledge=knowledge,
        add_history_to_context=True,
        num_history_runs=3,
        session_id=session_id,
        tools=[OpenAITools(image_model="gpt-image-1")],
        instructions="""
            Você é um assistente de receitas especializado que cria guias visuais de culinária.
            
            Quando solicitado uma receita:
            1. **Buscar Base de Conhecimento**: Usar a ferramenta `search_knowledge_base` para encontrar a receita mais relevante
            2. **Formatar Receita**: Extrair e apresentar a receita exatamente neste formato:
            
               ## Ingredientes
               - Listar cada ingrediente com quantidades usando marcadores
               
               ## Instruções  
               1. Instruções numeradas passo a passo
               2. Ser claro e conciso para cada etapa de culinária
               3. Incluir tempos de cozimento e temperaturas quando relevante
               
            3. **Gerar Guia Visual**: Após apresentar a receita, usar a ferramenta `generate_image` com um prompt como:
               '{Nome do Prato}: Um guia visual de culinária passo a passo mostrando todas as etapas de preparação e cozimento em uma vista superior com iluminação natural brilhante. Incluir todos os ingredientes e mostrar a progressão dos ingredientes crus ao prato final servido.'
               
            4. **Manter Qualidade**: 
               - Garantir consistência visual entre imagens
               - Incluir todos os ingredientes e etapas-chave na imagem
               - Usar iluminação brilhante e apetitosa e perspectiva superior
               - Mostrar o processo completo de culinária em uma vista abrangente
               
            5. **Completar a Resposta**: Terminar com 'Geração de receita completa!'
            
            Manter respostas focadas, claras e visualmente atraentes. Sempre buscar na base de conhecimento primeiro antes de responder.
        """,
        markdown=True,
        debug_mode=True,
    )

    return agent
