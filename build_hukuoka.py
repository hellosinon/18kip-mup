"""Build hukuoka.html and a schematic SVG from data/福岡/timetable.json."""
from __future__ import annotations

import json
import math
import re
from collections import deque
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA: dict = {}
ORIGIN = "博多"
CX, CY = 365.7, 493.2
RING = 17.01
W, H = 595.3, 841.9
ORIGIN_MIN = 5 * 60  # 05:00 博多始発

# 0 = 北. 博多からの見取り図:
#   北: 岡山・広島 / 東: 小倉・下関 / 西: 佐世保 / 南: 鳥栖・久留米
#   南西: 長崎→熊本→鹿児島 / 南東: 大分→宮崎
BEARING = {
    "博多": 0,
    "吉塚": 20,
    "香椎": 50,
    "西戸崎": 55,
    "宇美": 40,
    "桂川": 300,
    "新飯塚": 295,
    "直方": 290,
    "田川後藤寺": 285,
    "添田": 280,
    "赤間": 80,
    "折尾": 85,
    "若松": 95,
    "黒崎": 88,
    "小倉": 95,
    "門司": 70,
    "門司港": 98,
    "下関": 55,
    "厚狭": 50,
    "新山口": 28,
    "防府": 20,
    "徳山": 12,
    "岩国": 6,
    "宮島口": 3,
    "広島": 0,
    "海田市": 358,
    "呉": 348,
    "西条": 1,
    "三原": 2,
    "糸崎": 3,
    "福山": 1,
    "岡山": 0,
    "三次": 350,
    "長門市": 60,
    "東萩": 40,
    "津和野": 20,
    "益田": 355,
    "行橋": 112,
    "中津": 118,
    "宇佐": 124,
    "別府": 130,
    "大分": 135,
    "臼杵": 137,
    "佐伯": 139,
    "延岡": 142,
    "日向": 144,
    "日向市": 144,
    "高鍋": 147,
    "宮崎": 150,
    "南宮崎": 152,
    "都城": 155,
    "隼人": 168,
    "鳥栖": 172,
    "久留米": 188,
    "大牟田": 200,
    "玉名": 204,
    "熊本": 198,
    "宇土": 205,
    "三角": 220,
    "八代": 196,
    "新八代": 197,
    "人吉": 175,
    "水俣": 188,
    "出水": 193,
    "川内": 191,
    "鹿児島中央": 190,
    "鹿児島": 188,
    "指宿": 200,
    "日田": 120,
    "由布院": 128,
    "肥後大津": 150,
    "阿蘇": 142,
    "豊後竹田": 138,
    "佐賀": 242,
    "久保田": 232,
    "唐津": 255,
    "西唐津": 258,
    "伊万里": 262,
    "江北": 228,
    "肥前山口": 228,
    "肥前鹿島": 226,
    "諫早": 222,
    "長崎": 220,
    "武雄温泉": 252,
    "有田": 262,
    "早岐": 266,
    "佐世保": 270,
    "ハウステンボス": 268,
}

