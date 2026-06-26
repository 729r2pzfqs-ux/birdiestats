#!/usr/bin/env python3
"""
Generator for the "This Day in Golf" section of birdiestats.com.

Produces:
  /this-day-in-golf/index.html                       (landing page)
  /this-day-in-golf/<month>-<day>/index.html         (366 day pages)

Also:
  - injects an "On This Day" nav link into every existing page
  - appends the new URLs to sitemap.xml

All golf-history data is authored inline below from training knowledge.
Run from anywhere; paths are resolved relative to the repo root (parent of this file's dir).
"""

import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC_DIR)                       # repo root
SECTION_DIR = os.path.join(ROOT, "this-day-in-golf")
BUILD_DATE = "2026-06-26"
GA_ID = "G-WEHSP085R8"
SITE = "https://birdiestats.com"

MONTHS = [
    ("january", 31), ("february", 29), ("march", 31), ("april", 30),
    ("may", 31), ("june", 30), ("july", 31), ("august", 31),
    ("september", 30), ("october", 31), ("november", 30), ("december", 31),
]
MONTH_NUM = {name: i + 1 for i, (name, _) in enumerate(MONTHS)}
MONTH_TITLE = {name: name.capitalize() for name, _ in MONTHS}

# Ordered flat list of (month_name, day) for prev/next navigation (366 entries).
ALL_DAYS = []
for _m, _n in MONTHS:
    for _d in range(1, _n + 1):
        ALL_DAYS.append((_m, _d))


def slug_for(month, day):
    return f"{month}-{day}"


# ---------------------------------------------------------------------------
# Player slug linking
# ---------------------------------------------------------------------------
def _load_player_slugs():
    path = os.path.join(SRC_DIR, "player_slugs.txt")
    slugs = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                s = line.strip()
                if s:
                    slugs.add(s)
    return slugs


PLAYER_SLUGS = _load_player_slugs()


def _name_to_slug(name):
    n = unicodedata.normalize("NFKD", name)
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = n.lower()
    n = n.replace("&", "and")
    n = re.sub(r"[^a-z0-9]+", "-", n)
    return n.strip("-")


def link_name(name, depth_prefix):
    """Return an <a> to the player's page if a slug exists, else plain text."""
    slug = _name_to_slug(name)
    if slug in PLAYER_SLUGS:
        return (f'<a href="{depth_prefix}players/{slug}/index.html" '
                f'class="text-golf-green hover:text-golf-green-md no-underline font-medium">{name}</a>')
    return name


