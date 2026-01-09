"""🤔 DeepKnowledge - Um Agente de IA que pesquisa iterativamente uma base de conhecimento para responder perguntas

Este agente realiza buscas iterativas em sua base de conhecimento, dividindo consultas complexas
em sub-perguntas e sintetizando respostas abrangentes. Ele foi projetado para explorar
tópicos profundamente e completamente seguindo cadeias de raciocínio.

Neste exemplo, o agente usa a documentação do Agno como base de conhecimento

Características Principais:
- Pesquisa iterativamente uma base de conhecimento
- Atribuição de fontes e citações

Execute `pip install openai lancedb tantivy inquirer agno` para instalar as dependências.
"""

from textwrap import dedent
from typing import List, Optional

import inquirer
import typer
from agno.agent import Agent
from agno.db.base import SessionType
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.openai import OpenAIChat
from agno.vectordb.lancedb import LanceDb, SearchType
from rich import print


def initialize_knowledge_base():
    """Inicializar a base de conhecimento com sua documentação ou fonte de conhecimento preferida
    Aqui usamos a documentação do Agno como exemplo, mas você pode substituir por URLs relevantes
    """
    agent_knowledge = Knowledge(
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="deep_knowledge_knowledge",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
    )
    agent_knowledge.add_content(
        url="https://docs.agno.com/llms-full.txt",
    )
    return agent_knowledge


def get_agent_db():
    """Retornar armazenamento do agente"""
    return SqliteDb(session_table="deep_knowledge_sessions", db_file="tmp/agents.db")


def create_agent(session_id: Optional[str] = None) -> Agent:
    """Criar e retornar um agente DeepKnowledge configurado."""
    agent_knowledge = initialize_knowledge_base()
    agent_db = get_agent_db()
    return Agent(
        name="DeepKnowledge",
        session_id=session_id,
        model=OpenAIChat(id="gpt-4o"),
        description=dedent("""\
        Você é DeepKnowledge, um agente de raciocínio avançado projetado para fornecer respostas
        completas e bem pesquisadas a qualquer consulta pesquisando sua base de conhecimento.

        Seus pontos fortes incluem:
        - Dividir tópicos complexos em componentes gerenciáveis
        - Conectar informações em múltiplos domínios
        - Fornecer respostas matizadas e bem pesquisadas
        - Manter honestidade intelectual e citar fontes
        - Explicar conceitos complexos em termos claros e acessíveis"""),
        instructions=dedent("""\
        Sua missão é não deixar pedra sobre pedra em sua busca pela resposta correta.

        Para alcançar isso, siga estes passos:
        1. **Analisar a entrada e dividi-la em componentes-chave**.
        2. **Termos de busca**: Você deve identificar pelo menos 3-5 termos de busca-chave para pesquisar.
        3. **Busca Inicial:** Pesquisar sua base de conhecimento por informações relevantes. Você deve fazer pelo menos 3 buscas para obter todas as informações relevantes.
        4. **Avaliação:** Se a resposta da base de conhecimento estiver incompleta, ambígua ou insuficiente - Peça esclarecimentos ao usuário. Não faça suposições informadas.
        5. **Processo Iterativo:**
            - Continue pesquisando sua base de conhecimento até ter uma resposta abrangente.
            - Reavalie a completude de sua resposta após cada iteração de busca.
            - Repita o processo de busca até ter certeza de que todos os aspectos da pergunta foram abordados.
        4. **Documentação de Raciocínio:** Documente claramente seu processo de raciocínio:
            - Observe quando buscas adicionais foram acionadas.
            - Indique quais informações vieram da base de conhecimento e de onde foram obtidas.
            - Explique como você reconciliou quaisquer informações conflitantes ou ambíguas.
        5. **Síntese Final:** Apenas finalize e apresente sua resposta depois de verificá-la através de múltiplas passadas de busca.
            Inclua todos os detalhes pertinentes e forneça referências adequadas.
        6. **Melhoria Contínua:** Se novas informações relevantes surgirem mesmo após apresentar sua resposta,
            esteja preparado para atualizar ou expandir sua resposta.

        **Estilo de Comunicação:**
        - Use linguagem clara e concisa.
        - Organize sua resposta com passos numerados, marcadores ou parágrafos curtos conforme necessário.
        - Seja transparente sobre seu processo de busca e cite suas fontes.
        - Garanta que sua resposta final seja abrangente e não deixe nenhuma parte da consulta sem resposta.

        Lembre-se: **Não finalize sua resposta até que todos os ângulos da pergunta tenham sido explorados.**"""),
        additional_context=dedent("""\
        Você deve responder apenas com a resposta final e o processo de raciocínio.
        Não há necessidade de incluir informações irrelevantes.

        - User ID: {user_id}
        - Memória: Você tem acesso aos seus resultados de busca anteriores e processo de raciocínio.
        """),
        knowledge=agent_knowledge,
        db=agent_db,
        add_history_to_context=True,
        num_history_runs=3,
        read_chat_history=True,
        markdown=True,
    )