# 平日・博多始発の最速到達の目安 (arr, dep)
STATION_TIMES: dict[str, tuple[str, str]] = {
    "博多": ("", "05:00"),
    "吉塚": ("05:04", "05:08"),
    "香椎": ("05:12", "05:18"),
    "西戸崎": ("05:42", ""),
    "宇美": ("05:48", ""),
    "桂川": ("05:32", "05:36"),
    "新飯塚": ("05:48", "05:52"),
    "直方": ("06:08", "06:14"),
    "田川後藤寺": ("06:22", "06:30"),
    "添田": ("06:55", ""),
    "赤間": ("05:28", "05:28"),
    "折尾": ("05:42", "05:48"),
    "若松": ("06:18", ""),
    "黒崎": ("05:50", "05:50"),
    "小倉": ("06:05", "06:12"),
    "門司": ("06:12", "06:16"),
    "門司港": ("06:28", ""),
    "下関": ("06:22", "06:28"),
    "厚狭": ("06:52", "07:00"),
    "新山口": ("07:38", "07:48"),
    "防府": ("07:56", "08:00"),
    "徳山": ("08:28", "08:32"),
    "岩国": ("09:18", "09:22"),
    "宮島口": ("10:02", "10:06"),
    "広島": ("10:18", "10:28"),
    "西条": ("10:55", "10:58"),
    "三原": ("11:22", "11:26"),
    "海田市": ("10:28", "10:34"),
    "呉": ("10:58", ""),
    "糸崎": ("11:18", "11:22"),
    "福山": ("11:48", "11:52"),
    "岡山": ("13:08", ""),
    "三次": ("12:12", ""),
    "長門市": ("08:22", "08:28"),
    "東萩": ("09:12", "09:16"),
    "津和野": ("09:38", "09:42"),
    "益田": ("10:28", ""),
    "行橋": ("06:32", "06:32"),
    "中津": ("07:08", "07:08"),
    "宇佐": ("07:28", "07:28"),
    "別府": ("08:18", "08:22"),
    "大分": ("08:32", "08:48"),
    "臼杵": ("09:12", "09:16"),
    "佐伯": ("09:52", "10:00"),
    "延岡": ("11:28", "11:36"),
    "日向": ("12:12", "12:16"),
    "日向市": ("12:12", "12:16"),
    "高鍋": ("13:12", "13:16"),
    "宮崎": ("13:42", "13:48"),
    "南宮崎": ("13:50", ""),
    "都城": ("14:48", "14:52"),
    "隼人": ("16:08", "16:12"),
    "鳥栖": ("05:18", "05:24"),
    "久留米": ("05:28", "05:34"),
    "大牟田": ("06:08", "06:12"),
    "玉名": ("06:40", "06:44"),
    "熊本": ("07:02", "07:12"),
    "宇土": ("07:22", "07:28"),
    "三角": ("08:08", ""),
    "八代": ("07:48", "07:56"),
    "新八代": ("08:02", "08:06"),
    "人吉": ("09:28", ""),
    "水俣": ("08:42", "08:46"),
    "出水": ("09:18", "09:22"),
    "川内": ("10:18", "10:22"),
    "鹿児島中央": ("11:22", "11:32"),
    "鹿児島": ("11:38", ""),
    "指宿": ("12:42", ""),
    "日田": ("07:18", "07:28"),
    "由布院": ("08:32", "08:42"),
    "肥後大津": ("07:42", "07:48"),
    "阿蘇": ("09:02", "09:08"),
    "豊後竹田": ("10:22", "10:32"),
    "佐賀": ("05:48", "05:52"),
    "久保田": ("05:58", "06:04"),
    "唐津": ("06:58", "07:04"),
    "西唐津": ("07:12", ""),
    "伊万里": ("07:52", ""),
    "江北": ("06:18", "06:24"),
    "肥前山口": ("06:18", "06:24"),
    "肥前鹿島": ("06:42", "06:46"),
    "諫早": ("07:42", "07:48"),
    "長崎": ("08:22", ""),
    "武雄温泉": ("06:48", "06:52"),
    "有田": ("07:10", "07:14"),
    "早岐": ("07:22", "07:32"),
    "佐世保": ("07:42", ""),
    "ハウステンボス": ("07:38", ""),
}

# 見取り図に載せる駅
MAJOR_STATIONS = {
    "博多", "小倉",
    # 山陽
    "門司", "下関", "新山口", "防府", "徳山", "岩国", "宮島口",
    "広島", "西条", "三原", "福山", "岡山",
    # 鹿児島
    "鳥栖", "久留米", "大牟田", "玉名", "熊本", "八代", "新八代",
    "出水", "川内", "鹿児島中央",
    # 長崎
    "佐賀", "肥前山口", "諫早", "長崎",
    # 佐世保
    "武雄温泉", "有田", "佐世保",
    # 大分
    "行橋", "中津", "宇佐", "別府", "大分",
    # 宮崎
    "佐伯", "延岡", "日向市", "高鍋", "宮崎", "南宮崎",
}