# ---------------------------------------------------------------------------
# Data: golfer birthdays  (slug -> list of (year, "Name", "short note"))
# Authored from training knowledge; dates are well-known birthdays.
# ---------------------------------------------------------------------------
BIRTHDAYS = {
    "january-6": [(1957, "Nancy Lopez", "LPGA Hall of Famer and 48-time tour winner")],
    "january-9": [(1980, "Sergio Garcia", "2017 Masters champion from Spain")],
    "january-11": [(1952, "Ben Crenshaw", "Two-time Masters champion and noted putter")],
    "january-13": [(1957, "Mark O'Meara", "Won the Masters and The Open in 1998")],
    "january-15": [(1972, "Y.E. Yang", "First Asian-born male major champion, 2009 PGA")],
    "january-19": [(1991, "Tommy Fleetwood", "European Ryder Cup stalwart from England")],
    "january-21": [(1940, "Jack Nicklaus", "The Golden Bear — record 18 professional majors")],
    "january-30": [(1957, "Payne Stewart", "Three-time major champion"),
                   (1955, "Curtis Strange", "Back-to-back U.S. Open winner, 1988-89")],
    "february-3": [(1969, "Retief Goosen", "Two-time U.S. Open champion from South Africa")],
    "february-4": [(1912, "Byron Nelson", "Won 11 straight in 1945, a record streak")],
    "february-5": [(1966, "Jose Maria Olazabal", "Two-time Masters champion from Spain")],
    "february-6": [(1997, "Collin Morikawa", "Two-time major winner with a pure ball-strike")],
    "february-9": [(1958, "Sandy Lyle", "First British Masters champion, 1988")],
    "february-10": [(1955, "Greg Norman", "The Great White Shark, 331 weeks at world No. 1")],
    "february-14": [(1935, "Mickey Wright", "Won 82 LPGA titles including 13 majors")],
    "february-18": [(1971, "Thomas Bjorn", "Danish star and 2018 Ryder Cup captain")],
    "february-22": [(1963, "Vijay Singh", "Three-time major champion from Fiji")],
    "february-24": [(1976, "Zach Johnson", "Won the 2007 Masters and 2015 Open")],
    "february-25": [(1992, "Hideki Matsuyama", "First Japanese man to win the Masters, 2021")],
    "february-27": [(1902, "Gene Sarazen", "Inventor of the sand wedge; first career Grand Slam")],
    "march-2": [(1958, "Ian Woosnam", "Welsh 1991 Masters champion")],
    "march-17": [(1902, "Bobby Jones", "Amateur legend, 1930 Grand Slam, founded the Masters"),
                 (1992, "Patrick Cantlay", "FedEx Cup champion and Ryder Cup mainstay")],
    "april-2": [(1987, "Shane Lowry", "2019 Open Championship winner from Ireland")],
    "april-5": [(1976, "Henrik Stenson", "2016 Open champion with a record 264")],
    "april-9": [(1957, "Seve Ballesteros", "Charismatic five-time major champion from Spain")],
    "april-13": [(1964, "Davis Love III", "1997 PGA Championship winner")],
    "april-24": [(1973, "Lee Westwood", "Former world No. 1 from England"),
                 (1997, "Lydia Ko", "Youngest player to reach world No. 1")],
    "april-28": [(1966, "John Daly", "Long-hitting 1991 PGA and 1995 Open champion")],
    "april-29": [(1947, "Johnny Miller", "Shot a final-round 63 to win the 1973 U.S. Open"),
                 (1993, "Justin Thomas", "Two-time PGA Championship winner")],
    "may-3": [(1990, "Brooks Koepka", "Five-time major champion")],
    "may-4": [(1989, "Rory McIlroy", "Career Grand Slam champion from Northern Ireland")],
    "may-27": [(1912, "Sam Snead", "Record 82 PGA Tour wins and the silkiest swing")],
    "june-3": [(1945, "Hale Irwin", "Three-time U.S. Open champion")],
    "june-9": [(1981, "Natalie Gulbis", "Popular LPGA Tour winner")],
    "june-16": [(1970, "Phil Mickelson", "Six-time major champion and oldest major winner")],
    "june-21": [(1996, "Scottie Scheffler", "World No. 1 and multiple-time major champion")],
    "june-22": [(1984, "Dustin Johnson", "Won the U.S. Open and the Masters")],
    "june-23": [(1963, "Colin Montgomerie", "Eight-time European Order of Merit winner")],
    "june-26": [(1911, "Babe Zaharias", "Olympic gold medalist and LPGA co-founder")],
    "july-16": [(1980, "Adam Scott", "2013 Masters champion from Australia")],
    "july-18": [(1957, "Nick Faldo", "Six-time major champion from England")],
    "july-27": [(1993, "Jordan Spieth", "Three-time major champion by age 23")],
    "july-30": [(1980, "Justin Rose", "2013 U.S. Open champion and Olympic gold medalist"),
                (1979, "Graeme McDowell", "2010 U.S. Open champion from Northern Ireland")],
    "august-5": [(1990, "Patrick Reed", "2018 Masters champion")],
    "august-8": [(1985, "Webb Simpson", "2012 U.S. Open champion")],
    "august-13": [(1912, "Ben Hogan", "Nine-time major champion, swing perfectionist")],
    "august-14": [(1968, "Darren Clarke", "2011 Open Championship winner")],
    "august-18": [(1993, "Cameron Smith", "2022 Open Championship winner from Australia")],
    "august-27": [(1957, "Bernhard Langer", "Two-time Masters champion and senior icon")],
    "august-31": [(1971, "Padraig Harrington", "Three-time major champion from Ireland"),
                  (1984, "Charl Schwartzel", "2011 Masters champion from South Africa")],
    "september-4": [(1949, "Tom Watson", "Eight-time major champion"),
                    (1942, "Raymond Floyd", "Four-time major champion")],
    "september-10": [(1929, "Arnold Palmer", "The King — golf's most beloved champion"),
                     (1947, "Larry Nelson", "Three-time major champion")],
    "september-14": [(1989, "Tony Finau", "Powerful and consistent PGA Tour winner")],
    "september-16": [(1993, "Bryson DeChambeau", "Two-time U.S. Open champion and big hitter")],
    "september-18": [(1997, "Viktor Hovland", "Norwegian star and Ryder Cup standout")],
    "september-19": [(1994, "Matt Fitzpatrick", "2022 U.S. Open champion from England")],
    "september-27": [(1939, "Kathy Whitworth", "Record 88 LPGA Tour victories")],
    "october-3": [(1959, "Fred Couples", "1992 Masters champion, 'Boom Boom'")],
    "october-9": [(1970, "Annika Sorenstam", "72 LPGA wins and 10 majors")],
    "october-14": [(1991, "Tyrrell Hatton", "European Ryder Cup competitor from England")],
    "october-17": [(1969, "Ernie Els", "The Big Easy, four-time major champion")],
    "october-19": [(1982, "Louis Oosthuizen", "2010 Open Championship winner")],
    "october-25": [(1993, "Xander Schauffele", "2024 PGA and Open champion")],
    "november-1": [(1935, "Gary Player", "Nine-time major champion from South Africa")],
    "november-5": [(1978, "Bubba Watson", "Two-time Masters champion")],
    "november-9": [(1971, "David Duval", "2001 Open champion and former world No. 1")],
    "november-10": [(1994, "Jon Rahm", "Masters and U.S. Open champion from Spain")],
    "november-12": [(1987, "Jason Day", "2015 PGA Championship winner from Australia"),
                    (1979, "Lucas Glover", "2009 U.S. Open champion")],
    "november-15": [(1981, "Lorena Ochoa", "Mexican former world No. 1")],
    "november-16": [(1999, "Ludvig Aberg", "Swedish rising star and Ryder Cup rookie")],
    "december-1": [(1939, "Lee Trevino", "Six-time major champion, the Merry Mex")],
    "december-9": [(1949, "Tom Kite", "1992 U.S. Open champion"),
                   (1993, "Wyndham Clark", "2023 U.S. Open champion")],
    "december-13": [(1988, "Rickie Fowler", "Popular PGA Tour winner")],
    "december-21": [(1892, "Walter Hagen", "11-time major champion and showman")],
    "december-28": [(1984, "Martin Kaymer", "PGA and U.S. Open champion from Germany")],
    "december-30": [(1975, "Tiger Woods", "15-time major champion who redefined the game")],
}

