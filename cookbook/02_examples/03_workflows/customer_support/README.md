# Workflow de Suporte ao Cliente

Um sistema simples de suporte ao cliente que armazena soluções em cache para resolução mais rápida de consultas repetidas.

## Visão Geral

Este workflow demonstra o gerenciamento básico de estado de sessão do workflow construindo um sistema inteligente de suporte ao cliente. Ele armazena soluções em cache para consultas de clientes e retorna respostas instantâneas para correspondências exatas, enquanto gera novas soluções para problemas únicos.

O workflow usa estado de sessão para armazenar consultas resolvidas e suas soluções para reutilização eficiente.

## Começando

### Pré-requisitos
- Chave de API OpenAI

### Configuração
```bash
export OPENAI_API_KEY="your-openai-key"
```

Instalar dependências
```
pip install agno openai
```

Executar o workflow
```
python cookbook/examples/workflows_2/customer_support/run_workflow.py
```

## Fluxo do Workflow

O sistema de suporte ao cliente processa tickets através destes passos simples:

```
Pipeline de Resolução de Suporte ao Cliente
├── 🔍 Verificar Cache
│   ├── Procurar correspondência exata de consulta no estado de sessão
│   └── Retornar solução em cache se encontrada
└── 🔧 Gerar Nova Solução
    ├── Classificar a consulta do cliente
    ├── Gerar solução passo a passo
    └── Armazenar solução em cache para uso futuro
```

O workflow armazena soluções em cache de forma eficiente e aprende com cada ticket. Correspondências exatas de consulta são resolvidas instantaneamente do cache, enquanto novas consultas acionam geração e cache de soluções.

## Recursos de Estado de Sessão

**Cache Simples**: Armazena pares consulta-solução para recuperação instantânea

**Aprendizado Automático**: Cada nova solução é automaticamente armazenada em cache para reutilização futura

**Agentes Inteligentes**: Usa agente de triagem para classificação e agente de suporte para desenvolvimento de soluções

## Agentes

- **Agente de Triagem**: Classifica consultas de clientes por categoria, prioridade e tags
- **Agente de Suporte**: Desenvolve soluções claras, passo a passo para problemas de clientes

O workflow demonstra como o estado de sessão pode ser usado para construir sistemas de aprendizado que melhoram ao longo do tempo através de cache e reutilização. 