LINE_COLOR = {
    "起点": "#F00000",
    "鹿児島本線": "#F00000",
    "篠栗線": "#F00000",
    "福北ゆたか線": "#F00000",
    "香椎線": "#F00000",
    "後藤寺線": "#F00000",
    "日田彦山線": "#F00000",
    "筑豊本線": "#F00000",
    "日豊本線": "#F00000",
    "長崎本線": "#F00000",
    "佐世保線": "#F00000",
    "大村線": "#F00000",
    "唐津線": "#F00000",
    "筑肥線": "#F00000",
    "久大本線": "#F00000",
    "豊肥本線": "#F00000",
    "三角線": "#F00000",
    "肥薩線": "#F00000",
    "指宿枕崎線": "#F00000",
    "山陽本線": "#0099D9",
    "美祢線": "#0099D9",
    "山口線": "#0099D9",
    "山陰本線": "#0099D9",
    "呉線": "#0099D9",
    "芸備線": "#0099D9",
    "肥薩おれんじ鉄道": "#F39800",
}

EDITION_LINKS = {
    "tokyo": ("tokyo.html", "東京編"),
    "osaka": ("osaka.html", "大阪編"),
    "hukuoka": ("hukuoka.html", "福岡編"),
}


def links_html(current: str) -> str:
    return '<div id="links">\n    <a href="index.html">選択</a>\n  </div>'


def mins(t: str) -> int:
    if not t:
        return ORIGIN_MIN
    h, m = map(int, t.split(":"))
    v = h * 60 + m
    if v < ORIGIN_MIN - 60:
        v += 24 * 60
    return v


def line_key(line: str) -> str:
    return (line or "").split("→")[0].split("(")[0].strip()


def color_for_line(line: str) -> str:
    return LINE_COLOR.get(line_key(line), "#F00000")


def is_transfer(name: str) -> bool:
    if name == ORIGIN:
        return False
    nxt = DATA["next"].get(name, [])
    parents = DATA["parents"].get(name, [])
    line = DATA["info"][name].get("line") or ""
    return len(nxt) > 1 or len(parents) > 1 or "→" in line


def collapse_to_major() -> None:
    majors = MAJOR_STATIONS & set(DATA["info"])
    parents = DATA["parents"]
    nxt = DATA["next"]

    new_parents: dict[str, list[str]] = {}
    for st in majors:
        if st == ORIGIN:
            continue
        found: list[str] = []
        seen: set[str] = set()

        def walk(cur: str) -> None:
            for p in parents.get(cur, []):
                if p in seen:
                    continue
                seen.add(p)
                if p in majors:
                    if p not in found:
                        found.append(p)
                else:
                    walk(p)

        walk(st)
        if found:
            new_parents[st] = found

    new_next: dict[str, list[dict]] = {}
    for st in majors:
        edges: list[dict] = []
        seen_to: set[str] = set()
        q: deque[tuple[str, dict]] = deque()
        for e in nxt.get(st, []):
            q.append((e["to"], e))
        visited: set[str] = set()
        while q:
            to, first = q.popleft()
            if to in visited:
                continue
            visited.add(to)
            if to in majors:
                if to not in seen_to:
                    seen_to.add(to)
                    edges.append({
                        "to": to,
                        "dep": first.get("dep", ""),
                        "line": first.get("line", ""),
                    })
            else:
                for e2 in nxt.get(to, []):
                    q.append((e2["to"], first))
        if edges:
            new_next[st] = edges

    DATA["info"] = {k: v for k, v in DATA["info"].items() if k in majors}
    DATA["parents"] = new_parents
    DATA["next"] = new_next
    DATA["col"] = {}
    for frm, edges in new_next.items():
        for e in edges:
            DATA["col"].setdefault(e["to"], {})[
                frm] = color_for_line(e.get("line") or "")