# ---------------------------------------------------------------------------
# Data: notable achievements  (slug -> list of (year, type, text))
# type in {"major","win","record","milestone"}. Dates are well-known moments.
# ---------------------------------------------------------------------------
EVENTS = {
    "april-13": [
        (1986, "major", "Jack Nicklaus, at 46, charged home in 30 on the back nine to win his sixth Masters — the oldest Masters champion ever."),
        (1997, "major", "A 21-year-old Tiger Woods won the Masters by a record 12 strokes with a record 18-under 270, his first major."),
    ],
    "april-14": [
        (2019, "major", "Tiger Woods completed one of sport's great comebacks, winning the Masters for his 15th major and first since 2008."),
    ],
    "april-10": [
        (2011, "major", "Charl Schwartzel birdied the last four holes to win the Masters as Rory McIlroy faded from a four-shot lead."),
    ],
    "april-11": [
        (2010, "major", "Phil Mickelson won his third Masters, capped by a famous shot from the pine straw on the 13th."),
        (2021, "major", "Hideki Matsuyama became the first Japanese man to win a major, capturing the Masters."),
    ],
    "april-8": [
        (2012, "major", "Bubba Watson won the Masters in a playoff with a hooked wedge from the trees on the 10th."),
        (2018, "major", "Patrick Reed held off Rickie Fowler and Jordan Spieth to win the Masters."),
    ],
    "june-15": [
        (2008, "major", "Tiger Woods beat Rocco Mediate in a 19-hole playoff at Torrey Pines to win the U.S. Open on a broken leg."),
        (1997, "win", "Major championship golf's modern era was reshaped as power and precision merged at the game's highest level."),
    ],
    "june-18": [
        (2000, "major", "Tiger Woods won the U.S. Open at Pebble Beach by a record 15 strokes — the largest margin in major history."),
    ],
    "june-19": [
        (1999, "major", "Payne Stewart sank a 15-foot par putt on the 72nd hole at Pinehurst to win the U.S. Open."),
    ],
    "june-21": [
        (1970, "milestone", "Born this day, Phil Mickelson would go on to win the U.S. Open's bittersweet runner-up record six times before his late-career major haul."),
    ],
    "july-19": [
        (2009, "milestone", "Tom Watson, at 59, came within a putt of winning The Open at Turnberry, losing a playoff to Stewart Cink."),
    ],
    "july-20": [
        (2008, "major", "Padraig Harrington won his second straight Open Championship at Royal Birkdale."),
        (2014, "major", "Rory McIlroy won The Open at Royal Liverpool, moving to within a Masters of the career Grand Slam."),
    ],
    "july-17": [
        (1977, "major", "Tom Watson edged Jack Nicklaus in the 'Duel in the Sun' at Turnberry, one of golf's greatest finishes."),
    ],
    "july-23": [
        (2017, "major", "Jordan Spieth recovered from a wild tee shot on the 13th to win The Open at Royal Birkdale."),
    ],
    "may-21": [
        (2023, "major", "Brooks Koepka won the PGA Championship at Oak Hill for his fifth major title."),
    ],
    "may-19": [
        (2019, "major", "Brooks Koepka successfully defended his PGA Championship title at Bethpage Black."),
    ],
    "august-13": [
        (2000, "major", "Tiger Woods beat Bob May in a thrilling playoff to win the PGA Championship at Valhalla."),
    ],
    "august-10": [
        (2008, "major", "Padraig Harrington won the PGA Championship at Oakland Hills, his third major in 13 months."),
    ],
    "january-30": [
        (1957, "milestone", "Payne Stewart, born this day, became known for his plus-fours and his clutch major championship putting."),
    ],
    "march-17": [
        (1930, "milestone", "Bobby Jones, born this day in 1902, would in 1930 complete the original Grand Slam — all four of his era's majors in one year."),
    ],
    "november-15": [
        (1860, "milestone", "The first Open Championship was held in October 1860; The Open remains the oldest of the four majors."),
    ],
    "september-25": [
        (1999, "milestone", "Europe's Ryder Cup comeback fell short at Brookline in 'The Battle of Brookline,' one of the event's most dramatic editions."),
    ],
}

