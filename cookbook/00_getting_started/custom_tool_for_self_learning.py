"""
Ferramenta Personalizada para Autoaprendizado - Escreva Suas Próprias Ferramentas
===================================================================================
Este exemplo mostra como escrever ferramentas personalizadas para seu agente.
Uma ferramenta é apenas uma função Python — o agente a chama quando necessário.

Vamos construir um agente de autoaprendizado que pode salvar insights em uma base de conhecimento.
O conceito-chave: qualquer função pode se tornar uma ferramenta.

Conceitos-chave:
- Ferramentas são funções Python com docstrings (a docstring diz ao agente o que a ferramenta faz)
- O agente decide quando chamar sua ferramenta com base na conversa
- Retorne uma string para comunicar resultados de volta ao agente

Exemplos de prompts para testar:
- "Qual é uma boa relação P/E para ações de tecnologia? Salve esse insight."
- "Lembre-se que a receita de data center da NVDA é o principal driver de crescimento"
- "Quais aprendizados temos salvos?"
"""

import json
from datetime import datetime, timezone

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.reader.text_reader import TextReader
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools
from agno.vectordb.chroma import ChromaDb
from agno.vectordb.search import SearchType

# ============================================================================
# Configuração de Armazenamento
# ============================================================================
agent_db = SqliteDb(db_file="tmp/agents.db")

# ============================================================================
# Base de Conhecimento para Aprendizados
# ============================================================================
learnings_kb = Knowledge(
    name="Agent Learnings",
    vector_db=ChromaDb(
        name="learnings",
        collection="learnings",
        path="tmp/chromadb",
        persistent_client=True,
        search_type=SearchType.hybrid,
        hybrid_rrf_k=60,
        embedder=GeminiEmbedder(id="gemini-embedding-001"),
    ),
    max_results=5,
    contents_db=agent_db,
)


# ============================================================================
# Ferramenta Personalizada: Salvar Aprendizado
# ============================================================================
def save_learning(title: str, learning: str) -> str:
    """
    Salva um insight reutilizável na base de conhecimento para referência futura.

    Args:
        title: Título descritivo curto (ex: "Benchmarks P/E de ações de tecnologia")
        learning: O insight a salvar — seja específico e acionável

    Returns:
        Mensagem de confirmação
    """
    # Validar entradas
    if not title or not title.strip():
        return "Não é possível salvar: título é obrigatório"
    if not learning or not learning.strip():
        return "Não é possível salvar: conteúdo do aprendizado é obrigatório"

    # Construir o payload
    payload = {
        "title": title.strip(),
        "learning": learning.strip(),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }

    # Salvar na base de conhecimento
    learnings_kb.add_content(
        name=payload["title"],
        text_content=json.dumps(payload, ensure_ascii=False),
        reader=TextReader(),
        skip_if_exists=True,
    )

    return f"Salvo: '{title}'"


# ============================================================================
# Instruções do Agente
# ============================================================================
instructions = """\
Você é um Agente Financeiro que aprende e melhora com o tempo.

Você tem duas habilidades especiais:
1. Pesquisar sua base de conhecimento por aprendizados previamente salvos
2. Salvar novos insights usando a ferramenta save_learning

## Fluxo de Trabalho

1. Verificar Conhecimento Primeiro
   - Antes de responder, pesquisar aprendizados anteriores relevantes
   - Aplicar quaisquer insights relevantes à sua resposta

2. Coletar Informações
   - Usar ferramentas YFinance para dados de mercado
   - Combinar com insights da sua base de conhecimento

3. Propor Aprendizados
   - Após responder, considere: há um insight reutilizável aqui?
   - Se sim, proponha neste formato:

---
**Aprendizado Proposto**

Título: [título conciso]
Aprendizado: [o insight — específico e acionável]

Salvar isso? (sim/não)
---

- Apenas chamar save_learning DEPOIS que o usuário disser "sim"
- Se o usuário disser "não", reconhecer e continuar

## O que Faz um Bom Aprendizado

- Específico: "Relações P/E de tecnologia geralmente variam 20-35x" não "P/E varia"
- Acionável: Pode ser aplicado a perguntas futuras
- Reutilizável: Útil além desta conversa

Não salvar: Dados brutos, fatos únicos ou informações óbvias.\
"""

# ============================================================================
# Criar o Agente
# ============================================================================
self_learning_agent = Agent(
    name="Self-Learning Agent",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=instructions,
    tools=[
        YFinanceTools(),
        save_learning,  # Nossa ferramenta personalizada — apenas uma função Python!
    ],
    knowledge=learnings_kb,
    search_knowledge=True,
    db=agent_db,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

# ============================================================================
# Executar o Agente
# ============================================================================
if __name__ == "__main__":
    # Fazer uma pergunta que pode produzir um aprendizado
    self_learning_agent.print_response(
        "Qual é uma relação P/E saudável para ações de tecnologia?",
        stream=True,
    )

    # Se o agente propôs um aprendizado, aprová-lo
    self_learning_agent.print_response(
        "sim",
        stream=True,
    )

    # Depois, o agente pode recuperar o aprendizado
    self_learning_agent.print_response(
        "Quais aprendizados temos salvos?",
        stream=True,
    )

# ============================================================================
# Mais Exemplos
# ============================================================================
"""
Escrevendo ferramentas personalizadas:

1. Defina uma função com type hints e docstring
   def my_tool(param: str) -> str:
       '''Descrição do que esta ferramenta faz.

       Args:
           param: Para que este parâmetro serve

       Returns:
           O que a ferramenta retorna
       '''
       # Sua lógica aqui
       return "Resultado"

2. Adicione à lista de ferramentas do agente
   agent = Agent(
       tools=[my_tool],
       ...
   )

A docstring é crítica — ela diz ao agente:
- O que a ferramenta faz
- Quais parâmetros ela precisa
- O que ela retorna

O agente usa isso para decidir quando e como chamar sua ferramenta.
"""