def apply_schematic_tree() -> None:
    """指定の方面・駅順で幹を組む。"""
    tree = [
        ("博多", "小倉"),
        ("小倉", "門司"),
        ("門司", "下関"),
        ("下関", "新山口"),
        ("新山口", "防府"),
        ("防府", "徳山"),
        ("徳山", "岩国"),
        ("岩国", "宮島口"),
        ("宮島口", "広島"),
        ("広島", "西条"),
        ("西条", "三原"),
        ("三原", "福山"),
        ("福山", "岡山"),
        ("小倉", "行橋"),
        ("行橋", "中津"),
        ("中津", "宇佐"),
        ("宇佐", "別府"),
        ("別府", "大分"),
        ("大分", "佐伯"),
        ("佐伯", "延岡"),
        ("延岡", "日向市"),
        ("日向市", "高鍋"),
        ("高鍋", "宮崎"),
        ("宮崎", "南宮崎"),
        ("博多", "鳥栖"),
        ("鳥栖", "久留米"),
        ("久留米", "大牟田"),
        ("大牟田", "玉名"),
        ("玉名", "熊本"),
        ("熊本", "八代"),
        ("八代", "新八代"),
        ("新八代", "出水"),
        ("出水", "川内"),
        ("川内", "鹿児島中央"),
        ("鳥栖", "佐賀"),
        ("佐賀", "肥前山口"),
        ("肥前山口", "諫早"),
        ("諫早", "長崎"),
        ("佐賀", "武雄温泉"),
        ("武雄温泉", "有田"),
        ("有田", "佐世保"),
    ]
    missing = [n for pair in tree for n in pair if n not in DATA["info"]]
    if missing:
        raise SystemExit(f"tree stations missing from info: {missing}")
    DATA["parents"] = {c: [p] for p, c in tree}
    DATA["next"] = {}
    DATA["col"] = {}
    for frm, to in tree:
        dep = (STATION_TIMES.get(frm, ("", ""))[1]
               or DATA["info"][frm].get("dep") or "")
        line = DATA["info"][to].get("line") or ""
        DATA["next"].setdefault(frm, []).append(
            {"to": to, "dep": dep, "line": line})
        DATA["col"].setdefault(to, {})[frm] = color_for_line(line)


def apply_times() -> None:
    extras = {
        "防府": "山陽本線",
        "宮島口": "山陽本線",
        "西条": "山陽本線",
        "三原": "山陽本線",
        "玉名": "鹿児島本線",
        "新八代": "鹿児島本線",
        "肥前山口": "長崎本線→佐世保線",
        "有田": "佐世保線",
        "日向市": "日豊本線",
        "高鍋": "日豊本線",
    }
    for name, line in extras.items():
        arr, dep = STATION_TIMES.get(name, ("", ""))
        DATA["info"].setdefault(name, {"arr": arr, "dep": dep, "line": line})
    for name, (arr, dep) in STATION_TIMES.items():
        if name not in DATA["info"]:
            continue
        DATA["info"][name]["arr"] = arr
        DATA["info"][name]["dep"] = dep
    for frm, edges in DATA["next"].items():
        frm_dep = STATION_TIMES.get(frm, ("", ""))[1]
        for e in edges:
            e["dep"] = frm_dep or e.get("dep") or ""
    DATA["col"] = {}
    for frm, edges in DATA["next"].items():
        for e in edges:
            DATA["col"].setdefault(e["to"], {})[
                frm] = color_for_line(e.get("line") or "")


def polar(hours: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg)
    r = max(0.0, hours) * RING
    return CX + r * math.sin(rad), CY - r * math.cos(rad)


# 鳥栖・久留米は実到着が早すぎて中心に重なるので、見取り図用に少し外側へ
MIN_VISUAL_H = {
    "鳥栖": 1.05,
    "久留米": 1.32,
    "佐賀": 1.25,
    "門司": 1.22,
    "大牟田": 1.55,
}


