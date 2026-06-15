"""
Corre este script UNA SOLA VEZ en tu PC para obtener el REFRESH_TOKEN.
Necesitas: pip install requests
"""
import base64
import urllib.parse
import requests

CLIENT_ID     = input("Client ID: ").strip()
CLIENT_SECRET = input("Client Secret: ").strip()
REDIRECT_URI  = "https://example.com/callback"
SCOPE         = "playlist-read-public playlist-read-private"

auth_url = (
    "https://accounts.spotify.com/authorize?"
    + urllib.parse.urlencode({
        "client_id":     CLIENT_ID,
        "response_type": "code",
        "redirect_uri":  REDIRECT_URI,
        "scope":         SCOPE,
    })
)

print("\n1. Abre este link en tu navegador:\n")
print(auth_url)
print("\n2. Acepta los permisos en Spotify.")
print("3. Te redirige a una página de error (eso es normal).")
print("4. Copia la URL completa de esa página y pégala aquí.\n")

redirect = input("URL completa de la página de error: ").strip()
code = urllib.parse.parse_qs(urllib.parse.urlparse(redirect).query).get("code", [None])[0]

if not code:
    print("No se encontró el código en la URL. Inténtalo de nuevo.")
    exit(1)

credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
r = requests.post(
    "https://accounts.spotify.com/api/token",
    data={
        "grant_type":   "authorization_code",
        "code":         code,
        "redirect_uri": REDIRECT_URI,
    },
    headers={"Authorization": f"Basic {credentials}"},
)
r.raise_for_status()
data = r.json()

print("\n✅ Agrega estos secrets en tu repo de GitHub:\n")
print(f"  SPOTIFY_CLIENT_ID     = {CLIENT_ID}")
print(f"  SPOTIFY_CLIENT_SECRET = {CLIENT_SECRET}")
print(f"  SPOTIFY_REFRESH_TOKEN = {data['refresh_token']}")