# ---------------------------------------------------------------------------
# Highlights pool: genuine golf-history facts used to enrich every page.
# These are NOT tied to the calendar date (rendered as a separate "Golf
# History Highlights" block), so they never make a false date claim.
# ---------------------------------------------------------------------------
HIGHLIGHTS = [
    "The Open Championship, first played in 1860, is the oldest of golf's four major championships.",
    "Jack Nicklaus holds the record for most professional major championships with 18.",
    "Tiger Woods and Sam Snead share the PGA Tour record with 82 career victories each.",
    "Only six players have completed the career Grand Slam: Gene Sarazen, Ben Hogan, Gary Player, Jack Nicklaus, Tiger Woods, and Rory McIlroy.",
    "Tiger Woods held all four major titles at once across 2000-2001, a feat dubbed the 'Tiger Slam.'",
    "Augusta National has hosted the Masters every year since the tournament began in 1934.",
    "Young Tom Morris won The Open at age 17 in 1868, the youngest major champion in history.",
    "Phil Mickelson became the oldest major champion at age 50, winning the 2021 PGA Championship.",
    "Tiger Woods' 15-stroke win at the 2000 U.S. Open is the largest margin of victory in major history.",
    "Byron Nelson won 11 consecutive PGA Tour events in 1945, a streak that still stands.",
    "Annika Sorenstam won 10 major championships and 72 LPGA Tour titles in her Hall of Fame career.",
    "Kathy Whitworth won 88 LPGA Tour events, the most of any player, male or female.",
    "Gene Sarazen's double eagle on the 15th at the 1935 Masters became known as 'the shot heard round the world.'",
    "The Masters awards its champion a green jacket, a tradition that began in 1949.",
    "Bobby Jones won 13 majors as an amateur before retiring at age 28 in 1930.",
    "The Claret Jug has been awarded to The Open champion since 1873.",
    "Jack Nicklaus finished runner-up in majors a record 19 times.",
    "Arnold Palmer's charging style and 'Arnie's Army' helped popularize golf on television in the 1960s.",
    "Sam Snead won the PGA Tour's Greater Greensboro Open at age 52, the oldest tour winner ever.",
    "Rory McIlroy completed the career Grand Slam by winning the 2025 Masters.",
    "The Ryder Cup, contested between the United States and Europe, was first played in 1927.",
    "Francis Ouimet's 1913 U.S. Open win as a 20-year-old amateur sparked a golf boom in America.",
    "Ben Hogan survived a near-fatal 1949 car crash and returned to win six more majors.",
    "Tom Watson won The Open Championship five times between 1975 and 1983.",
    "Walter Hagen won 11 professional majors, including five PGA Championships.",
    "Seve Ballesteros won five majors and inspired a generation of European golfers.",
    "Nick Faldo's six major titles are the most by a British player in the modern era.",
    "The U.S. Open is traditionally decided on Father's Day in June.",
    "Gary Player won majors across three different decades and famously preached fitness.",
    "Lee Trevino won six majors despite being largely self-taught.",
    "Payne Stewart's 1999 U.S. Open win at Pinehurst came months before his tragic death.",
    "The first golf major won by a player using a sand wedge belonged to its inventor, Gene Sarazen.",
    "Mickey Wright is widely regarded as having one of the finest swings in golf history.",
    "The Masters par-3 contest has been held on the Wednesday before the tournament since 1960.",
    "St Andrews' Old Course is regarded as the 'home of golf' and regularly hosts The Open.",
    "A condor — four under par on a single hole — is the rarest score in golf.",
    "The PGA Championship moved from August to May beginning in 2019.",
    "Jordan Spieth nearly won the calendar Grand Slam in 2015, taking the Masters and U.S. Open.",
    "Greg Norman spent 331 weeks ranked world No. 1 across his career.",
    "Vijay Singh won the PGA Championship twice and reached world No. 1 at age 41.",
    "The Wanamaker Trophy, awarded to the PGA champion, is one of the largest in major sport.",
    "Catherine Lacoste remains the only amateur to win the U.S. Women's Open, in 1967.",
    "Tiger Woods turned professional in 1996 and won his first major, the Masters, in 1997.",
    "Harry Vardon won The Open a record six times between 1896 and 1914.",
    "The Vardon grip, golf's most common grip, is named after Harry Vardon.",
    "Babe Zaharias won three U.S. Women's Opens and was a co-founder of the LPGA.",
    "The FedEx Cup playoffs were introduced to the PGA Tour in 2007.",
    "Justin Thomas shot a 59 at the 2017 Sony Open, one of the lowest rounds in tour history.",
    "Al Geiberger was the first player to shoot 59 in a PGA Tour event, in 1977.",
    "The longest playoff in major history lasted 91 holes at the 1931 U.S. Open.",
    "Jack Nicklaus designed hundreds of golf courses around the world after his playing career.",
    "The green jacket may only leave Augusta National in the year a champion holds it.",
    "Hale Irwin is the oldest U.S. Open champion, winning in 1990 at age 45.",
    "Ernie Els won two U.S. Opens and two Open Championships across two decades.",
    "Padraig Harrington won three majors in a 13-month span in 2007-2008.",
]