def pos_map() -> dict[str, tuple[float, float]]:
    out = {}
    for name, info in DATA["info"].items():
        deg = BEARING.get(name, 0)
        if name == ORIGIN:
            out[name] = (CX, CY)
            continue
        t = info.get("arr") or info.get("dep") or ""
        hours = (mins(t) - ORIGIN_MIN) / 60
        hours = max(hours, MIN_VISUAL_H.get(name, 0))
        out[name] = polar(hours, deg)
    return out


def f(n: float) -> str:
    return f"{n:.2f}"


def hour_label_svg(hour: int, x: float, y: float, rot: str) -> list[str]:
    """rot: south | west | east | north"""
    num = "24" if hour == 24 else str(hour)
    if rot == "south":
        ntr = f"matrix(2.0 0.0 0.0 2.0 {x - 9.4:.2f} {y + 1.7:.2f})"
        jtr = f"matrix(1.0 0.0 0.0 1.0 {x + 3.4:.2f} {y + 0.7:.2f})"
    elif rot == "north":
        ntr = f"matrix(2.0 0.0 0.0 2.0 {x - 9.4:.2f} {y + 1.7:.2f})"
        jtr = f"matrix(1.0 0.0 0.0 1.0 {x + 3.4:.2f} {y + 0.7:.2f})"
    elif rot == "east":
        ntr = f"matrix(0.0 -2.0 2.0 0.0 {x + 1.6:.2f} {y + 9.4:.2f})"
        jtr = f"matrix(0.0 -1.0 1.0 0.0 {x - 3.4:.2f} {y - 3.4:.2f})"
    else:
        ntr = f"matrix(0.0 2.0 -2.0 0.0 {x - 1.6:.2f} {y - 9.4:.2f})"
        jtr = f"matrix(0.0 1.0 -1.0 0.0 {x + 3.4:.2f} {y + 3.4:.2f})"
    return [
        f'    <text transform="{ntr}" fill="#6e6e6e" font-size="6" font-weight="500" '
        f'font-family="\'Barlow\', sans-serif">{num}</text>',
        f'    <text transform="{jtr}" fill="#6e6e6e" font-size="6" font-weight="500" '
        f'font-family="\'Noto Sans JP\', sans-serif">時</text>',
    ]


