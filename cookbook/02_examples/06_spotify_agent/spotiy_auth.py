import base64
import webbrowser
from urllib.parse import parse_qs, urlencode, urlparse

import requests

CLIENT_ID = "<YOUR_CLIENT_ID>"
CLIENT_SECRET = "<YOUR_CLIENT_SECRET>"

REDIRECT_URI = "http://127.0.0.1:8888/callback"

SCOPES = [
    "user-read-email",
    "user-read-private",
    "playlist-modify-private",
    "playlist-modify-public",
    "user-library-read",
    "user-library-modify",
    "user-top-read",
    "user-read-playback-state",
    "user-modify-playback-state",
]


def build_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
    }
    return "https://accounts.spotify.com/authorize?" + urlencode(params)


def extract_code(redirect_url: str) -> str | None:
    parsed = urlparse(redirect_url)
    query_params = parse_qs(parsed.query)
    code_list = query_params.get("code")
    if not code_list:
        return None
    return code_list[0]


def exchange_code_for_token(code: str) -> dict:
    token_url = "https://accounts.spotify.com/api/token"

    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_header = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    resp = requests.post(token_url, data=data, headers=headers)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    # 1) Abrir navegador para login do usuário + consentimento
    url = build_auth_url()
    print("\nAbrindo navegador para autenticação do Spotify...\n")
    webbrowser.open(url)

    print("1. Fazer login e aprovar as permissões.")
    print("2. Após o redirecionamento, copiar a URL COMPLETA da barra de endereços do navegador.")
    print("   (Mesmo que a página não carregue, a URL ainda contém '?code=...')\n")

    redirect_url = input("Colar a URL de redirecionamento completa aqui:\n> ").strip()

    # 2) Extrair ?code=... da URL
    code = extract_code(redirect_url)
    if not code:
        print("\nNão foi possível encontrar 'code' na URL. Você colou corretamente?")
        exit(1)

    print("\nTrocando código por tokens...")

    # 3) Trocar código de autenticação por tokens de acesso + atualização
    tokens = exchange_code_for_token(code)

    print("\n==================== TOKEN SPOTIFY ====================")
    print(f"SPOTIFY_TOKEN={tokens.get('access_token')}")
    print("========================================================\n")

    print("\n==================== INFORMAÇÕES DO TOKEN SPOTIFY ====================")
    print("token_type   :", tokens.get("token_type"))
    print("expires_in   :", tokens.get("expires_in"))
    print("scope        :", tokens.get("scope"))
    print("refresh_token:", tokens.get("refresh_token"))
    print("========================================================\n")
