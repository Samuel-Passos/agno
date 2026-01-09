# Workflow de Análise de Empresas

Um workflow de análise de empresas que usa estruturas estratégicas para avaliar fornecedores e gerar relatórios de inteligência de negócios.

## Visão Geral

Este workflow analisa empresas usando 8 agentes especializados que realizam pesquisas em múltiplas estruturas estratégicas incluindo PESTLE, Cinco Forças de Porter e Matriz Kraljic. Ele gera relatórios abrangentes de análise de fornecedores para tomada de decisão de compras.

## Começando

### Pré-requisitos
- Chave de API OpenAI
- API Firecrawl. Você pode obter uma em https://www.firecrawl.dev/app/api-keys

### Configuração
```bash
export OPENAI_API_KEY="your-openai-key"
export FIRECRAWL_API_KEY="your-firecrawl-key"
```

Instalar dependências

```
pip install agno firecrawl-py openai
```

Executar o workflow

```
python cookbook/examples/workflows_2/company_analysis/run_workflow.py
```

## Fluxo de Análise

O workflow analisa empresas através de estruturas estratégicas:

```
Workflow de Análise de Empresas
├── Pesquisa de Visão Geral da Empresa
├── Análise Estratégica Paralela
│   ├── Análise de Barreiras de Troca
│   ├── Análise PESTLE
│   ├── Análise das Cinco Forças de Porter
│   ├── Análise da Matriz Kraljic
│   ├── Análise de Direcionadores de Custo
│   └── Pesquisa de Fornecedores Alternativos
└── Compilação de Relatório
```

O workflow usa 8 agentes especializados executando em paralelo para realizar análise estratégica abrangente em múltiplas estruturas, depois compila os resultados em um relatório de compras pronto para executivos. 