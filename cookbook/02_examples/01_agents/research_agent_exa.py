"""🎓 Research Scholar Agent - Seu Assistente de Pesquisa Acadêmica de IA!

Este exemplo mostra como criar um agente de pesquisa sofisticado que combina
capacidades de busca acadêmica com expertise em escrita acadêmica. O agente realiza
pesquisa completa usando busca acadêmica do Exa, analisa publicações recentes e entrega
relatórios bem estruturados, no estilo acadêmico, sobre qualquer tópico.

Capacidades principais:
- Busca avançada de literatura acadêmica
- Análise de publicações recentes
- Síntese interdisciplinar
- Expertise em escrita acadêmica
- Gerenciamento de citações

Exemplos de prompts para tentar:
- "Explore recent advances in quantum machine learning"
- "Analyze the current state of fusion energy research"
- "Investigate the latest developments in CRISPR gene editing"
- "Research the intersection of blockchain and sustainable energy"
- "Examine recent breakthroughs in brain-computer interfaces"
"""

from datetime import datetime
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

# Inicializar o agente de pesquisa acadêmica com capacidades acadêmicas
research_scholar = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        ExaTools(
            start_published_date=datetime.now().strftime("%Y-%m-%d"), type="keyword"
        )
    ],
    description=dedent("""\
        Você é um pesquisador distinto com expertise em múltiplas disciplinas.
        Suas credenciais acadêmicas incluem: 📚

        - Metodologia de pesquisa avançada
        - Síntese interdisciplinar
        - Análise de literatura acadêmica
        - Excelência em escrita científica
        - Experiência em revisão por pares
        - Gerenciamento de citações
        - Interpretação de dados
        - Comunicação técnica
        - Ética em pesquisa
        - Análise de tendências emergentes\
    """),
    instructions=dedent("""\
        1. Metodologia de Pesquisa 🔍
           - Realizar 3 buscas acadêmicas distintas
           - Focar em publicações revisadas por pares
           - Priorizar descobertas de avanços recentes
           - Identificar pesquisadores e instituições-chave

        2. Estrutura de Análise 📊
           - Sintetizar achados entre fontes
           - Avaliar metodologias de pesquisa
           - Identificar consenso e controvérsias
           - Avaliar implicações práticas

        3. Estrutura do Relatório 📝
           - Criar um título acadêmico envolvente
           - Escrever um resumo convincente
           - Apresentar metodologia claramente
           - Discutir achados sistematicamente
           - Tirar conclusões baseadas em evidências

        4. Padrões de Qualidade ✓
           - Garantir citações precisas
           - Manter rigor acadêmico
           - Apresentar perspectivas equilibradas
           - Destacar direções futuras de pesquisa\
    """),
    expected_output=dedent("""\
        # {Título Envolvente} 📚

        ## Resumo
        {Visão geral concisa da pesquisa e principais achados}

        ## Introdução
        {Contexto e significância}
        {Objetivos da pesquisa}

        ## Metodologia
        {Estratégia de busca}
        {Critérios de seleção}

        ## Revisão de Literatura
        {Estado atual da pesquisa}
        {Principais achados e avanços}
        {Tendências emergentes}

        ## Análise
        {Avaliação crítica}
        {Comparações entre estudos}
        {Lacunas de pesquisa}

        ## Direções Futuras
        {Oportunidades de pesquisa emergentes}
        {Aplicações potenciais}
        {Questões em aberto}

        ## Conclusões
        {Resumo dos principais achados}
        {Implicações para o campo}

        ## Referências
        {Citações acadêmicas formatadas adequadamente}

        ---
        Pesquisa conduzida por Acadêmico de IA
        Publicado: {current_date}
        Última Atualização: {current_time}\
    """),
    markdown=True,
    add_datetime_to_context=True,
    save_response_to_file="tmp/{message}.md",
)

# Exemplo de uso com solicitação de pesquisa acadêmica
if __name__ == "__main__":
    research_scholar.print_response(
        "Analyze recent developments in quantum computing architectures",
        stream=True,
    )

# Tópicos de pesquisa avançados para explorar:
"""
Ciência e Computação Quântica:
1. "Investigate recent breakthroughs in quantum error correction"
2. "Analyze the development of topological quantum computing"
3. "Research quantum machine learning algorithms and applications"
4. "Explore advances in quantum sensing technologies"

Biotecnologia e Medicina:
1. "Examine recent developments in mRNA vaccine technology"
2. "Analyze breakthroughs in organoid research"
3. "Investigate advances in precision medicine"
4. "Research developments in neurotechnology"

Ciência dos Materiais:
1. "Explore recent advances in metamaterials"
2. "Analyze developments in 2D materials beyond graphene"
3. "Research progress in self-healing materials"
4. "Investigate new battery technologies"

Inteligência Artificial:
1. "Examine recent advances in foundation models"
2. "Analyze developments in AI safety research"
3. "Research progress in neuromorphic computing"
4. "Investigate advances in explainable AI"
"""
