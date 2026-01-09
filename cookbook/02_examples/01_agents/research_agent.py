"""🔍 Research Agent - Seu Jornalista Investigativo de IA!

Este exemplo mostra como criar um agente de pesquisa sofisticado que combina
capacidades de busca na web com habilidades de escrita jornalística profissional. O agente realiza
pesquisa abrangente usando múltiplas fontes, verifica informações e entrega
artigos bem estruturados, no estilo NYT, sobre qualquer tópico.

Capacidades principais:
- Busca avançada na web em múltiplas fontes
- Extração e análise de conteúdo
- Verificação de referência cruzada
- Escrita jornalística profissional
- Reportagem equilibrada e objetiva

Exemplos de prompts para tentar:
- "Analyze the impact of AI on healthcare delivery and patient outcomes"
- "Report on the latest breakthroughs in quantum computing"
- "Investigate the global transition to renewable energy sources"
- "Explore the evolution of cybersecurity threats and defenses"
- "Research the development of autonomous vehicle technology"

Dependências: `pip install openai ddgs newspaper4k lxml_html_clean agno`
"""

from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

# Inicializar o agente de pesquisa com capacidades jornalísticas avançadas
research_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools(), Newspaper4kTools()],
    description=dedent("""\
        Você é um jornalista investigativo de elite com décadas de experiência no New York Times.
        Sua expertise abrange: 📰

        - Pesquisa e análise investigativa profunda
        - Verificação meticulosa de fatos e fontes
        - Construção de narrativa convincente
        - Reportagem e visualização baseada em dados
        - Síntese de entrevistas com especialistas
        - Análise de tendências e previsões futuras
        - Simplificação de tópicos complexos
        - Práticas de jornalismo ético
        - Apresentação de perspectiva equilibrada
        - Integração de contexto global\
    """),
    instructions=dedent("""\
        1. Fase de Pesquisa 🔍
           - Buscar 10+ fontes autoritárias sobre o tópico
           - Priorizar publicações recentes e opiniões de especialistas
           - Identificar partes interessadas e perspectivas-chave

        2. Fase de Análise 📊
           - Extrair e verificar informações críticas
           - Fazer referência cruzada de fatos em múltiplas fontes
           - Identificar padrões e tendências emergentes
           - Avaliar pontos de vista conflitantes

        3. Fase de Escrita ✍️
           - Criar uma manchete que chame atenção
           - Estruturar conteúdo no estilo NYT
           - Incluir citações e estatísticas relevantes
           - Manter objetividade e equilíbrio
           - Explicar conceitos complexos claramente

        4. Controle de Qualidade ✓
           - Verificar todos os fatos e atribuições
           - Garantir fluxo narrativo e legibilidade
           - Adicionar contexto onde necessário
           - Incluir implicações futuras
    """),
    expected_output=dedent("""\
        # {Manchete Convincente} 📰

        ## Resumo Executivo
        {Visão geral concisa dos principais achados e significância}

        ## Contexto e Antecedentes
        {Contexto histórico e importância}
        {Visão geral do cenário atual}

        ## Principais Achados
        {Principais descobertas e análise}
        {Insights e citações de especialistas}
        {Evidências estatísticas}

        ## Análise de Impacto
        {Implicações atuais}
        {Perspectivas das partes interessadas}
        {Efeitos na indústria/sociedade}

        ## Perspectiva Futura
        {Tendências emergentes}
        {Previsões de especialistas}
        {Desafios e oportunidades potenciais}

        ## Insights de Especialistas
        {Citações e análises notáveis de líderes da indústria}
        {Pontos de vista contrastantes}

        ## Fontes e Metodologia
        {Lista de fontes primárias com contribuições-chave}
        {Visão geral da metodologia de pesquisa}

        ---
        Pesquisa conduzida por Jornalista Investigativo de IA
        Relatório no Estilo New York Times
        Publicado: {current_date}
        Última Atualização: {current_time}\
    """),
    db=SqliteDb(db_file="tmp/research_agent.db"),
    num_history_runs=2,
    markdown=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    max_tool_calls_from_history=5,
    debug_mode=True,
)

# Exemplo de uso com solicitação de pesquisa detalhada
if __name__ == "__main__":
    research_agent.print_response(
        "Analyze the current state and future implications of artificial intelligence regulation worldwide",
        stream=True,
    )
    research_agent.print_response(
        "Research the current state of quantum computing and its practical applications",
        stream=True,
    )
    research_agent.print_response(
        "Explore the latest developments in CRISPR gene editing technology",
        stream=True,
    )
    research_agent.print_response(
        "Report on innovative carbon capture technologies and their effectiveness",
        stream=True,
    )
    research_agent.print_response(
        "Investigate the global progress in renewable energy adoption",
        stream=True,
    )
    research_agent.print_response(
        "Examine the effects of social media on democratic processes",
        stream=True,
    )

# Tópicos de pesquisa avançados para explorar:
"""
Tecnologia e Inovação:
1. "Investigate the development and impact of large language models in 2024"
2. "Research the current state of quantum computing and its practical applications"
3. "Analyze the evolution and future of edge computing technologies"
4. "Explore the latest advances in brain-computer interface technology"

Ambiental e Sustentabilidade:
1. "Report on innovative carbon capture technologies and their effectiveness"
2. "Investigate the global progress in renewable energy adoption"
3. "Analyze the impact of circular economy practices on global sustainability"
4. "Research the development of sustainable aviation technologies"

Saúde e Biotecnologia:
1. "Explore the latest developments in CRISPR gene editing technology"
2. "Analyze the impact of AI on drug discovery and development"
3. "Investigate the evolution of personalized medicine approaches"
4. "Research the current state of longevity science and anti-aging research"

Impacto Social:
1. "Examine the effects of social media on democratic processes"
2. "Analyze the impact of remote work on urban development"
3. "Investigate the role of blockchain in transforming financial systems"
4. "Research the evolution of digital privacy and data protection measures"
"""
