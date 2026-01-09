# Demonstração do Agno AgentOS

Esta demonstração mostra como executar um sistema multi-agente usando o **Agno AgentOS: um runtime de alta performance para sistemas multi-agente**:

## Começando

### 0. Clonar o repositório

```shell
git clone https://github.com/agno-agi/agno.git
cd agno
```

### 1. Criar um ambiente virtual

```shell
uv venv .demoenv --python 3.12
source .demoenv/bin/activate
```

### 2. Instalar dependências

```shell
uv pip install -r cookbook/01_demo/requirements.txt
```

### 3. Executar Postgres com PgVector

Vamos usar postgres para armazenar sessões de agentes, memórias, métricas, avaliações e conhecimento. Instale o [docker desktop](https://docs.docker.com/desktop/install/mac-install/) e execute o seguinte comando para iniciar um container postgres com PgVector.

```shell
./cookbook/scripts/run_pgvector.sh
```

OU use o comando docker run diretamente:

```shell
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

### 4. Exportar Chaves de API

Vamos usar serviços OpenAI, Anthropic e Parallel Search. Por favor, exporte as seguintes variáveis de ambiente:

```shell
export ANTHROPIC_API_KEY=***
export OPENAI_API_KEY=***
export PARALLEL_API_KEY=***
```

### 5. Executar o AgentOS de demonstração

```shell
python cookbook/01_demo/run.py
```

### 6. Conectar à Interface do AgentOS

- Abra a interface web: [os.agno.com](https://os.agno.com/)
- Conecte-se a http://localhost:7777 para interagir com o AgentOS de demonstração.

### Carregar Base de Conhecimento para o Agente de Conhecimento Agno

O Agente de Conhecimento Agno é um ótimo exemplo de construção de um agente de conhecimento usando RAG Agente. Ele carrega a documentação do Agno no pgvector e responde perguntas dos documentos. Ele usa o modelo de embedding OpenAI para incorporar os documentos e o pgvector para armazenar os embeddings.

Para popular a base de conhecimento, execute o seguinte comando:

```sh
python cookbook/01_demo/agents/agno_knowledge_agent.py
```

### Carregar dados para o Agente SQL

Para carregar os dados para o Agente SQL, execute:

```sh
python cookbook/01_demo/agents/sql/load_f1_data.py
```

Para popular a base de conhecimento, execute:

```sh
python cookbook/01_demo/agents/sql/load_sql_knowledge.py
```

### Carregar Base de Conhecimento para o Agente de Conhecimento Profundo

O Agente de Conhecimento Profundo é um ótimo exemplo de construção de um agente de pesquisa profunda usando Agno.

Para popular a base de conhecimento, execute o seguinte comando:

```sh
python cookbook/01_demo/agents/deep_knowledge_agent.py
```

---

## Recursos Adicionais

Precisa de ajuda, tem uma pergunta ou quer se conectar com a comunidade?

- 📚 **[Leia a Documentação do Agno](https://docs.agno.com)** para informações mais detalhadas.
- 💬 **Converse conosco no [Discord](https://agno.link/discord)** para discussões ao vivo.
- ❓ **Faça uma pergunta no [Discourse](https://agno.link/community)** para suporte da comunidade.
- 🐛 **[Reporte um Problema](https://github.com/agno-agi/agno/issues)** no GitHub se encontrar um bug ou tiver uma solicitação de recurso.
