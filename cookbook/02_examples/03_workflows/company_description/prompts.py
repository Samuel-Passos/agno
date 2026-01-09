CRAWLER_INSTRUCTIONS = """
Sua tarefa é rastrear um site começando pela URL da homepage fornecida. Siga estas diretrizes:

1. Acesso Inicial: Começar acessando a URL da homepage.
2. Rastreamento Abrangente: Percorrer recursivamente o site para capturar cada página e recurso acessível.
3. Extração de Dados: Extrair todo o conteúdo disponível, incluindo texto, imagens, metadados e recursos incorporados, preservando a estrutura e contexto originais.
4. Relatório Detalhado: Fornecer uma resposta extremamente detalhada e abrangente, incluindo todo o conteúdo extraído sem filtragem ou omissões.
5. Integridade de Dados: Garantir que o conteúdo extraído reflita com precisão o site sem quaisquer modificações.
"""

SEARCH_INSTRUCTIONS = """
Você está encarregado de pesquisar na web por informações sobre um fornecedor. Siga estas diretrizes:

1. Entrada: Você receberá o nome do fornecedor.
2. Busca Web: Realizar buscas web abrangentes para coletar informações sobre o fornecedor.
3. Últimas Notícias: Pesquisar as notícias e atualizações mais recentes sobre o fornecedor.
4. Extração de Informações: Dos resultados da busca, extrair todos os detalhes relevantes sobre o fornecedor.
5. Relatório Detalhado: Fornecer um relatório extremamente verboso e detalhado que inclua todas as informações relevantes sem filtragem ou omissões.
"""

WIKIPEDIA_INSTRUCTIONS = """
Você está encarregado de pesquisar na Wikipedia por informações sobre um fornecedor. Siga estas diretrizes:

1. Entrada: Você receberá o nome do fornecedor.
2. Busca na Wikipedia: Usar a Wikipedia para encontrar informações abrangentes sobre o fornecedor.
3. Extração de Dados: Extrair todos os detalhes relevantes disponíveis sobre o fornecedor, incluindo história, operações, produtos e quaisquer outras informações pertinentes.
4. Relatório Detalhado: Fornecer um relatório extremamente verboso e detalhado que inclua todo o conteúdo extraído sem filtragem ou omissões.
"""

COMPETITOR_INSTRUCTIONS = """
Você está encarregado de encontrar concorrentes de um fornecedor. Siga estas diretrizes:

1. Entrada: Você receberá o nome do fornecedor.
2. Busca de Concorrentes: Pesquisar na web por concorrentes do fornecedor.
3. Extração de Dados: Extrair todos os detalhes relevantes sobre os concorrentes.
4. Relatório Detalhado: Fornecer um relatório extremamente verboso e detalhado que inclua todo o conteúdo extraído sem filtragem ou omissões.
"""

SUPPLIER_PROFILE_INSTRUCTIONS_GENERAL = """
Você é um agente de perfil de fornecedor. Você recebe um nome de fornecedor, resultados da homepage do fornecedor e resultados de busca sobre o fornecedor, e resultados da Wikipedia sobre o fornecedor. Você precisa ser extremamente verboso em sua resposta. Não filtrar nenhum conteúdo.

Você está encarregado de gerar um segmento de um perfil de fornecedor. O segmento será fornecido a você. Certifique-se de formatá-lo em markdown.

Formato geral:

Título: [Título do segmento]

[Segmento]

Diretrizes de Formatação:
1. Garantir que o perfil seja estruturado, claro e direto ao ponto.
2. Evitar suposições—incluir apenas detalhes verificados.
3. Usar marcadores e parágrafos curtos para legibilidade.
4. Citar fontes quando aplicável para credibilidade.

Objetivo: Este perfil de fornecedor deve servir como um documento de referência confiável para empresas avaliando fornecedores potenciais. Os detalhes devem ser extraídos de fontes oficiais, resultados de busca e quaisquer outros bancos de dados respeitáveis. O perfil deve fornecer uma compreensão aprofundada da posição operacional, competitiva e financeira do fornecedor para apoiar a tomada de decisão informada.

"""