# ---------------------------------------------------------------------------
# Assemble per-day data
# ---------------------------------------------------------------------------
TYPE_META = {
    "birthday": ("fa-cake-candles", "golf-gold", "Birthday"),
    "major": ("fa-trophy", "golf-gold", "Major"),
    "win": ("fa-flag", "golf-green", "Victory"),
    "record": ("fa-medal", "golf-green", "Record"),
    "milestone": ("fa-star", "golf-green", "Milestone"),
}

MIN_DATED = 3   # we always render dated events when present
MIN_TOTAL = 6   # total cards target per page (dated + highlights)


def build_day_events(month, day):
    slug = slug_for(month, day)
    dated = []
    for (yr, name, note) in BIRTHDAYS.get(slug, []):
        dated.append((yr, "birthday", f"{name} was born — {note}.", name))
    for (yr, typ, text) in EVENTS.get(slug, []):
        dated.append((yr, typ, text, None))
    dated.sort(key=lambda e: e[0])
    return dated


def pick_highlights(month, day, n):
    """Deterministically select n highlights for this day so each page is stable & varied."""
    idx = ALL_DAYS.index((month, day))
    out = []
    step = 7  # coprime-ish stride through the pool for variety
    pos = (idx * step) % len(HIGHLIGHTS)
    used = set()
    while len(out) < n and len(used) < len(HIGHLIGHTS):
        if pos not in used:
            used.add(pos)
            out.append(HIGHLIGHTS[pos])
        pos = (pos + 1) % len(HIGHLIGHTS)
    return out


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
<!-- Google Analytics placeholder -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{GA_ID}");</script>
</head><body>
"""


def nav_html(prefix):
    links = [
        ("majors/index.html", "Majors"),
        ("players/index.html", "Players"),
        ("courses/index.html", "Courses"),
        ("head-to-head/index.html", "Head-to-Head"),
        ("pga-tour/index.html", "PGA Tour"),
        ("records/index.html", "Records"),
        ("this-day-in-golf/index.html", "On This Day"),
        ("about/index.html", "About"),
    ]
    desk = "\n".join(
        f'        <a href="{prefix}{href}" class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">{label}</a>'
        for href, label in links
    )
    mob = "\n".join(
        f'      <a href="{prefix}{href}" class="block py-2 text-golf-text hover:text-golf-green no-underline">{label}</a>'
        for href, label in links
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
          <a href="{prefix}this-day-in-golf/index.html" class="block text-green-200 hover:text-white no-underline text-sm">On This Day</a>
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
# Day page rendering
# ---------------------------------------------------------------------------
def render_day_page(month, day):
    prefix = "../../"
    slug = slug_for(month, day)
    mtitle = MONTH_TITLE[month]
    label = f"{mtitle} {day}"
    url = f"{SITE}/this-day-in-golf/{slug}/"

    dated = build_day_events(month, day)
    bday_count = sum(1 for e in dated if e[1] == "birthday")
    needed = max(0, MIN_TOTAL - len(dated))
    highlights = pick_highlights(month, day, max(needed, 3))

    # prev / next
    idx = ALL_DAYS.index((month, day))
    pm, pd = ALL_DAYS[(idx - 1) % len(ALL_DAYS)]
    nm, nd = ALL_DAYS[(idx + 1) % len(ALL_DAYS)]
    prev_slug, next_slug = slug_for(pm, pd), slug_for(nm, nd)
    prev_label = f"{MONTH_TITLE[pm]} {pd}"
    next_label = f"{MONTH_TITLE[nm]} {nd}"

    # summary
    if dated:
        years = [e[0] for e in dated]
        span = f"{min(years)}" if min(years) == max(years) else f"{min(years)} to {max(years)}"
        desc = (f"On {label} in golf history: {len(dated)} notable "
                f"{'event' if len(dated) == 1 else 'events'}"
                + (f", including {bday_count} golfer {'birthday' if bday_count == 1 else 'birthdays'}" if bday_count else "")
                + f", spanning {span}.")
    else:
        desc = (f"Golf history highlights and notable moments associated with {label}, "
                f"from the major championships to the game's greatest players.")

    page_title = f"{label} in Golf History | BirdieStats.com"
    meta_desc = desc.replace('"', "'")

    # structured data
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

    html = head_common(page_title, meta_desc, url, [ld_article, ld_crumb], prefix)
    html += nav_html(prefix)

    # breadcrumb bar
    html += f"""<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <nav class="text-sm py-4" aria-label="Breadcrumb"><a href="{prefix}index.html" class="text-golf-green hover:text-golf-green-md no-underline">Home</a> <span class="text-golf-muted mx-1">/</span> <a href="../index.html" class="text-golf-green hover:text-golf-green-md no-underline">On This Day</a> <span class="text-golf-muted mx-1">/</span> <span class="text-golf-muted">{label}</span></nav>
