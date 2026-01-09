# Agentes Gemini

Agentes de IA de nível de produção alimentados por Gemini e Agno. Este cookbook demonstra como combinar as capacidades nativas do Gemini com o runtime de agentes, memória, conhecimento e sistemas de gerenciamento de estado do Agno.

## Agentes

| Agente | Descrição | Recursos Principais |
| :--- | :--- | :--- |
| **Simple Research Agent** | Pesquisa web com respostas citadas | Grounding, Search |
| **Creative Studio** | Geração de imagens de alta qualidade | Imagen |
| **Product Comparison** | Analisar e comparar conteúdo de URLs | URL Context |
| **Self-Learning Agent** | Responde perguntas e aprende de execuções bem-sucedidas | Parallel Search, YFinance, Knowledge Base |
| **Self-Learning Research Agent** | Rastreia consenso da internet ao longo do tempo com snapshots históricos | Parallel Search, Continuous Learning |
| **PaL (Plan and Learn)** | Planejamento e execução disciplinados com aprendizado | Session State, Knowledge Base, Parallel Search |

## ✨ Destaque: PaL — Agente Planejar e Aprender

> *Planejar. Executar. Aprender. Repetir.*

PaL é um agente de execução disciplinado que:

- **Planeja** — Divide objetivos em passos com critérios de sucesso claros
- **Executa** — Trabalha através de passos sequencialmente, verificando conclusão
- **Adapta** — Modifica planos em meio ao voo quando requisitos mudam
- **Aprende** — Captura padrões reutilizáveis de execuções bem-sucedidas

**Novo padrão**: PaL usa o recurso incrível **Session State** do Agno — estado persistente que sobrevive através de turnos de conversa e sessões. Rastrear progresso, gerenciar workflows e construir agentes com estado.

```python
# Session state persists across runs
session_state={
    "objective": None,
    "plan": [],
    "current_step": 1,
    "status": "no_plan",
}
```

[→ See the full implementation](agents/pal_agent.py)

## Recursos Nativos do Gemini

Agno suporta todas as capacidades nativas do Gemini prontas para uso:

| Recurso | Parâmetro | Descrição |
| :--- | :--- | :--- |
| Google Search | `search=True` | Pesquisar na web (Gemini 2.0+) |
| Grounding | `grounding=True` | Pesquisar com citações |
| URL Context | `url_context=True` | Analisar conteúdo de página web |
| Imagen | `ImagenTools()` | Toolkit de geração de imagens |

## Por que Gemini + Agno

- **Velocidade** — Inferência rápida torna workflows de agentes responsivos
- **Raciocínio** — Raciocínio nativo forte com menos alucinações
- **Primitivas integradas** — Geração de imagens, contexto de URL e grounding são de primeira classe
- **Pronto para produção** — Agno fornece persistência, memória, conhecimento e gerenciamento de estado

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/agno-agi/agno.git
cd agno
```

### 2. Create and activate a virtual environment

```bash
uv venv .gemini-agents --python 3.12
source .gemini-agents/bin/activate
```

### 3. Install dependencies

```bash
uv pip install -r cookbook/02_examples/04_gemini/requirements.txt
```

### 4. Set environment variables

```bash
# Required for Gemini models
export GOOGLE_API_KEY=your-google-api-key

# Required for agents using parallel search
export PARALLEL_API_KEY=your-parallel-api-key
```

### 5. Run Postgres with PgVector

Postgres stores agent sessions, memory, knowledge, and state. Install [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/) and run:

```bash
./cookbook/scripts/run_pgvector.sh
```

Or run directly:

```bash
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql \
  -v pgvolume:/var/lib/postgresql \
  -p 5532:5432 \
  --name pgvector \
  agnohq/pgvector:18
```

### 6. Run the Agent OS

Agno provides a web interface for interacting with agents. Start the server:

```bash
python cookbook/02_examples/04_gemini/run.py
```

Then visit [os.agno.com](https://os.agno.com/?utm_source=github&utm_medium=cookbook&utm_campaign=gemini&utm_content=cookbook-gemini-flash&utm_term=gemini-flash) and add `http://localhost:7777` as an endpoint.

---

## Run Agents Individually

```bash
# Research with grounding and citations
python cookbook/02_examples/04_gemini/agents/simple_research_agent.py

# Image generation
python cookbook/02_examples/04_gemini/agents/creative_studio_agent.py

# Compare products from URLs
python cookbook/02_examples/04_gemini/agents/product_comparison_agent.py

# Self-learning agent
python cookbook/02_examples/04_gemini/agents/self_learning_agent.py

# Self-learning research agent
python cookbook/02_examples/04_gemini/agents/self_learning_research_agent.py

# PaL - Plan and Learn Agent
python cookbook/02_examples/04_gemini/agents/pal_agent.py
```

## File Structure

```
cookbook/02_examples/04_gemini/
├── agents/
│   ├── creative_studio_agent.py    # Image generation
│   ├── pal_agent.py                # Plan and Learn (session state)
│   ├── product_comparison_agent.py # URL comparison
│   ├── self_learning_agent.py      # Learning from tasks
│   ├── self_learning_research_agent.py  # Research with history
│   └── simple_research_agent.py    # Grounded search
├── assets/                         # Screenshots
├── db.py                           # Database configuration
├── run.py                          # Agent OS entrypoint
└── README.md
```
## Screenshots

<p align="center">
  <img src="assets/agentos_2.png" alt="Creative Studio Demo" width="500"/>
  <br>
  <em>Creative Studio: AI Image Generation with Imagen</em>
</p>

<p align="center">
  <img src="assets/agentos_3.png" alt="Research Agent Demo" width="500"/>
  <br>
  <em>Research Agent: Web Search &amp; Grounding</em>
</p>

<p align="center">
  <img src="assets/agentos_4.png" alt="Product Comparison Agent Demo" width="500"/>
  <br>
  <em>Product Comparison: Analyze products using URLs</em>
</p>

## Learn More

- [Agno Documentation](https://docs.agno.com/?utm_source=github&utm_medium=cookbook&utm_campaign=gemini&utm_content=cookbook-gemini-flash&utm_term=gemini-flash)
- [Gemini Native Features](https://docs.agno.com/integrations/models/native/google/overview/?utm_source=github&utm_medium=cookbook&utm_campaign=gemini&utm_content=cookbook-gemini-flash&utm_term=gemini-flash)
- [Session State Guide](https://docs.agno.com/basics/state/agent/?utm_source=github&utm_medium=cookbook&utm_campaign=gemini&utm_content=cookbook-gemini-flash&utm_term=gemini-flash)
- [Agent OS Overview](https://docs.agno.com/agent-os/overview/?utm_source=github&utm_medium=cookbook&utm_campaign=gemini&utm_content=cookbook-gemini-flash&utm_term=gemini-flash)
