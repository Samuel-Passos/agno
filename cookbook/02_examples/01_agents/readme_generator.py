from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.github import GithubTools
from agno.tools.local_file_system import LocalFileSystemTools

readme_gen_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    name="Readme Generator Agent",
    tools=[GithubTools(), LocalFileSystemTools()],
    markdown=True,
    instructions=[
        "Você é um agente gerador de README",
        "Você receberá uma URL de repositório ou nome de repositório do usuário."
        "Você usará a ferramenta `get_repository` para obter os detalhes do repositório."
        "Você deve passar o repo_name como argumento para a ferramenta. Deve estar no formato owner/repo_name. Se fornecida uma URL, extrair owner/repo_name dela."
        "Também chamar a ferramenta `get_repository_languages` para obter os idiomas usados no repositório."
        "Escrever um README útil para um projeto de código aberto, incluindo como clonar e instalar o projeto, executar o projeto, etc. Também adicionar badges para a licença, tamanho do repo, etc"
        "Não incluir os idiomas usados do projeto no README"
        "Escrever o README produzido no sistema de arquivos local",
    ],
)

readme_gen_agent.print_response(
    "Get details of https://github.com/agno-agi/agno", markdown=True
)