def get_example_topics() -> List[str]:
    """Retornar uma lista de tópicos de exemplo para o agente."""
    return [
        "What are AI agents and how do they work in Agno?",
        "What chunking strategies does Agno support for text processing?",
        "How can I implement custom tools in Agno?",
        "How does knowledge retrieval work in Agno?",
        "What types of embeddings does Agno support?",
    ]


def handle_session_selection() -> Optional[str]:
    """Lidar com a seleção de sessão e retornar o ID da sessão selecionada."""
    agent_db = get_agent_db()

    new = typer.confirm("Do you want to start a new session?", default=True)
    if new:
        return None

    existing_sessions: List[str] = agent_db.get_sessions(session_type=SessionType.AGENT)
    if not existing_sessions:
        print("Nenhuma sessão existente encontrada. Iniciando uma nova sessão.")
        return None

    print("\nSessões existentes:")
    for i, session in enumerate(existing_sessions, 1):
        print(f"{i}. {session}")

    session_idx = typer.prompt(
        "Escolha um número de sessão para continuar (ou pressione Enter para a mais recente)",
        default=1,
    )

    try:
        return existing_sessions[int(session_idx) - 1]
    except (ValueError, IndexError):
        return existing_sessions[0]


def run_interactive_loop(agent: Agent):
    """Executar o loop interativo de perguntas e respostas."""
    example_topics = get_example_topics()

    while True:
        choices = [f"{i + 1}. {topic}" for i, topic in enumerate(example_topics)]
        choices.extend(["Enter custom question...", "Exit"])

        questions = [
            inquirer.List(
                "topic",
                message="Selecione um tópico ou faça uma pergunta diferente:",
                choices=choices,
            )
        ]
        answer = inquirer.prompt(questions)

        if answer["topic"] == "Exit":
            break

        if answer["topic"] == "Enter custom question...":
            questions = [inquirer.Text("custom", message="Digite sua pergunta:")]
            custom_answer = inquirer.prompt(questions)
            topic = custom_answer["custom"]
        else:
            topic = example_topics[int(answer["topic"].split(".")[0]) - 1]

        agent.print_response(topic, stream=True)


def deep_knowledge_agent():
    """Função principal para executar o agente DeepKnowledge."""

    session_id = handle_session_selection()
    agent = create_agent(session_id)

    print("\n🤔 Bem-vindo ao DeepKnowledge - Seu Assistente de Pesquisa Avançado! 📚")
    if session_id is None:
        session_id = agent.session_id
        if session_id is not None:
            print(f"[bold green]Nova Sessão Iniciada: {session_id}[/bold green]\n")
        else:
            print("[bold green]Nova Sessão Iniciada[/bold green]\n")
    else:
        print(f"[bold blue]Continuando Sessão Anterior: {session_id}[/bold blue]\n")

    run_interactive_loop(agent)


if __name__ == "__main__":
    typer.run(deep_knowledge_agent)

# Exemplos de prompts para tentar:
"""
Explore as capacidades do Agno com estas consultas:
1. "What are the different types of agents in Agno?"
2. "How does Agno handle knowledge base management?"
3. "What embedding models does Agno support?"
4. "How can I implement custom tools in Agno?"
5. "What storage options are available for workflow caching?"
6. "How does Agno handle streaming responses?"
7. "What types of LLM providers does Agno support?"
8. "How can I implement custom knowledge sources?"
"""
