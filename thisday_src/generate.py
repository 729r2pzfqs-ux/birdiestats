#!/usr/bin/env python3
"""
Generator for the "This Day in Golf" section of birdiestats.com.

Produces:
  /this-day-in-golf/index.html                       (landing page)
  /this-day-in-golf/<month>-<day>/index.html         (366 day pages)

Also (idempotent):
  - injects an "On This Day" nav link into every existing page
  - appends the new URLs to sitemap.xml

Per-day golf-history data is authored in thisday_src/month-NN.json (one file
per month). Each day maps to a list of event objects:
    {"year": int, "title": str, "text": str,
     "category": "birth|championship|record|death|milestone",
     "player_slug": str|null}

Run from anywhere; paths are resolved relative to the repo root (parent of
this file's dir):  python3 thisday_src/generate.py
"""

import os
import re
import json
import html

# ---------------------------------------------------------------------------
# Paths / constants
# ---------------------------------------------------------------------------
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC_DIR)                       # repo root
SECTION_DIR = os.path.join(ROOT, "this-day-in-golf")
PLAYERS_DIR = os.path.join(ROOT, "players")
BUILD_DATE = "2026-06-26"
GA_ID = "G-WEHSP085R8"
SITE = "https://birdiestats.com"

# Featured date on the landing page (today's build date: June 26).
FEATURE_MONTH, FEATURE_DAY = "june", 26

MONTHS = [
    ("january", 31), ("february", 29), ("march", 31), ("april", 30),
    ("may", 31), ("june", 30), ("july", 31), ("august", 31),
    ("september", 30), ("october", 31), ("november", 30), ("december", 31),
]
MONTH_NUM = {name: i + 1 for i, (name, _) in enumerate(MONTHS)}
MONTH_TITLE = {name: name.capitalize() for name, _ in MONTHS}
MONTH_ABBR = {name: name.capitalize()[:3] for name, _ in MONTHS}

# Ordered flat list of (month_name, day) for prev/next navigation (366 entries).
ALL_DAYS = []
for _m, _n in MONTHS:
    for _d in range(1, _n + 1):
        ALL_DAYS.append((_m, _d))


def slug_for(month, day):
    return f"{month}-{day}"


def esc(s):
    """Escape text for safe placement in HTML body / attributes."""
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------------------
# Player slug -> display name (read straight from each player's page <h1>)
# ---------------------------------------------------------------------------
_H1_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.S)


def _slug_to_name_fallback(slug):
    parts = slug.split("-")
    out = []
    for p in parts:
        if p in ("ii", "iii", "iv"):
            out.append(p.upper())
        elif p in ("jr", "sr"):
            out.append(p.capitalize() + ".")
        else:
            out.append(p.capitalize())
    return " ".join(out)


def _load_player_names():
    names = {}
    if os.path.isdir(PLAYERS_DIR):
        for slug in os.listdir(PLAYERS_DIR):
            page = os.path.join(PLAYERS_DIR, slug, "index.html")
            if not os.path.isfile(page):
                continue
            try:
                with open(page, encoding="utf-8") as fh:
                    head = fh.read(8000)
            except OSError:
                continue
            m = _H1_RE.search(head)
            if m:
                names[slug] = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    return names


PLAYER_NAMES = _load_player_names()


def player_display_name(slug):
    return PLAYER_NAMES.get(slug) or _slug_to_name_fallback(slug)


def player_exists(slug):
    return os.path.isfile(os.path.join(PLAYERS_DIR, slug, "index.html"))


# ---------------------------------------------------------------------------
# Load per-month event data
# ---------------------------------------------------------------------------
def load_events():
    """Return dict {(month_name, day): [event, ...]} sorted by year."""
    data = {}
    for name, ndays in MONTHS:
        path = os.path.join(SRC_DIR, "month-%02d.json" % MONTH_NUM[name])
        if not os.path.isfile(path):
            raise SystemExit(f"Missing data file: {path}")
        with open(path, encoding="utf-8") as fh:
            month = json.load(fh)
        days = month["days"]
        for d in range(1, ndays + 1):
            evs = list(days.get(str(d), []))
            evs.sort(key=lambda e: e["year"])
            data[(name, d)] = evs
    return data


EVENTS = load_events()


