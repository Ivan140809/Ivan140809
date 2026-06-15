"""
Corre este script UNA SOLA VEZ en tu PC para obtener el REFRESH_TOKEN.
Necesitas: pip install requests
"""
import base64
import urllib.parse
import http.server
import webbrowser
import threading
import requests

CLIENT_ID     = input("Client ID de tu Spotify App: ").strip()
CLIENT_SECRET = input("Client Secret de tu Spotify App: ").strip()
REDIRECT_URI  = "http://localhost:8888/callback"
SCOPE         = "user-read-recently-played"

auth_url = (
    "https://accounts.spotify.com/authorize?"
    + urllib.parse.urlencode({
        "client_id":     CLIENT_ID,
        "response_type": "code",
        "redirect_uri":  REDIRECT_URI,
        "scope":         SCOPE,
    })
)

code_holder = {}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            code_holder["code"] = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Listo! Puedes cerrar esta ventana.</h2>")
        else:
            self.send_response(400)
            self.end_headers()
    def log_message(self, *_): pass

server = http.server.HTTPServer(("localhost", 8888), Handler)
thread = threading.Thread(target=server.handle_request)
thread.start()

print(f"\nAbriendo Spotify en tu navegador...")
webbrowser.open(auth_url)
thread.join()

code = code_holder.get("code")
if not code:
    print("No se recibió el código. Inténtalo de nuevo.")
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

print("\n✅ TOKENS OBTENIDOS — guárdalos como secrets en GitHub:\n")
print(f"  SPOTIFY_CLIENT_ID     = {CLIENT_ID}")
print(f"  SPOTIFY_CLIENT_SECRET = {CLIENT_SECRET}")
print(f"  SPOTIFY_REFRESH_TOKEN = {data['refresh_token']}")
