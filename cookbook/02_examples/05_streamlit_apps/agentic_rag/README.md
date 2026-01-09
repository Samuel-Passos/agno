# Agente Agentic RAG

**Agentic RAG** é uma aplicação de chat que combina geração aumentada por recuperação com workflows agenticos.
Permite que os usuários façam perguntas com base em bases de conhecimento personalizadas, documentos e dados web, recuperem respostas conscientes do contexto e mantenham histórico de chat através de sessões.

> Nota: Fazer fork e clonar este repositório se necessário

### 1. Criar um ambiente virtual

```shell
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências

```shell
pip install -r cookbook/examples/streamlit_apps/agentic_rag/requirements.txt
```

### 3. Configurar Chaves de API

Necessário:

```bash
export OPENAI_API_KEY=your_openai_key_here
```

Opcional (para modelos adicionais):

```bash
export ANTHROPIC_API_KEY=your_anthropic_key_here
export GOOGLE_API_KEY=your_google_key_here
export GROQ_API_KEY=your_groq_key_here
```

### 4. Executar PgVector

> Instalar [docker desktop](https://docs.docker.com/desktop/install/mac-install/) primeiro.

- Executar usando um script auxiliar

```shell
./cookbook/scripts/run_pgvector.sh
```

- OU executar usando o comando docker run

```shell
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

### 5. Executar Aplicativo Agentic RAG

```shell
streamlit run cookbook/examples/streamlit_apps/agentic_rag/app.py
```

## 🔧 Personalização

### Seleção de Modelo

A aplicação suporta múltiplos provedores de modelos:

- OpenAI (o3-mini, gpt-4o)
- Anthropic (claude-3-5-sonnet)
- Google (gemini-2.0-flash-exp)
- Groq (llama-3.3-70b-versatile)

### Como Usar

- Abrir [localhost:8501](http://localhost:8501) no seu navegador.
- Enviar documentos ou fornecer URLs (sites, csv, txt e PDFs) para construir uma base de conhecimento.
- Inserir perguntas na interface de chat e obter respostas conscientes do contexto.
- O aplicativo também pode responder perguntas usando busca duckduckgo sem nenhum documento externo adicionado.

### Solução de Problemas

- **Conexão Docker Recusada**: Certificar-se de que os containers `pgvector` estão em execução (`docker ps`).
- **Erros de API OpenAI**: Verificar se `OPENAI_API_KEY` está definida e é válida.

## 📚 Documentação

Para informações mais detalhadas:

- [Documentação Agno](https://docs.agno.com)
- [Documentação Streamlit](https://docs.streamlit.io)

## 🤝 Suporte

Precisa de ajuda? Junte-se à nossa [comunidade Discord](https://agno.link/discord)
