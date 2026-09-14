"""Fetch latest HTML from the official site and save reference copies."""
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "tokyo.html": "https://maps.chizutodesign.com/18kippu/",
    "osaka.html": "https://maps.chizutodesign.com/18kippu/osaka/",
}

ctx = ssl.create_default_context()

for filename, url in SOURCES.items():
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx) as resp:
        html = resp.read().decode("utf-8")
    out = ROOT / filename
    out.write_text(html, encoding="utf-8")
    print(f"{filename}: {len(html)} bytes from {url}")

print("\nRun build.py to generate tokyo.html and osaka.html")