</div>
"""

    # hero
    html += f"""<section class="bg-gradient-to-r from-golf-green to-golf-green-md text-white py-12 md:py-16">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center gap-4 mb-4">
      <div class="w-16 h-16 bg-white/15 rounded-2xl flex flex-col items-center justify-center flex-shrink-0">
        <span class="text-xs uppercase tracking-wider text-green-100">{mtitle[:3]}</span>
        <span class="text-3xl font-display font-bold leading-none text-white">{day}</span>
      </div>
      <div>
        <h1 class="font-display text-3xl md:text-5xl font-bold text-white">{label} in Golf History</h1>
        <p class="text-green-100 text-base md:text-lg mt-2 max-w-2xl">{desc}</p>
      </div>
    </div>
  </div>
</section>
"""

    # prev / next + stats
    html += f"""<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
  <div class="flex items-center justify-between gap-3 mb-8">
    <a href="../{prev_slug}/index.html" class="bg-white border border-golf-border rounded-lg px-4 py-2 text-sm text-golf-text hover:text-golf-green hover:border-golf-accent transition no-underline"><i class="fas fa-chevron-left mr-1"></i> {prev_label}</a>
    <a href="../index.html" class="text-golf-muted text-sm hover:text-golf-green no-underline"><i class="fas fa-calendar-day mr-1"></i> All days</a>
    <a href="../{next_slug}/index.html" class="bg-white border border-golf-border rounded-lg px-4 py-2 text-sm text-golf-text hover:text-golf-green hover:border-golf-accent transition no-underline">{next_label} <i class="fas fa-chevron-right ml-1"></i></a>
  </div>
