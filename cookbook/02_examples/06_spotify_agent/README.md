# Agente Spotify

Um Agente que pode pesquisar músicas, gerenciar playlists, obter recomendações personalizadas e controlar a reprodução no Spotify.

## Autenticação

Definir a variável de ambiente `SPOTIFY_TOKEN` com seu token de acesso do Spotify.

**Início rápido:**
Ir para https://developer.spotify.com/ e clicar em "See it in action" para obter um token. Isso funciona para pesquisar, criar playlists e obter suas faixas principais.

**Acesso completo (com reprodução):**
Executar `python spotify_auth.py` para obter um token com todos os escopos, incluindo controle de reprodução.

## Recursos

- **Faixas e artistas principais** - Obter suas músicas e artistas mais tocados (últimas 4 semanas, 6 meses ou de todos os tempos)
- **Pesquisa** - Pesquisar faixas, artistas, álbuns e playlists
- **Gerenciamento de playlists** - Criar, atualizar e gerenciar playlists
- **Recomendações** - Obter recomendações personalizadas de faixas com base em seeds e humor (energia, felicidade, dançabilidade)
- **Faixas principais do artista** - Obter as músicas mais populares de qualquer artista
- **Faixas do álbum** - Adicionar álbuns inteiros a playlists
- **Controle de reprodução** - Reproduzir, pausar, pular e buscar faixas

## Começando

### 1. Clonar o repositório

```shell
git clone https://github.com/agno-ai/agno.git
cd agno/cookbook/examples/spotify_agent
```

### 2. Criar e ativar um ambiente virtual

```shell
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Fazer login no Console de Desenvolvedor do Spotify e criar uma nova aplicação

- Ir para https://developer.spotify.com/ e clicar em "See it in action".
- Clicar em "Create an app".
- Inserir um nome para sua aplicação e clicar em "Create".
- Copiar o Client ID e Client Secret.
- Definir o Redirect URI como `http://127.0.0.1:8888/callback`. Você pode usar qualquer valor que quiser para a URL de callback. Mas certifique-se de usar o mesmo valor na variável `REDIRECT_URI` no arquivo `spotify_auth.py`.

### 4. Obter um token de acesso do Spotify

Inserir o Client ID e Client Secret que você copiou do Console de Desenvolvedor do Spotify e executar o script.

```shell
python spotify_auth.py
```

Seguir as instruções para obter um token de acesso do Spotify. Certificar-se de copiar o token de acesso e defini-lo na variável de ambiente `SPOTIFY_TOKEN`.

### 5. Definir variáveis de ambiente

```shell
export ANTHROPIC_API_KEY=xxx
export SPOTIFY_TOKEN=xxx
```

### 6. Instalar dependências

```shell
pip install -U anthropic agno sqlalchemy
```

### 7. Executar o agente

```shell
python spotify_agent.py
```

### 8. Conectar via AgentOS

- Abrir [os.agno.com](https://os.agno.com/)
- Adicionar seu AgentOS local executando em http://localhost:7777
- Começar a conversar com o Agente Spotify

## Exemplos de Prompts

- "Quais são minhas músicas mais tocadas das últimas 4 semanas?"
- "Quem são meus artistas principais de todos os tempos?"
- "Criar uma playlist de músicas felizes do Eminem e Coldplay"
- "Adicionar o álbum inteiro Abbey Road à minha playlist"
- "Encontrar músicas animadas semelhantes a Blinding Lights"
- "Atualizar minha playlist Good Vibes com mais faixas relaxantes"

## Nota sobre Controle de Reprodução

Para controlar a reprodução via API, você precisa de uma sessão ativa do Spotify. Se receber um erro "No active device", reproduzir e pausar qualquer música no Spotify primeiro - isso registra seu dispositivo nos servidores do Spotify e habilita comandos remotos.
