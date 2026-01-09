from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.website_reader import WebsiteReader
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.exa import ExaTools
from agno.tools.slack import SlackTools
from agno.vectordb.pgvector.pgvector import PgVector

knowledge = Knowledge(
    vector_db=PgVector(
        table_name="website_documents",
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
    ),
)

knowledge.add_content(
    url="https://docs.agno.com/introduction",
    reader=WebsiteReader(
        # Número de links para seguir a partir das URLs iniciais
        max_links=10,
    ),
)


support_channel = "testing"
feedback_channel = "testing"

doc_researcher_agent = Agent(
    name="Doc researcher Agent",
    role="Pesquisar a base de conhecimento por informações",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools(), ExaTools()],
    knowledge=knowledge,
    search_knowledge=True,
    instructions=[
        "Você é um especialista em documentação para o produto fornecido. Pesquisar a base de conhecimento completamente para responder perguntas do usuário.",
        "Sempre fornecer informações precisas com base na documentação.",
        "Se a pergunta corresponder a uma FAQ, fornecer a resposta específica da FAQ da documentação.",
        "Quando relevante, incluir links diretos para páginas específicas da documentação que abordam a pergunta do usuário.",
        "Se não tiver certeza sobre uma resposta, reconhecer isso e sugerir onde o usuário pode encontrar mais informações.",
        "Formatar suas respostas claramente com cabeçalhos, marcadores e exemplos de código quando apropriado.",
        "Sempre verificar que sua resposta aborda diretamente a pergunta específica do usuário.",
        "Se não conseguir encontrar a resposta na base de conhecimento da documentação, usar DuckDuckGoTools ou ExaTools para pesquisar na web por informações relevantes para responder a pergunta do usuário.",
    ],
)


escalation_manager_agent = Agent(
    name="Escalation Manager Agent",
    role="Escalar o problema para o canal do slack",
    model=OpenAIChat(id="gpt-4o"),
    tools=[SlackTools()],
    instructions=[
        "Você é um gerente de escalação responsável por rotear problemas críticos para a equipe de suporte.",
        f"Quando um usuário reportar um problema, sempre enviá-lo para o canal Slack #{support_channel} com todos os detalhes relevantes usando a função send_message do toolkit.",
        "Incluir o nome do usuário, informações de contato (se disponíveis) e uma descrição clara do problema.",
        "Após escalar o problema, responder ao usuário confirmando que seu problema foi escalado.",
        "Sua resposta deve ser profissional e tranquilizadora, informando que a equipe de suporte o abordará em breve.",
        "Sempre incluir um número de ticket ou referência se disponível para ajudar o usuário a rastrear seu problema.",
        "Nunca tentar resolver problemas técnicos sozinho - seu papel é estritamente escalar e comunicar.",
    ],
)

feedback_collector_agent = Agent(
    name="Feedback Collector Agent",
    role="Coletar feedback do usuário",
    model=OpenAIChat(id="gpt-4o"),
    tools=[SlackTools()],
    description="Você é um agente de IA que pode coletar feedback do usuário.",
    instructions=[
        "Você é responsável por coletar feedback do usuário sobre o produto ou solicitações de recursos.",
        f"Quando um usuário fornecer feedback ou sugerir um recurso, usar a ferramenta Slack para enviá-lo para o canal #{feedback_channel} usando a função send_message do toolkit.",
        "Incluir todos os detalhes relevantes do feedback do usuário em sua mensagem do Slack.",
        "Após enviar o feedback para o Slack, responder ao usuário profissionalmente, agradecendo por sua contribuição.",
        "Sua resposta deve reconhecer o feedback deles e garantir que será levado em consideração.",
        "Ser caloroso e apreciativo em seu tom, pois o feedback do usuário é valioso para melhorar nosso produto.",
        "Não prometer prazos específicos ou garantir que suas sugestões serão implementadas.",
    ],
)


customer_support_team = Team(
    name="Customer Support Team",
    model=OpenAIChat("gpt-4o"),
    members=[doc_researcher_agent, escalation_manager_agent, feedback_collector_agent],
    determine_input_for_members=False,
    respond_directly=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
    instructions=[
        "Você é o agente principal de suporte ao cliente responsável por classificar e rotear consultas de clientes.",
        "Analisar cuidadosamente cada mensagem do usuário e determinar se é: uma pergunta que precisa de pesquisa na documentação, um relatório de bug que requer escalação ou feedback do produto.",
        "Para perguntas gerais sobre o produto, rotear para o doc_researcher_agent que pesquisará a documentação por respostas.",
        "Se o doc_researcher_agent não conseguir encontrar uma resposta para uma pergunta, escalá-la para o escalation_manager_agent.",
        "Para relatórios de bugs ou problemas técnicos, rotear imediatamente para o escalation_manager_agent.",
        "Para solicitações de recursos ou feedback do produto, rotear para o feedback_collector_agent.",
        "Sempre fornecer uma explicação clara do por que está roteando a consulta para um agente específico.",
        "Após receber uma resposta do agente apropriado, retransmitir essas informações de volta ao usuário de forma profissional e útil.",
        "Garantir uma experiência perfeita para o usuário mantendo o contexto ao longo da conversa.",
    ],
)

# Adicionar a consulta e o agente redireciona para o agente apropriado
customer_support_team.print_response(
    "Hi Team, I want to build an educational platform where the models are have access to tons of study materials, How can Agno platform help me build this?",
    stream=True,
)
# customer_support_team.print_response(
#     "Support json schemas in Gemini client in addition to pydantic base model",
#     stream=True,
# )
# customer_support_team.print_response(
#     "Can you please update me on the above feature",
#     stream=True,
# )
# customer_support_team.print_response(
#     "[Bug] Async tools in team of agents not awaited properly, causing runtime errors ",
#     stream=True,
# )
