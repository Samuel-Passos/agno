import json
from datetime import datetime, timezone
from typing import Optional

from agno.agent import Agent
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.text_reader import TextReader
from agno.models.openai import OpenAIResponses
from agno.tools.parallel import ParallelTools
from agno.tools.yfinance import YFinanceTools
from agno.utils.log import logger
from agno.vectordb.pgvector import PgVector, SearchType
from db import db_url, demo_db

# ============================================================================
# Base de conhecimento: armazena aprendizados bem-sucedidos
# ============================================================================
agent_knowledge = Knowledge(
    name="Agent Learnings",
    vector_db=PgVector(
        db_url=db_url,
        table_name="agent_learnings",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    max_results=5,
    contents_db=demo_db,
)


# ============================================================================
# Ferramenta: salvar um snapshot de aprendizado
# ============================================================================
def save_learning(
    title: str,
    context: str,
    learning: str,
    confidence: Optional[str] = "medium",
    type: Optional[str] = "rule",
) -> str:
    """
    Salva um aprendizado reutilizável de uma execução bem-sucedida.

    Args:
        title: Título descritivo curto
        context: Quando / por que este aprendizado se aplica
        learning: O insight reutilizável real
        confidence: low | medium | high
        type: rule | heuristic | source | process | constraint
    """

    payload = {
        "title": title.strip(),
        "context": context.strip(),
        "learning": learning.strip(),
        "confidence": confidence,
        "type": type,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    logger.info(f"Salvando aprendizado: {payload['title']}")

    agent_knowledge.add_content(
        name=payload["title"],
        text_content=json.dumps(payload, ensure_ascii=False),
        reader=TextReader(),
        skip_if_exists=True,
    )

    return "Aprendizado salvo"


# ============================================================================
# Mensagem do sistema
# ============================================================================
system_message = """\
Você é um agente de autoaprendizado.

Você tem acesso a:
- Ferramentas de busca web paralela para informações amplas e atualizadas
- Ferramentas YFinance para dados estruturados de mercado e empresas
- Uma base de conhecimento de aprendizados bem-sucedidos anteriores
- Uma ferramenta para salvar novos aprendizados reutilizáveis

Seu objetivo:
Produzir a melhor resposta possível combinando dados externos frescos com aprendizados anteriores, e melhorar continuamente execuções futuras capturando o que funcionou.

Loop principal:
1) Recuperar aprendizados relevantes da base de conhecimento.
2) Coletar novas informações quando necessário:
   - Usar busca web paralela para tópicos abertos ou atuais.
   - Usar YFinance para dados de mercado, financeiros e séries temporais.
3) Sintetizar uma resposta de alta qualidade usando ambas as fontes.
4) Identificar qualquer insight reutilizável que claramente melhorou o resultado.
5) Perguntar ao usuário se esse insight deve ser salvo.
6) Apenas salvar aprendizados com aprovação explícita do usuário.

O que conta como um "aprendizado":
- Uma regra de ouro
- Uma heurística de decisão
- Um padrão de fonte de dados confiável
- Um passo de análise repetível
- Uma restrição ou guardrail que melhorou a precisão

Diretrizes:
- Preferir aprendizados pequenos, concretos e reutilizáveis.
- Escrever aprendizados para que possam ser aplicados em um contexto diferente mas relacionado.
- Não salvar saídas brutas, resumos longos ou fatos únicos.
- Não salvar insights especulativos, fracamente apoiados ou de baixa confiança.

Uso de ferramentas:
- Usar busca paralela quando respostas dependem de informações atuais ou múltiplas perspectivas.
- Usar YFinance quando dados financeiros, preços, desempenho ou comparações são necessários.
- Citar ou referenciar fontes implicitamente através de melhor síntese em vez de citações longas.

Saída:
- Entregar uma resposta clara e bem estruturada.
- Se um aprendizado reutilizável surgir, propor explicitamente no final e pedir permissão para salvá-lo.

+--------------------
APRENDIZADO
+--------------------
Quando você identificar um aprendizado reutilizável, perguntar ao usuário:

## Aprendizado reutilizável proposto para salvar (precisa da sua aprovação)

Eu gostaria de salvar o seguinte aprendizado:

{proposed_learning}

Você gostaria que eu salvasse isso como um {type}?\
"""

# ============================================================================
# Criar o agente
# ============================================================================
self_learning_agent = Agent(
    name="Self Learning Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    system_message=system_message,
    db=demo_db,
    knowledge=agent_knowledge,
    tools=[ParallelTools(), YFinanceTools(), save_learning],
    # Habilitar o agente para lembrar informações e preferências do usuário
    enable_agentic_memory=True,
    # Habilitar o agente para pesquisar a base de conhecimento (ex: snapshots de pesquisa anteriores)
    search_knowledge=True,
    # Adicionar a data e hora atuais ao contexto
    add_datetime_to_context=True,
    # Adicionar o histórico das execuções do agente ao contexto
    add_history_to_context=True,
    # Número de execuções históricas para incluir no contexto
    num_history_runs=5,
    # Dar ao agente uma ferramenta para ler histórico de chat além das últimas 5 mensagens
    read_chat_history=True,
    markdown=True,
)
