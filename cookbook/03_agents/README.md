# Livro de Receitas de Agentes Agno - Guia do Desenvolvedor

Bem-vindo ao **Livro de Receitas de Agentes Agno** - seu guia abrangente para construir agentes de IA inteligentes com Agno. Este livro de receitas contém exemplos práticos, padrões e melhores práticas para criar aplicações de IA poderosas usando o framework de agentes do Agno.

- [Features](#features)
  - [Tool Integration](#tool-integration)
  - [RAG & Knowledge](#rag--knowledge)
  - [Human-in-the-Loop](#human-in-the-loop)
  - [Multimodal Capabilities](#multimodal-capabilities)
  - [Async & Performance](#async--performance)
  - [State Management](#state-management)
  - [Event Handling & Streaming](#event-handling--streaming)
  - [Parser & Output Models](#parser--output-models)
  - [Advanced Patterns](#advanced-patterns)

### Recursos-Chave de Agentes

| Recurso | Descrição 
|---------|-------------
| **Memória** | Histórico de conversa persistente e aprendizado 
| **Ferramentas** | Integração de API externa e chamada de funções 
| **Gerenciamento de Estado** | Contexto baseado em sessão e persistência de dados 
| **Multimodal** | Capacidades de processamento de imagem, áudio e vídeo 
| **Humano no Loop** | Fluxos de trabalho de confirmação e entrada do usuário 
| **Suporte Assíncrono** | Operações concorrentes de alto desempenho 
| **Integração RAG** | Recuperação de conhecimento e geração aumentada


### Integração de Ferramentas
**APIs externas, funções e capacidades**

Agentes podem usar Agno ToolKits, funções personalizadas ou construir classes Toolkit personalizadas para integrações complexas.

**Exemplos:**
- [`cookbook/agents/tool_concepts`](cookbook/agents/tool_concepts)

### RAG e Conhecimento
**Geração Aumentada por Recuperação e sistemas de conhecimento**

Conectar agentes a bancos de dados vetoriais e bases de conhecimento para recuperação inteligente de documentos e resposta a perguntas.

**Exemplos:**
- [`rag/traditional_rag_lancedb.py`](./rag/traditional_rag_lancedb.py) - Recuperação de conhecimento baseada em vetores
- [`rag/agentic_rag_pgvector.py`](./rag/agentic_rag_pgvector.py) - RAG Agente com Pgvector
- [`rag/agentic_rag_with_reranking.py`](./rag/agentic_rag_with_reranking.py) - Recuperação aprimorada com reranking

Ver todos os exemplos [aqui](./rag) 

### Humano no Loop
**Confirmação do usuário, entrada e fluxos de trabalho interativos**

Construir agentes que podem pausar para confirmação do usuário, coletar entrada dinâmica ou integrar com sistemas externos que requerem supervisão humana.

**Exemplos:**
- [`human_in_the_loop/confirmation_required.py`](./human_in_the_loop/confirmation_required.py) - Confirmação de execução de ferramenta
- [`human_in_the_loop/user_input_required.py`](./human_in_the_loop/user_input_required.py) - Coleta de entrada dinâmica do usuário
- [`human_in_the_loop/external_tool_execution.py`](./human_in_the_loop/external_tool_execution.py) - Integração com sistema externo

Ver todos os exemplos [aqui](./human_in_the_loop)

### Capacidades Multimodais
**Processamento de imagem, áudio e vídeo**

Processar e analisar múltiplos tipos de mídia incluindo imagens, arquivos de áudio e conteúdo de vídeo.

**Exemplos:**
- [`multimodal/image_to_text.py`](./multimodal/image_to_text.py) - Análise e descrição de imagem
- [`multimodal/audio_sentiment_analysis.py`](./multimodal/audio_sentiment_analysis.py) - Processamento de áudio
- [`multimodal/video_caption_agent.py`](./multimodal/video_caption_agent.py) - Compreensão de conteúdo de vídeo

Ver todos os exemplos [aqui](./multimodal)

### Assíncrono e Desempenho
**Operações de alto desempenho e concorrentes**

Construir agentes de alto desempenho com suporte assíncrono para operações concorrentes e streaming em tempo real.

**Exemplos:**
- [`async/basic.py`](./async/basic.py) - Uso básico de agente assíncrono
- [`async/gather_agents.py`](./async/gather_agents.py) - Execução concorrente de agentes
- [`async/streaming.py`](./async/streaming.py) - Respostas de streaming em tempo real

Ver todos os exemplos [aqui](./async)

### Gerenciamento de Estado
**Persistência de sessão e gerenciamento de contexto**

Manter estado de conversa entre sessões, armazenar dados do usuário e gerenciar interações multi-turno com contexto persistente.

**Exemplos:**
- [`state/session_state_basic.py`](./state/session_state_basic.py) - Uso básico de estado de sessão
- [`state/session_state_in_instructions.py`](./state/session_state_in_instructions.py) - Usando estado em instruções
- [`state/session_state_multiple_users.py`](./state/session_state_multiple_users.py) - Cenários multi-usuário

Ver todos os exemplos [aqui](./state)

### Manipulação de Eventos e Streaming
**Monitoramento de eventos em tempo real e streaming**

Capturar eventos de agente durante streaming para monitoramento, depuração ou construção de UIs interativas com atualizações em tempo real.

**Exemplos:**
- [`events/basic_agent_events.py`](./events/basic_agent_events.py) - Manipulação de eventos de chamada de ferramenta
- [`events/reasoning_agent_events.py`](./events/reasoning_agent_events.py) - Captura de eventos de raciocínio

### Modelos de Parser e Saída
**Modelos especializados para diferentes estágios de processamento**

Usar diferentes modelos para raciocínio vs análise de saídas estruturadas, ou para gerar respostas finais, otimizando para custo e desempenho.

**Benefícios do Modelo de Parser:**
- Otimização de custo com modelos de análise mais baratos
- Melhor consistência de saída estruturada
- Separar preocupações de raciocínio de análise

**Benefícios do Modelo de Saída:**
- Controle de qualidade para respostas finais
- Consistência de estilo em diferentes casos de uso
- Gerenciamento de custo para geração final cara

**Exemplos:**
- [`other/parse_model.py`](./other/parse_model.py) - Modelo de parser para saídas estruturadas
- [`other/output_model.py`](./other/output_model.py) - Modelo de saída para respostas finais

### Outros Padrões

Alguns outros padrões incluem integração de banco de dados, gerenciamento de sessão e injeção de dependência para aplicações de produção.

**Exemplos:**
- [`db/`](./db/) - Padrões de integração de banco de dados
- [`session/`](./session/) - Gerenciamento avançado de sessão  
- [`dependencies/`](./dependencies/) - Padrões de injeção de dependência

---