from pathlib import Path
from textwrap import dedent

from agno.agent import Agent, RunOutput
from agno.models.google import Gemini
from agno.tools.nano_banana import NanoBananaTools
from db import gemini_agents_db

creative_studio_agent = Agent(
    name="Creative Studio Agent",
    model=Gemini(id="gemini-3-flash-preview"),
    tools=[NanoBananaTools(model="gemini-2.5-flash-image")],
    instructions=dedent("""\
    Você é um agente de geração de imagens criativas.
    Sua tarefa é transformar ideias curtas do usuário em imagens de alta qualidade e visualmente coerentes usando a ferramenta de geração de imagens.

    Ao gerar imagens:
    1. Agir imediatamente. Apenas fazer perguntas esclarecedoras se a solicitação for ambígua ou estiver faltando um detalhe crítico.
    2. Expandir o prompt internamente para incluir:
        - Assunto e ambiente
        - Composição e enquadramento da câmera
        - Iluminação e paleta de cores
        - Humor ou atmosfera
        - Estilo artístico ou referência visual (quando apropriado)
    3. Manter o prompt final da imagem abaixo de 100 palavras.
    4. Preferir detalhes visuais concretos sobre linguagem abstrata.
    5. Evitar estilos contraditórios ou cenas superlotadas.

    Após a geração da imagem:
    1. Fornecer uma legenda breve de 1-2 frases descrevendo a imagem.
    2. Não explicar a engenharia de prompt ou passos internos a menos que explicitamente solicitado.\
    """),
    db=gemini_agents_db,
    # Adicionar a data e hora atuais ao contexto
    add_datetime_to_context=True,
    # Adicionar o histórico das execuções do agente ao contexto
    add_history_to_context=True,
    # Número de execuções históricas para incluir no contexto
    num_history_runs=3,
    markdown=True,
)


def save_images(response, output_dir: str = "generated_images"):
    """Salvar imagens geradas da resposta no disco."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    if response.images:
        for img in response.images:
            if img.content:
                filename = output_path / f"image_{img.id[:8]}.png"
                with open(filename, "wb") as f:
                    f.write(img.content)
                print(f"Salvo: {filename}")


if __name__ == "__main__":
    creative_studio_agent.print_response(
        "A surreal desert landscape with floating monoliths, golden hour lighting, dreamlike atmosphere",
        stream=True,
    )

    run_response = creative_studio_agent.get_last_run_output()
    if run_response and isinstance(run_response, RunOutput) and run_response.images:
        save_images(run_response)
