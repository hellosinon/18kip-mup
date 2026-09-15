"""Build tokyo.html, osaka.html, and hukuoka.html."""
from __future__ import annotations

import json
import re
import ssl
import sys
import urllib.request
from pathlib import Path

from build_hukuoka import build_hukuoka

ROOT = Path(__file__).resolve().parent
TOKYO_URL = "https://maps.chizutodesign.com/18kippu/"
OSAKA_URL = "https://maps.chizutodesign.com/18kippu/osaka/"
HUKUOKA_URL = "https://maps.chizutodesign.com/18kippu/hukuoka/"

EDITIONS = {
    "tokyo": {
        "url": TOKYO_URL,
        "local_ref": ROOT / "tokyo.html",
        "out": ROOT / "tokyo.html",
        "other_link": '<div id="links"><a href="index.html">選択</a></div>\n',
        "remove_link": None,
    },
    "osaka": {
        "url": OSAKA_URL,
        "local_ref": ROOT / "osaka.html",
        "out": ROOT / "osaka.html",
        "other_link": '<div id="links"><a href="index.html">選択</a></div>\n',
        "remove_link": None,
    },
    "hukuoka": {
        "url": HUKUOKA_URL,
        "local_ref": ROOT / "hukuoka.html",
        "out": ROOT / "hukuoka.html",
        "other_link": '<div id="links"><a href="index.html">選択</a></div>\n',
        "remove_link": None,
    }
}

LINK_PATTERNS = [
    re.compile(r'<div id="links"><a href="[^"]*">.*?</a></div>\n', re.S),
]


def fetch(url: str) -> str:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx) as resp:
        return resp.read().decode("utf-8")


def clean_html(html: str, other_link: str) -> str:
    html = html.split("<!-- Cloudflare Pages Analytics -->")[0].rstrip()
    html = html + "\n</body>\n</html>\n"
    for pat in LINK_PATTERNS:
        html = pat.sub("", html)
    if other_link:
        html = html.replace('<div id="zoom">', other_link + '<div id="zoom">')
    return html


def extract_data(html: str, edition: str) -> None:
    data_dir = ROOT / "data" / edition
    data_dir.mkdir(parents=True, exist_ok=True)

    m = re.search(r"const D=(\{.*?\});\s*const map", html, re.S)
    if m:
        data = json.loads(m.group(1))
        (data_dir / "timetable.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  timetable: {len(data['info'])} stations")

    svg_m = re.search(r'(<svg id="map".*?</svg>)', html, re.S)
    if svg_m:
        (data_dir / "map.svg").write_text(svg_m.group(1), encoding="utf-8")
        print("  map.svg extracted")


def build_edition(name: str, cfg: dict, use_cache: bool = False) -> None:
    ref_path = cfg["local_ref"]
    if use_cache and ref_path.exists():
        html = ref_path.read_text(encoding="utf-8")
        print(f"{name}: using cached {ref_path.name}")
    else:
        print(f"{name}: fetching {cfg['url']}")
        html = fetch(cfg["url"])
        ref_path.write_text(html, encoding="utf-8")
        print(f"  saved {ref_path.name} ({len(html)} bytes)")

    cleaned = clean_html(html, cfg["other_link"])
    cfg["out"].write_text(cleaned, encoding="utf-8")
    print(f"  created {cfg['out'].name} ({cfg['out'].stat().st_size} bytes)")
    extract_data(cleaned, name)


def main() -> None:
    raw = [a.lower() for a in sys.argv[1:]]
    fetch = "--fetch" in raw
    args = [a for a in raw if not a.startswith("-")]
    want = set(args) if args else {"tokyo", "osaka", "hukuoka"}
    unknown = want - {"tokyo", "osaka", "hukuoka"}
    if unknown:
        raise SystemExit(f"unknown edition: {', '.join(sorted(unknown))}")
    for name, cfg in EDITIONS.items():
        if name in want:
            build_edition(
                name, cfg, use_cache=not fetch and cfg["out"].exists())
    if "hukuoka" in want:
        build_hukuoka()


if __name__ == "__main__":
    main()
