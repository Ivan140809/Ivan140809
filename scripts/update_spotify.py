import os
import re
import base64
import requests
from datetime import datetime, timezone

CLIENT_ID     = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]
PLAYLIST_ID   = "54xDppMIQXxjzAtKV2oiFA"

README_PATH  = "README.md"
MARKER_START = "<!-- SPOTIFY_START -->"
MARKER_END   = "<!-- SPOTIFY_END -->"


def get_token():
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
        headers={"Authorization": f"Basic {credentials}"},
    )
    if not r.ok:
        print(f"Token error {r.status_code}: {r.text}")
        print(f"CLIENT_ID length: {len(CLIENT_ID)}")
        print(f"REFRESH_TOKEN length: {len(REFRESH_TOKEN)}")
    r.raise_for_status()
    return r.json()["access_token"]


def get_playlist_tracks(token, limit=5):
    r = requests.get(
        f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks",
        params={"limit": limit},
        headers={"Authorization": f"Bearer {token}"},
    )
    if not r.ok:
        print(f"Error {r.status_code}: {r.text}")
        r.raise_for_status()
    tracks = []
    for item in r.json().get("items", []):
        t = item.get("track")
        if not t:
            continue
        name   = t["name"]
        artist = ", ".join(a["name"] for a in t["artists"])
        url    = t["external_urls"]["spotify"]
        ms     = t["duration_ms"]
        mins, secs = divmod(ms // 1000, 60)
        tracks.append({"name": name, "artist": artist, "url": url, "duration": f"{mins}:{secs:02d}"})
    return tracks


def build_section(tracks):
    now  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = ""
    for i, t in enumerate(tracks):
        num = f"`{i+1}`"
        rows += f'| {num} | [**{t["name"]}**]({t["url"]}) | {t["artist"]} | `{t["duration"]}` |\n'

    return f"""{MARKER_START}
| # | Canción | Artista | Duración |
|:---:|:---|:---|:---:|
{rows}
<sub>🎧 De mi playlist en Spotify · actualizado {now}</sub>
{MARKER_END}"""


def update_readme(section):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        re.DOTALL,
    )
    if not pattern.search(content):
        print("WARN: markers not found in README")
        return

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(pattern.sub(section, content))
    print("README updated ✓")


if __name__ == "__main__":
    token  = get_token()
    tracks = get_playlist_tracks(token)
    if tracks:
        update_readme(build_section(tracks))
    else:
        print("No tracks found")
