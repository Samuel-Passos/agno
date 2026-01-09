# Exemplos de Fala para Texto

Exemplos de fala para texto usando OpenAI e Gemini. Estes exemplos demonstram como transcrever arquivos de áudio usando Agno. Com base no caso de uso, qualquer um dos cookbooks pode ser usado como ponto de partida para sua própria implementação.

## Autenticação

Definir as variáveis de ambiente `OPENAI_API_KEY` e `GEMINI_API_KEY` com suas chaves de API OpenAI e Gemini.

**Início rápido:**
Ir para https://platform.openai.com/ e https://console.cloud.google.com/ para obter suas chaves de API.

## Recursos

- **Transcrição Estruturada** - Obter saída estruturada do arquivo de áudio
- **Transcrição Simples** - Obter transcrição simples do arquivo de áudio
- **Workflow** - Usar um Workflow Agno para transcrever o arquivo de áudio

Os Agentes e o Workflow podem ser usados com AgentOS para criar uma aplicação completa de fala para texto.

## Começando

### 1. Clonar o repositório

```shell
git clone https://github.com/agno-ai/agno.git
cd agno/cookbook/02_examples/other/speech_to_text
```

### 2. Criar e ativar um ambiente virtual

```shell
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Definir variáveis de ambiente

Seguir as instruções para obter suas chaves de API OpenAI e Gemini. Certificar-se de copiar as chaves de API e defini-las nas variáveis de ambiente `OPENAI_API_KEY` e `GEMINI_API_KEY`.

```shell
export OPENAI_API_KEY=xxx
export GEMINI_API_KEY=xxx
```

### 4. Executar Postgres com PgVector

Postgres armazena sessões de agentes, memória, conhecimento e estado. Instalar [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/) e executar:

```bash
./cookbook/scripts/run_pgvector.sh
```

Ou executar diretamente:

```bash
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  agnohq/pgvector:16
```

### 5. Executar os exemplos

```shell
python stt_openai_agent_simple.py
```

```shell
python stt_openai_agent.py
```

```shell
python stt_gemini_agent.py
```