# ---------------------------------------------------------------------------
# Category presentation
# ---------------------------------------------------------------------------
TYPE_META = {
    "birth":        ("fa-cake-candles",   "golf-gold",  "Born"),
    "championship": ("fa-trophy",         "golf-green", "Championship"),
    "record":       ("fa-medal",          "golf-green", "Record"),
    "death":        ("fa-ribbon",         "golf-muted", "In Memoriam"),
    "milestone":    ("fa-flag-checkered", "golf-green", "Milestone"),
}
DEFAULT_META = ("fa-golf-ball-tee", "golf-green", "Moment")


# ---------------------------------------------------------------------------
# HTML building blocks
# ---------------------------------------------------------------------------
def head_common(title, description, canonical, ld_blocks, prefix):
    ld = "\n".join(
        f'<script type="application/ld+json">{b}</script>' for b in ld_blocks
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:site_name" content="BirdieStats.com">
<meta name="twitter:card" content="summary_large_image">

<link rel="apple-touch-icon" sizes="180x180" href="{prefix}apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="{prefix}favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{prefix}favicon-16x16.png">
<link rel="manifest" href="{prefix}site.webmanifest">
<meta name="theme-color" content="#1B5E20">
{ld}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config={{theme:{{extend:{{colors:{{'golf-green':'#1B5E20','golf-green-md':'#2E7D32','golf-green-lt':'#E8F5E9','golf-accent':'#4CAF50','golf-bg':'#FAFAFA','golf-card':'#FFFFFF','golf-border':'#E0E0E0','golf-dark':'#1A1A2E','golf-text':'#424242','golf-muted':'#757575','golf-gold':'#FFB300'}},fontFamily:{{'display':['Playfair Display','Georgia','serif'],'body':['Inter','system-ui','sans-serif']}}}}}}}}
</script>
<style>
body {{ font-family: 'Inter', system-ui, sans-serif; background: #FAFAFA; color: #424242; }}
h1, h2, h3, h4, h5 {{ font-family: 'Playfair Display', Georgia, serif; color: #1A1A2E; }}
a {{ color: #1B5E20; }}
a:hover {{ color: #2E7D32; }}
.table-striped tr:nth-child(even) {{ background-color: #F5F5F5; }}
.table-striped tr:hover {{ background-color: #E8F5E9; }}
</style>
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{GA_ID}");</script>
</head><body>
"""


NAV_LINKS = [
    ("majors/index.html", "Majors"),
    ("players/index.html", "Players"),
    ("courses/index.html", "Courses"),
    ("head-to-head/index.html", "Head-to-Head"),
    ("pga-tour/index.html", "PGA Tour"),
    ("records/index.html", "Records"),
    ("this-day-in-golf/index.html", "This Day"),
    ("about/index.html", "About"),
]


def nav_html(prefix):
    desk = "\n".join(
        f'        <a href="{prefix}{href}" class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">{label}</a>'
        for href, label in NAV_LINKS
    )
    mob = "\n".join(
        f'      <a href="{prefix}{href}" class="block py-2 text-golf-text hover:text-golf-green no-underline">{label}</a>'
        for href, label in NAV_LINKS
    )
    return f"""<nav class="bg-white border-b border-golf-border sticky top-0 z-50 shadow-sm">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <a href="{prefix}index.html" class="flex items-center gap-2 no-underline">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" class="w-8 h-8">
  <circle cx="20" cy="32" r="6" fill="#4CAF50" opacity="0.3"/>
  <line x1="20" y1="4" x2="20" y2="30" stroke="#1B5E20" stroke-width="2.5" stroke-linecap="round"/>
  <polygon points="20,4 34,12 20,16" fill="#1B5E20"/>
</svg>
        <span class="font-display text-xl font-bold text-golf-green">BirdieStats</span>
      </a>
      <button onclick="document.getElementById('mobile-menu').classList.toggle('hidden')" class="md:hidden p-2 text-golf-text hover:text-golf-green">
        <i class="fas fa-bars text-xl"></i>
      </button>
      <div class="hidden md:flex items-center gap-6">
{desk}
      </div>
    </div>
  </div>
  <div id="mobile-menu" class="hidden md:hidden border-t border-golf-border bg-white">
    <div class="px-4 py-3 space-y-2">
{mob}
    </div>
  </div>
</nav>
"""


def footer_html(prefix):
    return f"""<footer class="bg-golf-green text-white mt-16">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div>
        <div class="flex items-center gap-2 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" class="w-8 h-8">
            <circle cx="20" cy="32" r="6" fill="white" opacity="0.3"/>
            <line x1="20" y1="4" x2="20" y2="30" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
            <polygon points="20,4 34,12 20,16" fill="white"/>
          </svg>
          <span class="font-display text-xl font-bold">BirdieStats</span>
        </div>
        <p class="text-green-200 text-sm leading-relaxed">The most comprehensive collection of golf championship history, statistics, and records.</p>
      </div>
      <div>
        <h4 class="font-display text-lg font-semibold mb-4 text-white">Explore</h4>
        <div class="space-y-2">
          <a href="{prefix}majors/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Major Championships</a>
          <a href="{prefix}players/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Players</a>
          <a href="{prefix}courses/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Courses</a>
          <a href="{prefix}head-to-head/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Head-to-Head</a>
          <a href="{prefix}records/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Records</a>
          <a href="{prefix}this-day-in-golf/index.html" class="block text-green-200 hover:text-white no-underline text-sm">This Day in Golf</a>
        </div>
      </div>
      <div>
        <h4 class="font-display text-lg font-semibold mb-4 text-white">Info</h4>
        <div class="space-y-2">
          <a href="{prefix}about/index.html" class="block text-green-200 hover:text-white no-underline text-sm">About</a>
          <a href="{prefix}privacy/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Privacy Policy</a>
          <a href="mailto:info@birdiestats.com" class="block text-green-200 hover:text-white no-underline text-sm">Contact</a>
        </div>
      </div>
    </div>
    <div class="border-t border-green-800 mt-8 pt-8 text-center">
      <p class="text-green-300 text-xs leading-relaxed">Data compiled from public historical records. Not affiliated with the PGA Tour, USGA, R&amp;A, or Augusta National.</p>
      <p class="text-green-300 text-xs mt-2">&copy; 2025 BirdieStats.com. All rights reserved.</p>
    </div>
  </div>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Event card rendering
# ---------------------------------------------------------------------------
def player_chip(slug, prefix):
    if not slug or not player_exists(slug):
        return ""
    name = esc(player_display_name(slug))
    return (f'\n        <a href="{prefix}players/{slug}/index.html" '
            f'class="inline-flex items-center gap-1.5 mt-3 text-sm text-golf-green hover:text-golf-green-md no-underline font-medium">'
            f'<i class="fas fa-circle-user"></i> {name} '
            f'<i class="fas fa-arrow-right text-xs"></i></a>')


def event_card(ev, prefix, timeline=True):
    icon, color, badge = TYPE_META.get(ev["category"], DEFAULT_META)
    title = esc(ev["title"])
    text = esc(ev["text"])
    chip = player_chip(ev.get("player_slug"), prefix)
    inner = f"""      <div class="bg-white rounded-xl shadow-sm border border-golf-border p-5">
        <div class="flex items-center gap-3 mb-2">
          <span class="font-display text-2xl font-bold text-golf-green">{ev['year']}</span>
          <span class="text-xs font-semibold uppercase tracking-wide text-{color} bg-golf-green-lt px-2 py-0.5 rounded">{badge}</span>
        </div>
        <h3 class="font-display text-lg font-bold text-golf-dark mb-1">{title}</h3>
        <p class="text-golf-text leading-relaxed">{text}</p>{chip}
      </div>"""
    if not timeline:
        return inner + "\n"
    return f"""    <div class="relative pl-8 pb-6 border-l-2 border-golf-green-lt last:border-l-transparent">
      <div class="absolute -left-[11px] top-0 w-5 h-5 rounded-full bg-golf-green flex items-center justify-center">
        <i class="fas {icon} text-white" style="font-size:10px"></i>
      </div>
{inner}
    </div>
"""


# ---------------------------------------------------------------------------
# Day page rendering
# ---------------------------------------------------------------------------
def day_meta_description(label, events):
    births = sum(1 for e in events if e["category"] == "birth")
    years = [e["year"] for e in events]
    span = f"{min(years)}" if min(years) == max(years) else f"{min(years)}–{max(years)}"
    desc = (f"On {label} in golf history: {len(events)} notable "
            f"{'event' if len(events) == 1 else 'events'}"
            + (f", including {births} golfer {'birthday' if births == 1 else 'birthdays'}" if births else "")
            + f", spanning {span}.")
    if len(desc) > 155:
        desc = (f"On {label} in golf history: {len(events)} notable golf moments "
                f"spanning {span}.")
    return desc[:155]


def render_day_page(month, day):
    prefix = "../../"
    slug = slug_for(month, day)
    mtitle = MONTH_TITLE[month]
    label = f"{mtitle} {day}"
    url = f"{SITE}/this-day-in-golf/{slug}/"
    events = EVENTS[(month, day)]

    # prev / next
    idx = ALL_DAYS.index((month, day))
    pm, pd = ALL_DAYS[(idx - 1) % len(ALL_DAYS)]
    nm, nd = ALL_DAYS[(idx + 1) % len(ALL_DAYS)]
    prev_slug, next_slug = slug_for(pm, pd), slug_for(nm, nd)
    prev_label = f"{MONTH_TITLE[pm]} {pd}"
    next_label = f"{MONTH_TITLE[nm]} {nd}"

    desc = day_meta_description(label, events)
    meta_desc = esc(desc)
    page_title = f"{label} in Golf History | BirdieStats.com"

    ld_article = (
        '{"@context":"https://schema.org","@type":"Article",'
        f'"headline":"{label} in Golf History",'
        f'"description":"{meta_desc}",'
        f'"url":"{url}",'
        f'"datePublished":"{BUILD_DATE}","dateModified":"{BUILD_DATE}",'
        '"author":{"@type":"Organization","name":"BirdieStats.com","url":"https://birdiestats.com"},'
        '"publisher":{"@type":"Organization","name":"BirdieStats.com",'
        '"logo":{"@type":"ImageObject","url":"https://birdiestats.com/android-chrome-512x512.png","width":512,"height":512}}}'
    )
    ld_crumb = (
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Home","item":"https://birdiestats.com/"},'
        '{"@type":"ListItem","position":2,"name":"On This Day","item":"https://birdiestats.com/this-day-in-golf/"},'
        f'{{"@type":"ListItem","position":3,"name":"{label}","item":"{url}"}}]}}'
    )

    html_out = head_common(esc(page_title), meta_desc, url, [ld_article, ld_crumb], prefix)
    html_out += nav_html(prefix)

    html_out += f"""<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <nav class="text-sm py-4" aria-label="Breadcrumb"><a href="{prefix}index.html" class="text-golf-green hover:text-golf-green-md no-underline">Home</a> <span class="text-golf-muted mx-1">/</span> <a href="../index.html" class="text-golf-green hover:text-golf-green-md no-underline">This Day in Golf</a> <span class="text-golf-muted mx-1">/</span> <span class="text-golf-muted">{label}</span></nav>
</div>
"""

    html_out += f"""<section class="bg-gradient-to-r from-golf-green to-golf-green-md text-white py-12 md:py-16">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center gap-4 mb-4">
      <div class="w-16 h-16 bg-white/15 rounded-2xl flex flex-col items-center justify-center flex-shrink-0">
        <span class="text-xs uppercase tracking-wider text-green-100">{MONTH_ABBR[month]}</span>
        <span class="text-3xl font-display font-bold leading-none text-white">{day}</span>
      </div>
      <div>
        <h1 class="font-display text-3xl md:text-5xl font-bold text-white">{label} in Golf History</h1>
        <p class="text-green-100 text-base md:text-lg mt-2 max-w-2xl">{esc(desc)}</p>
      </div>
    </div>
  </div>
</section>
"""

    html_out += f"""<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
  <div class="flex items-center justify-between gap-3 mb-8">
    <a href="../{prev_slug}/index.html" class="bg-white border border-golf-border rounded-lg px-4 py-2 text-sm text-golf-text hover:text-golf-green hover:border-golf-accent transition no-underline"><i class="fas fa-chevron-left mr-1"></i> {prev_label}</a>
    <a href="../index.html" class="text-golf-muted text-sm hover:text-golf-green no-underline"><i class="fas fa-calendar-day mr-1"></i> All days</a>
    <a href="../{next_slug}/index.html" class="bg-white border border-golf-border rounded-lg px-4 py-2 text-sm text-golf-text hover:text-golf-green hover:border-golf-accent transition no-underline">{next_label} <i class="fas fa-chevron-right ml-1"></i></a>
  </div>
"""

    rows = "".join(event_card(ev, prefix) for ev in events)
    html_out += f"""  <h2 class="font-display text-2xl font-bold text-golf-dark mb-6 flex items-center gap-3">
    <i class="fas fa-calendar-check text-golf-green"></i> On This Day in Golf
  </h2>
  <div class="max-w-3xl mb-12">
{rows}  </div>
</section>
"""

    html_out += footer_html(prefix)
    return html_out


# ---------------------------------------------------------------------------
# Landing page rendering
# ---------------------------------------------------------------------------
def render_landing():
    prefix = "../"
    url = f"{SITE}/this-day-in-golf/"
    title = "This Day in Golf History — On This Day | BirdieStats.com"
    desc = ("Discover what happened on this day in golf history: major championship moments, "
            "record rounds, and the birthdays of the game's greatest players, every day of the year.")

    ld_web = (
        '{"@context":"https://schema.org","@type":"WebPage",'
        '"name":"This Day in Golf History",'
        f'"description":"{esc(desc)}",'
        f'"url":"{url}",'
        '"publisher":{"@type":"Organization","name":"BirdieStats.com","url":"https://birdiestats.com"}}'
    )
    ld_crumb = (
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Home","item":"https://birdiestats.com/"},'
        '{"@type":"ListItem","position":2,"name":"On This Day","item":"https://birdiestats.com/this-day-in-golf/"}]}'
    )

    html_out = head_common(esc(title), esc(desc), url, [ld_web, ld_crumb], prefix)
    html_out += nav_html(prefix)

    html_out += f"""<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <nav class="text-sm py-4" aria-label="Breadcrumb"><a href="{prefix}index.html" class="text-golf-green hover:text-golf-green-md no-underline">Home</a> <span class="text-golf-muted mx-1">/</span> <span class="text-golf-muted">This Day in Golf</span></nav>
</div>
"""

    html_out += """<section class="bg-gradient-to-br from-golf-green via-golf-green-md to-golf-accent text-white py-16 md:py-20">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
    <h1 class="font-display text-4xl md:text-5xl font-bold text-white mb-4">This Day in Golf History</h1>
    <p class="text-green-100 text-lg md:text-xl max-w-2xl mx-auto mb-8">Major championship moments, record rounds, and the birthdays of golf's greatest players &mdash; for every day of the year.</p>
    <a id="today-link" href="#" class="inline-block bg-white text-golf-green px-8 py-3 rounded-lg font-semibold hover:bg-green-50 transition no-underline shadow-lg"><i class="fas fa-calendar-day mr-2"></i>Go to Today</a>
  </div>
</section>
"""

    # Featured: build-date events (June 26)
    feat_label = f"{MONTH_TITLE[FEATURE_MONTH]} {FEATURE_DAY}"
    feat_events = EVENTS[(FEATURE_MONTH, FEATURE_DAY)][:6]
    feat = ""
    for ev in feat_events:
        icon, color, badge = TYPE_META.get(ev["category"], DEFAULT_META)
        chip = player_chip(ev.get("player_slug"), prefix)
        feat += f"""    <div class="bg-white rounded-xl shadow-sm border border-golf-border p-5">
      <div class="flex items-center gap-3 mb-2">
        <span class="font-display text-xl font-bold text-golf-green">{ev['year']}</span>
        <span class="text-xs font-semibold uppercase tracking-wide text-{color} bg-golf-green-lt px-2 py-0.5 rounded">{badge}</span>
      </div>
      <h3 class="font-display text-base font-bold text-golf-dark mb-1">{esc(ev['title'])}</h3>
      <p class="text-golf-text text-sm leading-relaxed">{esc(ev['text'])}</p>{chip}
    </div>
"""
    html_out += f"""<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
  <div class="flex items-center justify-between flex-wrap gap-3 mb-2">
    <h2 class="font-display text-2xl font-bold text-golf-dark flex items-center gap-3"><i class="fas fa-star text-golf-gold"></i> Featured: {feat_label}</h2>
    <a href="{FEATURE_MONTH}-{FEATURE_DAY}/index.html" class="text-sm font-medium text-golf-green hover:text-golf-green-md no-underline">View full day <i class="fas fa-arrow-right text-xs ml-1"></i></a>
  </div>
  <p class="text-golf-muted text-sm mb-6">A glimpse of golf history on {feat_label}. Use &ldquo;Go to Today&rdquo; above to jump straight to the current date.</p>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
{feat}  </div>
</section>
"""

    # Month / calendar grid
    grid = ""
    for (mname, ndays) in MONTHS:
        mt = MONTH_TITLE[mname]
        days_links = ""
        for d in range(1, ndays + 1):
            days_links += (f'<a href="{mname}-{d}/index.html" '
                           f'class="inline-flex items-center justify-center w-9 h-9 rounded-md text-sm text-golf-text hover:bg-golf-green hover:text-white no-underline transition">{d}</a>')
        grid += f"""    <div class="bg-white rounded-xl shadow-sm border border-golf-border p-5">
      <h3 class="font-display text-lg font-bold text-golf-dark mb-3">{mt}</h3>
      <div class="flex flex-wrap gap-1">{days_links}</div>
    </div>
"""
    html_out += f"""<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
  <h2 class="font-display text-2xl font-bold text-golf-dark mb-2 flex items-center gap-3"><i class="fas fa-calendar text-golf-green"></i> Browse Every Day</h2>
  <p class="text-golf-muted text-sm mb-6">Pick any date to see the major moments, records and birthdays in golf history.</p>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
{grid}  </div>
</section>
"""

    html_out += """<script>
(function(){
  var months=["january","february","march","april","may","june","july","august","september","october","november","december"];
  var now=new Date();
  var slug=months[now.getMonth()]+"-"+now.getDate();
  var el=document.getElementById("today-link");
  if(el){el.href=slug+"/index.html";el.innerHTML='<i class="fas fa-calendar-day mr-2"></i>Go to Today ('+slug.replace("-"," ").replace(/^./,function(c){return c.toUpperCase();})+')';}
})();
</script>
"""

    html_out += footer_html(prefix)
    return html_out


# ---------------------------------------------------------------------------
# Nav injection into existing pages (idempotent)
# ---------------------------------------------------------------------------
def inject_nav():
    count = 0
    skip_dirs = {".git", "this-day-in-golf"}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            if "this-day-in-golf/index.html" in content:
                continue  # already injected
            new = content

            desk_re = re.compile(
                r'(<a href="((?:\.\./)*)about/index\.html" class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">About</a>)'
            )

            def desk_sub(m):
                pre = m.group(2)
                link = (f'<a href="{pre}this-day-in-golf/index.html" '
                        f'class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">This Day</a>\n        ')
                return link + m.group(1)
            new = desk_re.sub(desk_sub, new, count=1)

            mob_re = re.compile(
                r'(<a href="((?:\.\./)*)about/index\.html" class="block py-2 text-golf-text hover:text-golf-green no-underline">About</a>)'
            )

            def mob_sub(m):
                pre = m.group(2)
                link = (f'<a href="{pre}this-day-in-golf/index.html" '
                        f'class="block py-2 text-golf-text hover:text-golf-green no-underline">This Day</a>\n      ')
                return link + m.group(1)
            new = mob_re.sub(mob_sub, new, count=1)

            if new != content:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                count += 1
    return count


# ---------------------------------------------------------------------------
# Sitemap update (idempotent)
# ---------------------------------------------------------------------------
def update_sitemap():
    path = os.path.join(ROOT, "sitemap.xml")
    with open(path, encoding="utf-8") as fh:
        xml = fh.read()
    if "/this-day-in-golf/" in xml:
        return 0  # already present

    def entry(loc, pr, freq="monthly"):
        return (f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{BUILD_DATE}</lastmod>\n"
                f"    <changefreq>{freq}</changefreq>\n    <priority>{pr}</priority>\n  </url>")

    entries = [entry(f"{SITE}/this-day-in-golf/", "0.8", "daily")]
    for (mname, ndays) in MONTHS:
        for d in range(1, ndays + 1):
            entries.append(entry(f"{SITE}/this-day-in-golf/{mname}-{d}/", "0.6"))

    block = "\n".join(entries) + "\n"
    xml = xml.replace("</urlset>", block + "</urlset>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(xml)
    return len(entries)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    os.makedirs(SECTION_DIR, exist_ok=True)

    with open(os.path.join(SECTION_DIR, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(render_landing())

    n = 0
    for (mname, ndays) in MONTHS:
        for d in range(1, ndays + 1):
            day_dir = os.path.join(SECTION_DIR, slug_for(mname, d))
            os.makedirs(day_dir, exist_ok=True)
            with open(os.path.join(day_dir, "index.html"), "w", encoding="utf-8") as fh:
                fh.write(render_day_page(mname, d))
            n += 1
    print(f"Generated landing + {n} day pages")

    injected = inject_nav()
    print(f"Injected This Day nav into {injected} existing pages")

    added = update_sitemap()
    print(f"Added {added} sitemap entries")


if __name__ == "__main__":
    main()