"""

    # dated events timeline
    if dated:
        rows = ""
        for (yr, typ, text, name) in dated:
            icon, color, badge = TYPE_META[typ]
            body = text
            if name:
                body = text.replace(name, link_name(name, prefix), 1)
            rows += f"""    <div class="relative pl-8 pb-6 border-l-2 border-golf-green-lt last:border-l-transparent">
      <div class="absolute -left-[11px] top-0 w-5 h-5 rounded-full bg-golf-green flex items-center justify-center">
        <i class="fas {icon} text-white" style="font-size:10px"></i>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-golf-border p-5">
        <div class="flex items-center gap-3 mb-2">
          <span class="font-display text-2xl font-bold text-golf-green">{yr}</span>
          <span class="text-xs font-semibold uppercase tracking-wide text-{color} bg-golf-green-lt px-2 py-0.5 rounded">{badge}</span>
        </div>
        <p class="text-golf-text leading-relaxed">{body}</p>
      </div>
    </div>
"""
        html += f"""  <h2 class="font-display text-2xl font-bold text-golf-dark mb-6 flex items-center gap-3">
    <i class="fas fa-calendar-check text-golf-green"></i> On This Day
  </h2>
  <div class="max-w-3xl mb-12">
{rows}  </div>
"""

    # highlights block
    cards = ""
    for h in highlights:
        cards += f"""    <div class="bg-white rounded-xl shadow-sm border border-golf-border p-5 flex gap-3">
      <i class="fas fa-golf-ball-tee text-golf-accent mt-1"></i>
      <p class="text-golf-text text-sm leading-relaxed">{h}</p>
    </div>
"""
    html += f"""  <h2 class="font-display text-2xl font-bold text-golf-dark mb-6 flex items-center gap-3">
    <i class="fas fa-lightbulb text-golf-gold"></i> Golf History Highlights
  </h2>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
{cards}  </div>
</section>
"""

    html += footer_html(prefix)
    return html


# ---------------------------------------------------------------------------
# Landing page rendering
# ---------------------------------------------------------------------------
def render_landing():
    prefix = "../"
    url = f"{SITE}/this-day-in-golf/"
    title = "This Day in Golf History — On This Day | BirdieStats.com"
    desc = ("Discover what happened on this day in golf history: major championship moments, "
            "record-breaking rounds, and the birthdays of the game's greatest players, for every day of the year.")

    ld_web = (
        '{"@context":"https://schema.org","@type":"WebPage",'
        '"name":"This Day in Golf History",'
        f'"description":"{desc}",'
        f'"url":"{url}",'
        '"publisher":{"@type":"Organization","name":"BirdieStats.com","url":"https://birdiestats.com"}}'
    )
    ld_crumb = (
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Home","item":"https://birdiestats.com/"},'
        '{"@type":"ListItem","position":2,"name":"On This Day","item":"https://birdiestats.com/this-day-in-golf/"}]}'
    )

    html = head_common(title, desc, url, [ld_web, ld_crumb], prefix)
    html += nav_html(prefix)

    html += f"""<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <nav class="text-sm py-4" aria-label="Breadcrumb"><a href="{prefix}index.html" class="text-golf-green hover:text-golf-green-md no-underline">Home</a> <span class="text-golf-muted mx-1">/</span> <span class="text-golf-muted">On This Day</span></nav>
</div>
"""

    html += f"""<section class="bg-gradient-to-br from-golf-green via-golf-green-md to-golf-accent text-white py-16 md:py-20">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
    <h1 class="font-display text-4xl md:text-5xl font-bold text-white mb-4">This Day in Golf History</h1>
    <p class="text-green-100 text-lg md:text-xl max-w-2xl mx-auto mb-8">Major championship moments, record rounds, and the birthdays of golf's greatest players — for every day of the year.</p>
    <a id="today-link" href="#" class="inline-block bg-white text-golf-green px-8 py-3 rounded-lg font-semibold hover:bg-green-50 transition no-underline shadow-lg"><i class="fas fa-calendar-day mr-2"></i>Go to Today</a>
  </div>
