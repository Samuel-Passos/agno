# Workflow de Descrição de Empresa

Um workflow que gera perfis abrangentes de fornecedores coletando informações de múltiplas fontes e entregando-os por e-mail.

## Visão Geral

Este workflow combina rastreamento web, mecanismos de busca, Wikipedia e análise de concorrentes para criar perfis detalhados de fornecedores. Ele processa informações da empresa através de 4 agentes especializados executando em paralelo, depois gera um relatório markdown estruturado e o envia por e-mail.

O workflow usa gerenciamento de estado de sessão do workflow para armazenar resultados de análise em cache. Se o mesmo fornecedor for analisado novamente, ele retorna resultados em cache em vez de re-executar o pipeline de análise caro.

## Começando

### Pré-requisitos
- Chave de API OpenAI
- Chave de API Resend para e-mails [https://resend.com/api-keys]
- Chave de API Firecrawl para rastreamento web [https://www.firecrawl.dev/app/api-keys]

### Configuração Rápida
```bash
export OPENAI_API_KEY="your-openai-key"
export RESEND_API_KEY="your-resend-key"
export FIRECRAWL_API_KEY="your-firecrawl-key"
```

Instalar dependências
```
pip install agno openai firecrawl-py resend
```

## Fluxo de Análise

O workflow processa informações do fornecedor através destes passos:

```
Workflow de Descrição de Empresa
├── 🔍 Verificar Análise em Cache
│   └── Se existir → Retornar Resultados em Cache
├── 🔍 Nova Análise Necessária
│   └── Se necessário → 
│       ├── 🔄 Coleta Paralela de Informações
│       │   ├── Rastreador Web (Firecrawl)
│       │   ├── Mecanismo de Busca (DuckDuckGo)
│       │   ├── Pesquisa na Wikipedia
│       │   └── Análise de Concorrentes
│       └── 📄 Geração de Perfil de Fornecedor
│           └── Cria relatório markdown estruturado e armazena resultados em cache
└── 📧 Entrega por E-mail
    └── Envia relatório para e-mail especificado
```

O workflow usa estado de sessão do workflow para armazenar resultados de análise de forma inteligente. Se o mesmo fornecedor for analisado novamente, ele retorna resultados em cache em vez de re-executar todo o pipeline de análise, economizando tempo e custos de API. 