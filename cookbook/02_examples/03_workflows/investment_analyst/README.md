# 🚀 Workflow de Análise de Investimentos

Um sistema sofisticado de análise de investimentos para capacidades de pesquisa avançadas usando workflows.

## 📋 **Visão Geral**

Este workflow demonstra como construir um workflow abrangente de análise de investimentos. Ele combina 8 agentes especializados em um workflow de análise adaptativo e inteligente que pode lidar com tudo, desde avaliações simples de ações até decisões complexas de investimento multi-empresa.

## 🚀 **Começando**

### **Pré-requisitos**
- Uma chave de API Supabase. Você pode obter uma em https://supabase.com/dashboard/account/tokens.
- Chave de API OpenAI

### **Configuração**
```bash
export SUPABASE_ACCESS_TOKEN="your-supabase-token"
export OPENAI_API_KEY="your-openai-key"
```

Instalar pacotes
```
pip install agno mcp openai
```


## 🏗️ **Fluxo de Análise**

Este workflow é projetado como o processo de pesquisa de uma empresa de investimentos sofisticada. Aqui estão os passos:

```
Jornada de Análise de Investimentos
├── 🗄️  Configuração de Banco de Dados (Sempre primeiro)
│   └── Cria projeto e esquema Supabase
├── 🔍 Pesquisa de Empresas (Fundação)
│   └── Coleta dados básicos da empresa
├── 🔀 Pipeline Inteligente Multi-Empresa
│   └── Se analisando múltiplas empresas:
│       ├── 🔄 Loop Iterativo de Empresas (até 5 rodadas)
│       └── ⚡ Análise Comparativa Paralela
├── 🎯 Roteamento de Avaliação de Risco
│   └── Escolhe estrutura de risco especializada
├── 💰 Seleção de Estratégia de Avaliação
│   └── Escolhe abordagem de avaliação por tipo de investimento
├── ⚠️  Análise Profunda de Alto Risco
│   └── Se investimento de alto risco detectado:
│       ├── ⚡ Modelagem de Risco Paralela
│       └── 🔄 Loop de Refinamento de Risco (até 3 rodadas)
├── 🏢 Due Diligence de Investimento Grande
│   └── Se investimento de $50M+:
│       └── ⚡ Análise paralela regulatória, de mercado e de gestão
├── 🌱 Pipeline de Análise ESG
│   └── Se análise ESG solicitada:
│       └── Avaliação e integração ESG sequencial
├── 📊 Análise de Contexto de Mercado
│   └── Se análise de mercado necessária:
│       └── ⚡ Análise paralela de mercado e setor
└── 📝 Decisão de Investimento e Relatório
    ├── 🔄 Loop de Construção de Consenso (até 2 rodadas)
    └── 📊 Síntese de Relatório Final
```

O workflow é adaptativo. Por exemplo, ao analisar uma única ação blue-chip, um caminho simples e direto é seguido, mas para avaliações complexas envolvendo múltiplas empresas, o workflow aciona automaticamente análises mais profundas.