def build_svg(pos: dict[str, tuple[float, float]]) -> str:
    parts = [
        f'<svg id="map" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
        """    <defs>
      <filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="595.3" height="841.9"
        color-interpolation-filters="sRGB">
        <feGaussianBlur in="SourceAlpha" stdDeviation="1.5" result="b1" />
        <feFlood flood-color="#f2c14e" flood-opacity="0.85" result="f1" />
        <feComposite in="f1" in2="b1" operator="in" result="g1" />
        <feGaussianBlur in="SourceAlpha" stdDeviation="4" result="b2" />
        <feFlood flood-color="#f2c14e" flood-opacity="0.5" result="f2" />
        <feComposite in="f2" in2="b2" operator="in" result="g2" />
        <feMerge>
          <feMergeNode in="g2" />
          <feMergeNode in="g2" />
          <feMergeNode in="g1" />
          <feMergeNode in="g1" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
      <filter id="glowPick" filterUnits="userSpaceOnUse" x="0" y="0" width="595.3" height="841.9"
        color-interpolation-filters="sRGB">
        <feGaussianBlur in="SourceAlpha" stdDeviation="2" result="b1" />
        <feFlood flood-color="#f2c14e" flood-opacity="1" result="f1" />
        <feComposite in="f1" in2="b1" operator="in" result="g1" />
        <feGaussianBlur in="SourceAlpha" stdDeviation="5" result="b2" />
        <feFlood flood-color="#f2c14e" flood-opacity="0.75" result="f2" />
        <feComposite in="f2" in2="b2" operator="in" result="g2" />
        <feMerge>
          <feMergeNode in="g2" />
          <feMergeNode in="g2" />
          <feMergeNode in="g1" />
          <feMergeNode in="g1" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>""",
        f'    <rect width="{W}" height="{H}" fill="#000" />',
    ]
    for i in range(1, 20):
        r = i * RING
        sw = "0.75" if i % 3 == 0 else "0.5"
        dash = "" if i % 3 == 0 else ' stroke-dasharray="2,1.5"'
        parts.append(
            f'    <circle cx="{CX}" cy="{CY}" r="{r:.2f}" fill="none" stroke="#595757" '
            f'stroke-width="{sw}"{dash} />'
        )

    thick = []
    thin = []
    stub_dots = []
    for frm, edges in DATA["next"].items():
        x1, y1 = pos[frm]
        for e in edges:
            to = e["to"]
            x2, y2 = pos[to]
            color = ((DATA["col"].get(to) or {}).get(frm)
                     ) or color_for_line(e.get("line") or "")
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy) or 1
            stub = min(max(4.5, dist * 0.22), dist * 0.62)
            sx, sy = x1 + dx / dist * stub, y1 + dy / dist * stub
            thick.append(
                f'    <line data-e="{escape(frm)}&gt;{escape(to)}" data-sn="{escape(frm)}" '
                f'x1="{f(x1)}" y1="{f(y1)}" x2="{f(sx)}" y2="{f(sy)}" '
                f'stroke="#B5B5B6" stroke-width="2.9" stroke-linecap="round" />'
            )
            thin.append(
                f'    <line data-e="{escape(frm)}&gt;{escape(to)}" '
                f'x1="{f(sx)}" y1="{f(sy)}" x2="{f(x2)}" y2="{f(y2)}" '
                f'stroke="{color}" stroke-width="0.75" stroke-linecap="round" />'
            )
            stub_dots.append(
                f'    <circle data-e="{escape(frm)}&gt;{escape(to)}" data-sn="{escape(frm)}" '
                f'cx="{f(sx)}" cy="{f(sy)}" r="1.35" fill="#fff" />'
            )
    parts.extend(thick)
    parts.extend(thin)
    parts.extend(stub_dots)

    for name, (x, y) in pos.items():
        parts.append(
            f'    <circle class="onl" data-onl="{escape(name)}" cx="{f(x)}" cy="{f(y)}" r="1.55" fill="#fff" />'
        )
    for name, (x, y) in pos.items():
        xfer = is_transfer(name)
        col = color_for_line(DATA["info"][name].get("line") or "")
        fill = col if xfer else "#fff"
        r = 1.85 if name == ORIGIN else 1.35
        parts.append(
            f'    <circle data-st="{escape(name)}" data-sn="{escape(name)}" '
            f'cx="{f(x)}" cy="{f(y)}" r="{r:.2f}" fill="{fill}" />'
        )

    def label_at(name: str, x: float, y: float, tx: float, ty: float, size: float, weight: str) -> str:
        label = escape(name)
        halo = "2.2" if name == ORIGIN else "1.6"
        return (
            f'    <g data-st="{label}" data-sn="{label}" data-dx="0.00" data-dy="0.00">'
            f'<text x="{f(tx)}" y="{f(ty)}" fill="none" stroke="#000000" stroke-width="{halo}" '
            f'stroke-linejoin="round" font-size="{size:.0f}" font-weight="{weight}" '
            f'font-family="\'Noto Sans JP\', sans-serif">{label}</text>'
            f'<text x="{f(tx)}" y="{f(ty)}" fill="#fff" font-size="{size:.0f}" font-weight="{weight}" '
            f'font-family="\'Noto Sans JP\', sans-serif">{label}</text></g>'
        )

    placed: list[tuple[float, float]] = []
    others = [(n, p) for n, p in pos.items() if n != ORIGIN]
    others.sort(key=lambda np: math.hypot(
        np[1][0] - CX, np[1][1] - CY), reverse=True)
    for name, (x, y) in others:
        deg = BEARING.get(name, 0)
        rad = math.radians(deg)
        tx = x + 7.2 * math.sin(rad)
        ty = y - 7.2 * math.cos(rad) + 2.2
        if any(math.hypot(tx - px, ty - py) < 8.0 for px, py in placed):
            tx += 6.0 * math.cos(rad)
            ty += 6.0 * math.sin(rad)
        placed.append((tx, ty))
        parts.append(label_at(name, x, y, tx, ty, 6, "500"))

    ox, oy = pos[ORIGIN]
    parts.append(label_at(ORIGIN, ox, oy, ox - 22.0, oy + 2.5, 8, "700"))

    for hour in (9, 12, 15, 18, 21, 24):
        r = ((hour * 60) - ORIGIN_MIN) / 60 * RING
        parts.extend(hour_label_svg(hour, CX, CY + r, "south"))
        if hour in (9, 12, 15, 18, 21):
            parts.extend(hour_label_svg(hour, CX, CY - r, "north"))
        if hour in (12, 15, 18, 21, 24):
            parts.extend(hour_label_svg(hour, CX + r, CY, "east"))
            parts.extend(hour_label_svg(hour, CX - r, CY, "west"))

    parts.append("  </svg>")
    return "\n".join(parts)


