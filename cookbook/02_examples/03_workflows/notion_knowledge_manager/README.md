# Guia de Configuração de Integração Notion

Este guia ajudará você a configurar a integração Notion para o workflow de classificação de consultas.

## Pré-requisitos

1. Uma conta Notion
2. Python 3.9 ou superior
3. Framework Agno instalado

## Passo 1: Instalar Dependências Necessárias

```bash
pip install notion-client
```

## Passo 2: Criar uma Integração Notion

1. Ir para [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Clicar em **"+ New integration"**
3. Preencher os detalhes:
   - **Nome**: Dar um nome como "Agno Query Classifier"
   - **Workspace associado**: Selecionar seu workspace
   - **Tipo**: Integração interna
4. Clicar em **"Submit"**
5. Copiar o **"Internal Integration Token"** (começa com `secret_`)
   - ⚠️ Manter isso em segredo! Esta é sua `NOTION_API_KEY`

## Passo 3: Criar um Banco de Dados Notion

1. Abrir Notion e criar uma nova página
2. Adicionar um **Database** (você pode usar o comando "/database")
3. Configurar o banco de dados com estas propriedades:
   - **Nome** (Título) - Já existe por padrão
   - **Tag** (Select) - Clicar em "+" para adicionar uma nova propriedade
     - Tipo de propriedade: **Select**
     - Nome da propriedade: **Tag**
     - Adicionar estas opções:
       - travel
       - tech
       - general-blogs
       - fashion
       - documents

## Passo 4: Compartilhar Banco de Dados com Sua Integração

1. Abrir sua página de banco de dados no Notion
2. Clicar no menu **"..."** (três pontos) no canto superior direito
3. Rolar para baixo e clicar em **"Add connections"**
4. Pesquisar pelo nome da sua integração (ex: "Agno Query Classifier")
5. Clicar nela para conceder acesso

## Passo 5: Obter Seu ID de Banco de Dados

Seu ID de banco de dados está na URL da sua página de banco de dados:

```
https://www.notion.so/../{database_id}?v={view_id}
```

O `database_id` é a string de 32 caracteres (com hífens) entre o nome do workspace e o `?v=`.

Exemplo:
```
https://www.notion.so/myworkspace/28fee27fd9128039b3f8f47cb7ade7cb?v=...
                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                 Este é seu database_id
```

Copiar este ID de banco de dados.

## Passo 6: Definir Variáveis de Ambiente

Criar um arquivo `.env` na raiz do seu projeto ou exportar estas variáveis:

```bash
export NOTION_API_KEY="secret_your_integration_token_here"
export NOTION_DATABASE_ID="your_database_id_here"
export OPENAI_API_KEY="your_openai_api_key_here"
```

Ou em um arquivo `.env`:
```
NOTION_API_KEY=secret_your_integration_token_here
NOTION_DATABASE_ID=your_database_id_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Passo 7: Executar o Workflow

```bash
python cookbook/examples/workflows/thoughts_dump_notion/thoughts_dump_notion.py
```

O servidor iniciará em `http://localhost:7777` (ou outra porta).

Ir para [AgentOS](https://os.agno.com/) e testar!