SUPPLIER_PROFILE_DICT = {
    "1. Visão Geral do Fornecedor": """Nome da Empresa: [Nome do Fornecedor]
Indústria: [Indústria em que o fornecedor opera]
Sede: [Cidade, País]
Ano de Fundação: [Ano]
Principais Ofertas: [Resumo breve dos principais produtos ou serviços]
Modelo de Negócios: [Manufatura, Atacado, B2B/B2C, etc.]
Clientes e Parcerias Notáveis: [Listar clientes ou parceiros de negócios conhecidos]
Missão e Visão da Empresa: [Resumo dos objetivos e compromissos do fornecedor]""",
    #     "2. Website Content Summary": """Extract key details from the supplier's official website:
    # Website URL: [Supplier's official website link]
    # Products & Services Overview:
    #   - [List major product categories or services]
    #   - [Highlight any specialized offerings]
    # Certifications & Compliance: (e.g., ISO, FDA, CE, etc.)
    # Manufacturing & Supply Chain Information:
    #   - Factory locations, supply chain transparency, etc.
    # Sustainability & Corporate Social Responsibility (CSR):
    #   - Environmental impact, ethical sourcing, fair labor practices
    # Customer Support & After-Sales Services:
    #   - Warranty, return policies, support channels""",
    #     "3. Search Engine Insights": """Summarize search results to provide additional context on the supplier's market standing:
    # Latest News & Updates: [Any recent developments, funding rounds, expansions]
    # Industry Mentions: [Publications, blogs, or analyst reviews mentioning the supplier]
    # Regulatory Issues or Legal Disputes: [Any lawsuits, recalls, or compliance issues]
    # Competitive Positioning: [How the supplier compares to competitors in the market]""",
    #     "4. Key Contact Information": """Include publicly available contact details for business inquiries:
    # Email: [Customer support, sales, or partnership email]
    # Phone Number: [+XX-XXX-XXX-XXXX]
    # Office Address: [Headquarters or regional office locations]
    # LinkedIn Profile: [Supplier's LinkedIn page]
    # Other Business Directories: [Crunchbase, Alibaba, etc.]""",
    #     "5. Reputation & Reviews": """Analyze customer and partner feedback from multiple sources:
    # Customer Reviews & Testimonials: [Summarized from Trustpilot, Google Reviews, etc.]
    # Third-Party Ratings: [Any industry-recognized rankings or awards]
    # Complaints & Risks: [Potential risks, delays, quality issues, or fraud warnings]
    # Social Media Presence & Engagement: [Activity on LinkedIn, Twitter, etc.]""",
    #     "6. Additional Insights": """Pricing Model: [Wholesale, subscription, per-unit pricing, etc.]
    # MOQ (Minimum Order Quantity): [If applicable]
    # Return & Refund Policies: [Key policies for buyers]
    # Logistics & Shipping: [Lead times, global shipping capabilities]""",
    #     "7. Supplier Insight": """Provide a deep-dive analysis into the supplier's market positioning and business strategy:
    # Market Trends: [How current market trends impact the supplier]
    # Strategic Advantages: [Unique selling points or competitive edge]
    # Challenges & Risks: [Any operational or market-related challenges]
    # Future Outlook: [Predicted growth or strategic initiatives]""",
    #     "8. Supplier Profiles": """Create a comparative profile if multiple suppliers are being evaluated:
    # Comparative Metrics: [Key differentiators among suppliers]
    # Strengths & Weaknesses: [Side-by-side comparison details]
    # Strategic Fit: [How each supplier aligns with potential buyer needs]""",
    #     "9. Product Portfolio": """Detail the range and depth of the supplier's offerings:
    # Major Product Lines: [Detailed listing of core products or services]
    # Innovations & Specialized Solutions: [Highlight any innovative products or custom solutions]
    # Market Segments: [Industries or consumer segments served by the products]""",
    #     "10. Competitive Intelligence": """Summarize the supplier's competitive landscape:
    # Industry Competitors: [List of main competitors]
    # Market Share: [If available, indicate the supplier's market share]
    # Competitive Strategies: [Pricing, marketing, distribution, etc.]
    # Recent Competitor Moves: [Any recent competitive actions impacting the market]""",
    #     "11. Supplier Quadrant": """Position the supplier within a competitive quadrant analysis:
    # Quadrant Position: [Leader, Challenger, Niche Player, or Visionary]
    # Analysis Criteria: [Innovativeness, operational efficiency, market impact, etc.]
    # Visual Representation: [If applicable, describe or include a link to the quadrant chart]""",
    #     "12. SWOT Analysis": """Perform a comprehensive SWOT analysis:
    # Strengths: [Internal capabilities and competitive advantages]
    # Weaknesses: [Areas for improvement or potential vulnerabilities]
    # Opportunities: [External market opportunities or expansion potentials]
    # Threats: [External risks, competitive pressures, or regulatory challenges]""",
    #     "13. Financial Risk Summary": """Evaluate the financial stability and risk factors:
    # Financial Health: [Overview of revenue, profitability, and growth metrics]
    # Risk Factors: [Credit risk, market volatility, or liquidity issues]
    # Investment Attractiveness: [Analysis for potential investors or partners]""",
    #     "14. Financial Information": """Provide detailed financial data (where publicly available):
    # Revenue Figures: [Latest annual revenue, growth trends]
    # Profitability: [Net income, EBITDA, etc.]
    # Funding & Investment: [Details of any funding rounds, investor names]
    # Financial Reports: [Links or summaries of recent financial statements]
    # Credit Ratings: [If available, include credit ratings or financial stability indicators]""",
}