def extract_style(src: str) -> str:
    m = re.search(r"(<style>.*?</style>)", src, re.S)
    if not m:
        raise SystemExit("style not found")
    style = m.group(1)
    extra = """
    #links a.cur {
      border-color: #f2c14e;
      color: #f2c14e
    }
"""
    return style.replace("  </style>", extra + "  </style>")


def chrome() -> str:
    return f"""  <header class="ver">
    <h1>各種到着マップ<span class="ed">福岡編</span></h1>
    <p class="en">SEISHUN 18 KIPPU ARRIVAL TIME MAP / FUKUOKA</p>
  </header>

  <div id="panel">
    <div id="grip" aria-label="開閉"></div>
    <div class="ph">
      <div class="n" id="pn"></div>
      <div class="t" id="pt"></div>
      <button class="x" id="px" aria-label="閉じる"><svg width="16" height="16" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg></button>
    </div>
    <div id="tabs"></div>
    <div class="pb">
      <ol id="po"></ol>
    </div>
  </div>

  {links_html("hukuoka")}
  <div id="zoom">
    <button id="in" aria-label="拡大">＋</button>
    <button id="out" aria-label="縮小">－</button>
  </div>

  <div id="tip"></div>

  <button id="info" aria-label="このマップについて">i</button>

  <div id="about">
    <div class="ab">
      <button class="x" id="abx" aria-label="閉じる"><svg width="20" height="20" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg></button>
      <h2>各種到着マップ<span class="ed">福岡編</span></h2>
      <p class="en2">SEISHUN 18 KIPPU ARRIVAL TIME MAP / FUKUOKA</p>
      <p>青春18きっぷを使用して、平日に博多駅を始発で出発したときの各駅の到着時刻を等時線で表現したマップです。駅を選ぶと、その駅までの往路と、同じ所要で折り返したときの博多着（復路）も表示します。地図表現の都合上、主な路線および駅のみ掲載しています。</p>
      <h3>使い方</h3>
      <ul>
        <li>駅をタップすると博多からの経路と復路の博多着を表示</li>
        <li>ピンチ / ホイールで拡大、ドラッグで移動</li>
        <li>左上の選択から他の編へ戻る</li>
        <li>複数の経路がある駅はタブで切り替え</li>
      </ul>
      <h3>使用データ</h3>
      <ul>
        <li>JR各社・並行在来線各社の時刻表を参考にした最速到達の目安</li>
      </ul>
      <p class="cau">
        ※各駅に対して最も早く到達する列車の目安を掲載しているため、乗換待ちの時間が長くなっている箇所があります。
        復路の博多着は、到着後すぐに往路と同じ所要時間で折り返した場合の目安です。
        ダイヤ改正などにより実際と異なる場合がありますので、お出かけの際は各自でお調べください。
      </p>
    </div>
  </div>

  <div id="hint">駅をタップすると経路が見られます<br>ピンチ / ホイールで拡大、ドラッグで移動</div>
"""