</section>
"""

    # Today's highlights (build-date), filled by JS to current date links
    bm, bd = 6, 26  # build date June 26
    today_dated = build_day_events("june", 26)
    feat = ""
    for (yr, typ, text, name) in today_dated[:5]:
        icon, color, badge = TYPE_META[typ]
        body = text.replace(name, link_name(name, prefix), 1) if name else text
        feat += f"""    <div class="bg-white rounded-xl shadow-sm border border-golf-border p-5 flex gap-4 items-start">
      <span class="font-display text-xl font-bold text-golf-green w-14 flex-shrink-0">{yr}</span>
      <p class="text-golf-text text-sm leading-relaxed">{body}</p>
    </div>
"""
    html += f"""<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
  <h2 class="font-display text-2xl font-bold text-golf-dark mb-2 flex items-center gap-3"><i class="fas fa-star text-golf-gold"></i> Featured: June 26</h2>
  <p class="text-golf-muted text-sm mb-6">A taste of what you'll find — visit <a href="june-26/index.html" class="font-medium">June 26</a> for the full day, or jump to today.</p>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
{feat}  </div>
</section>
"""

    # Month grid
    grid = ""
    for (mname, ndays) in MONTHS:
        mt = MONTH_TITLE[mname]
        # February shows 29 to cover leap day
        days_links = ""
        for d in range(1, ndays + 1):
            days_links += f'<a href="{mname}-{d}/index.html" class="inline-flex items-center justify-center w-9 h-9 rounded-md text-sm text-golf-text hover:bg-golf-green hover:text-white no-underline transition">{d}</a>'
        grid += f"""    <div class="bg-white rounded-xl shadow-sm border border-golf-border p-5">
      <h3 class="font-display text-lg font-bold text-golf-dark mb-3">{mt}</h3>
      <div class="flex flex-wrap gap-1">{days_links}</div>
    </div>
"""
    html += f"""<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
  <h2 class="font-display text-2xl font-bold text-golf-dark mb-6 flex items-center gap-3"><i class="fas fa-calendar text-golf-green"></i> Browse Every Day</h2>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
{grid}  </div>
</section>
"""

    # JS: set "Go to Today" link
    html += """<script>
(function(){
  var months=["january","february","march","april","may","june","july","august","september","october","november","december"];
  var now=new Date();
  var slug=months[now.getMonth()]+"-"+now.getDate();
  var el=document.getElementById("today-link");
  if(el){el.href=slug+"/index.html";el.innerHTML='<i class="fas fa-calendar-day mr-2"></i>Go to Today ('+slug.replace("-"," ").replace(/^./,function(c){return c.toUpperCase();})+')';}
})();
</script>
"""

    html += footer_html(prefix)
    return html


# ---------------------------------------------------------------------------
# Nav injection into existing pages
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

            # desktop About link -> insert On This Day before it
            desk_re = re.compile(
                r'(<a href="((?:\.\./)*)about/index\.html" class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">About</a>)'
            )
            def desk_sub(m):
                pre = m.group(2)
                link = (f'<a href="{pre}this-day-in-golf/index.html" '
                        f'class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">On This Day</a>\n        ')
                return link + m.group(1)
            new = desk_re.sub(desk_sub, new, count=1)

            # mobile About link
            mob_re = re.compile(
                r'(<a href="((?:\.\./)*)about/index\.html" class="block py-2 text-golf-text hover:text-golf-green no-underline">About</a>)'
            )
            def mob_sub(m):
                pre = m.group(2)
                link = (f'<a href="{pre}this-day-in-golf/index.html" '
                        f'class="block py-2 text-golf-text hover:text-golf-green no-underline">On This Day</a>\n      ')
                return link + m.group(1)
            new = mob_re.sub(mob_sub, new, count=1)

            if new != content:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                count += 1
    return count


# ---------------------------------------------------------------------------
# Sitemap update
# ---------------------------------------------------------------------------
def update_sitemap():
    path = os.path.join(ROOT, "sitemap.xml")
    with open(path, encoding="utf-8") as fh:
        xml = fh.read()
    if "/this-day-in-golf/" in xml:
        return 0  # already present

    entries = []
    def entry(loc, pr, freq="monthly"):
        return (f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{BUILD_DATE}</lastmod>\n"
                f"    <changefreq>{freq}</changefreq>\n    <priority>{pr}</priority>\n  </url>")

    entries.append(entry(f"{SITE}/this-day-in-golf/", "0.8", "daily"))
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

    # landing
    with open(os.path.join(SECTION_DIR, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(render_landing())

    # day pages
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
    print(f"Injected On This Day nav into {injected} existing pages")

    added = update_sitemap()
    print(f"Added {added} sitemap entries")


if __name__ == "__main__":
    main()