def extract_js(src: str) -> str:
    m = re.search(
        r"const map = document\.getElementById\('map'\);(.*)$", src, re.S)
    if not m:
        raise SystemExit("map JS not found")
    js = m.group(1)
    js = js.replace(
        "document.getElementById('pt').textContent = (name === ORIGIN) ? `${i.arr} 発` : `${i.arr} 着`;",
        "document.getElementById('pt').textContent = i.arr ? ((name === ORIGIN) ? `${i.arr} 発` : `${i.arr} 着`) : (name === ORIGIN ? `${i.dep} 発` : '');",
    )
    js = js.replace(
        "? (depT || d.dep || d.arr) + ' 発'",
        "? ((depT || d.dep || d.arr) ? (depT || d.dep || d.arr) + ' 発' : '')",
    )
    js = js.replace("大阪着", "博多着")
    if "sl-transition.js" not in js:
        js = js.replace("</body>", '  <script src="sl-transition.js"></script>\n</body>')
    return js


def build_hukuoka() -> None:
    global DATA
    DATA = json.loads(
        (ROOT / "data" / "福岡" / "timetable.json").read_text(encoding="utf-8")
    )
    apply_times()
    (ROOT / "data" / "福岡" / "timetable.json").write_text(
        json.dumps(DATA, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    collapse_to_major()
    apply_schematic_tree()
    pos = pos_map()
    missing = [n for n in DATA["info"] if n not in pos]
    if missing:
        raise SystemExit(f"missing positions: {missing}")
    svg = build_svg(pos)
    (ROOT / "data" / "福岡" / "map.svg").write_text(svg, encoding="utf-8")

    osaka = (ROOT / "osaka.html").read_text(encoding="utf-8")
    style = extract_style(osaka)
    js_tail = extract_js(osaka)
    d_json = json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))

    html = f"""<!DOCTYPE html>
<html lang="ja">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <title>各種到着マップ 福岡編</title>
  <meta name="description" content="青春18きっぷで平日に博多駅を始発で出発したとき、各駅に何時に到着できるかを等時線で表したマップです。">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet"
    href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Mono:wght@400;700&family=Barlow:wght@500&family=Hanken+Grotesk:wght@400;500;600&family=Noto+Sans+JP:wght@400;500;700&display=swap">
  <link rel="stylesheet" href="sl-transition.css">
  <script>try{{if(sessionStorage.getItem('sl-dir'))document.documentElement.classList.add('sl-wait')}}catch(e){{}}</script>
  <script>
    (function () {{
      var u = navigator.userAgent,
        ios = /iPhone|iPad|iPod/.test(u) || (/Macintosh/.test(u) && navigator.maxTouchPoints > 1),
        mac = /Macintosh/.test(u) && /Safari/.test(u) && !/Chrome|Chromium|Edg|OPR|Android/.test(u);
      if (ios || mac) document.documentElement.classList.add('is-safari');
    }})();
  </script>
  {style}
</head>

<body>
{svg}

{chrome()}
  <script>
    const ORIGIN = "{ORIGIN}";
    const D = {d_json};
    const map = document.getElementById('map');{js_tail}
"""
    out = ROOT / "hukuoka.html"
    out.write_text(html, encoding="utf-8")
    print(
        f"hukuoka: wrote {out.name} ({out.stat().st_size} bytes), stations={len(DATA['info'])}")


def main() -> None:
    build_hukuoka()


if __name__ == "__main__":
    main()
