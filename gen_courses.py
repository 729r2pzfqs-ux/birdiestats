# -*- coding: utf-8 -*-
import json, os, html
from course_data import COURSES

ROOT = os.path.dirname(os.path.abspath(__file__))
CJSON = json.load(open(os.path.join(os.path.dirname(ROOT), "courses.json")))
BYNAME = {c["course_name"]: c for c in CJSON["courses"]}

MAJOR_SLUG = {"Masters": "masters", "US Open": "us-open", "The Open": "the-open", "PGA Championship": "pga-championship"}
MAJOR_LABEL = {"Masters": "The Masters", "US Open": "U.S. Open", "The Open": "The Open", "PGA Championship": "PGA Championship"}

def esc(s):
    return html.escape(str(s), quote=True)

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} – Course Records & Major History | BirdieStats.com</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://birdiestats.com/courses/{slug}/">
<meta property="og:title" content="{name} – Course Records & Major History | BirdieStats.com">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://birdiestats.com/courses/{slug}/">
<meta property="og:image" content="https://birdiestats.com/og-image.png">
<meta property="og:site_name" content="BirdieStats.com">
<meta name="twitter:card" content="summary_large_image">

<link rel="apple-touch-icon" sizes="180x180" href="../../apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="../../favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="../../favicon-16x16.png">
<link rel="manifest" href="../../site.webmanifest">
<meta name="theme-color" content="#1B5E20">
<script type="application/ld+json">
{article_ld}
</script>
<script type="application/ld+json">
{breadcrumb_ld}
</script>
<script type="application/ld+json">
{faq_ld}
</script>
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
<script async src="https://www.googletagmanager.com/gtag/js?id=G-WEHSP085R8"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","G-WEHSP085R8");</script>
</head><body>
<nav class="bg-white border-b border-golf-border sticky top-0 z-50 shadow-sm">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <a href="../../index.html" class="flex items-center gap-2 no-underline">
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
        <a href="../../majors/index.html" class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">Majors</a>
        <a href="../../players/index.html" class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">Players</a>
        <a href="../../courses/index.html" class="text-golf-green font-semibold text-sm no-underline transition">Courses</a>
        <a href="../../head-to-head/index.html" class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">Head-to-Head</a>
        <a href="../../pga-tour/index.html" class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">PGA Tour</a>
        <a href="../../records/index.html" class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">Records</a>
        <a href="../../about/index.html" class="text-golf-text hover:text-golf-green font-medium text-sm no-underline transition">About</a>
      </div>
    </div>
  </div>
  <div id="mobile-menu" class="hidden md:hidden border-t border-golf-border bg-white">
    <div class="px-4 py-3 space-y-2">
      <a href="../../majors/index.html" class="block py-2 text-golf-text hover:text-golf-green no-underline">Majors</a>
      <a href="../../players/index.html" class="block py-2 text-golf-text hover:text-golf-green no-underline">Players</a>
      <a href="../../courses/index.html" class="block py-2 text-golf-text hover:text-golf-green no-underline">Courses</a>
      <a href="../../head-to-head/index.html" class="block py-2 text-golf-text hover:text-golf-green no-underline">Head-to-Head</a>
      <a href="../../pga-tour/index.html" class="block py-2 text-golf-text hover:text-golf-green no-underline">PGA Tour</a>
      <a href="../../records/index.html" class="block py-2 text-golf-text hover:text-golf-green no-underline">Records</a>
      <a href="../../about/index.html" class="block py-2 text-golf-text hover:text-golf-green no-underline">About</a>
    </div>
  </div>
</nav>
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <nav class="text-sm py-4" aria-label="Breadcrumb"><a href="../../index.html" class="text-golf-green hover:text-golf-green-md no-underline">Home</a> <span class="text-golf-muted mx-1">/</span> <a href="../../courses/index.html" class="text-golf-green hover:text-golf-green-md no-underline">Courses</a> <span class="text-golf-muted mx-1">/</span> <span class="text-golf-muted">{name}</span></nav>
</div>
"""

FOOTER = """<footer class="bg-golf-green text-white mt-16">
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
          <a href="../../majors/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Major Championships</a>
          <a href="../../players/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Players</a>
          <a href="../../courses/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Courses</a>
          <a href="../../head-to-head/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Head-to-Head</a>
          <a href="../../records/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Records</a>
        </div>
      </div>
      <div>
        <h4 class="font-display text-lg font-semibold mb-4 text-white">Info</h4>
        <div class="space-y-2">
          <a href="../../about/index.html" class="block text-green-200 hover:text-white no-underline text-sm">About</a>
          <a href="../../privacy/index.html" class="block text-green-200 hover:text-white no-underline text-sm">Privacy Policy</a>
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
</html>"""

def stat_card(label, value, sub=""):
    sub_html = f'<p class="text-golf-muted text-sm mt-1">{esc(sub)}</p>' if sub else ""
    return f'''    <div class="bg-white rounded-xl shadow-md border border-golf-border p-6">
      <p class="text-golf-muted text-sm font-medium">{esc(label)}</p>
      <p class="text-2xl font-bold text-golf-dark font-display mt-1">{value}</p>
      {sub_html}
    </div>'''

def section_header(icon_svg, title, subtitle=""):
    sub = f'\n  <p class="text-golf-muted text-sm mb-6">{esc(subtitle)}</p>' if subtitle else ""
    return f'''  <h2 class="font-display text-2xl font-bold text-golf-dark mb-2 flex items-center gap-3">
    {icon_svg}
    {esc(title)}
  </h2>{sub}'''

ICON_FLAG = '<svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#1B5E20" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22V4a1 1 0 0 1 1-1h13l-2 5 2 5H5"/><circle cx="4" cy="22" r="0.5" fill="#1B5E20"/></svg>'
ICON_TROPHY = '<svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#1B5E20" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" fill="#E8F5E9"/></svg>'
ICON_CLOCK = '<svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#1B5E20" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" fill="#E8F5E9"/><polyline points="12 6 12 12 16 14"/></svg>'
ICON_INFO = '<svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#1B5E20" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" fill="#E8F5E9"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
ICON_QA = '<svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#1B5E20" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" fill="#E8F5E9"/></svg>'

def build_page(slug, d):
    jc = BYNAME[d["json_name"]]
    name = jc["course_name"]
    location = jc["location"]
    total = jc["total_times_hosted"]
    majors = {m: yrs for m, yrs in jc["majors_hosted"].items() if yrs}
    # ordered list of (major, years) sorted by first year
    major_list = sorted(majors.items(), key=lambda kv: min(kv[1]))

    desc = f"{name} in {location}: course records, lowest rounds, the lowest 72-hole totals, and the complete major championship history of a venue that has hosted {total} majors."
    desc = esc(desc)

    # ---- structured data ----
    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": f"{name} – Course Records, Notable Rounds & Major History",
        "description": d["about"][0],
        "image": "https://birdiestats.com/og-image.png",
        "author": {"@type": "Organization", "name": "BirdieStats.com", "url": "https://birdiestats.com"},
        "publisher": {"@type": "Organization", "name": "BirdieStats.com", "logo": {"@type": "ImageObject", "url": "https://birdiestats.com/android-chrome-512x512.png"}},
        "datePublished": "2026-06-26", "dateModified": "2026-06-26",
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"https://birdiestats.com/courses/{slug}/"},
        "about": {"@type": "GolfCourse", "name": name, "address": location},
    }
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://birdiestats.com/"},
            {"@type": "ListItem", "position": 2, "name": "Courses", "item": "https://birdiestats.com/courses/"},
            {"@type": "ListItem", "position": 3, "name": name, "item": f"https://birdiestats.com/courses/{slug}/"},
        ],
    }
    faq = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faqs"]],
    }
    jd = lambda o: json.dumps(o, ensure_ascii=False)

    parts = []
    parts.append(HEAD.format(
        name=esc(name), desc=desc, slug=slug,
        article_ld=jd(article), breadcrumb_ld=jd(breadcrumb), faq_ld=jd(faq),
    ))

    # hero
    chips = " ".join(
        f'<span class="bg-white/15 text-white text-xs font-semibold px-3 py-1 rounded-full">{esc(MAJOR_LABEL[m])} &times;{len(y)}</span>'
        for m, y in major_list
    )
    parts.append(f'''
<section class="bg-gradient-to-r from-golf-green to-golf-green-md text-white py-12">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <h1 class="font-display text-3xl md:text-4xl font-bold text-white">{esc(name)}</h1>
    <p class="text-green-100 text-lg mt-2"><i class="fas fa-map-marker-alt mr-2"></i>{esc(location)} &middot; {esc(d["type"])}</p>
    <p class="text-green-200 mt-1">{total} major championships hosted since {esc(d["first_major"])}</p>
    <div class="flex flex-wrap gap-2 mt-4">{chips}</div>
  </div>
</section>
''')

    # quick facts
    parts.append('''
<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
''')
    parts.append(stat_card("Established", esc(d["established"])) + "\n")
    parts.append(stat_card("Designer", esc(d["architect"])) + "\n")
    parts.append(stat_card("Par", esc(d["par"])) + "\n")
    parts.append(stat_card("Championship Yardage", esc(d["yardage"]) + ('<span class="text-base font-normal"> yds</span>' if d["yardage"] != "—" else "")) + "\n")
    parts.append('  </div>\n</section>\n')

    # about
    about_html = "\n".join(f'    <p class="text-golf-text leading-relaxed mb-4">{esc(p)}</p>' for p in d["about"])
    parts.append(f'''
<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
{section_header(ICON_INFO, "About the Course")}
  <div class="bg-white rounded-xl shadow-md border border-golf-border p-6 md:p-8">
{about_html}
  </div>
</section>
''')

    # course records cards
    rr_score, rr_who = d["record_round"]
    r72_score, r72_who = d["record_72"]
    rr_card = stat_card("Course Record (round)", esc(rr_score), rr_who)
    r72_card = stat_card("Lowest 72-Hole Total", esc(r72_score) if r72_score != "—" else "—", r72_who)
    first_card = stat_card("First Major Hosted", esc(d["first_major"]))
    total_card = stat_card("Total Majors Hosted", str(total))
    parts.append(f'''
<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
{section_header(ICON_TROPHY, "Course Records")}
  <p class="text-golf-muted text-sm mb-6">Lowest scoring marks recorded in major championship competition at {esc(name)}.</p>
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
{rr_card}
{r72_card}
{first_card}
{total_card}
  </div>
</section>
''')

    # hosting history table
    rows = []
    for m, yrs in sorted(major_list, key=lambda kv: -len(kv[1])):
        ylist = ", ".join(str(y) for y in yrs)
        rows.append(f'''          <tr class="border-b border-golf-border/50 align-top">
            <td class="px-4 py-3 font-medium"><a href="../../majors/{MAJOR_SLUG[m]}/index.html" class="text-golf-green hover:text-golf-green-md font-semibold no-underline">{esc(MAJOR_LABEL[m])}</a></td>
            <td class="px-4 py-3 text-center font-bold text-golf-green">{len(yrs)}</td>
            <td class="px-4 py-3 text-golf-text text-sm">{ylist}</td>
          </tr>''')
    rows_html = "\n".join(rows)
    parts.append(f'''
<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
{section_header(ICON_FLAG, "Major Hosting History")}
  <p class="text-golf-muted text-sm mb-6">Every major championship staged at {esc(name)}, by championship and year.</p>
  <div class="bg-white rounded-xl shadow-md border border-golf-border overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full text-sm table-striped">
        <thead class="bg-golf-green text-white">
          <tr>
            <th class="px-4 py-3 text-left">Championship</th>
            <th class="px-4 py-3 text-center">Times</th>
            <th class="px-4 py-3 text-left">Years</th>
          </tr>
        </thead>
        <tbody>
{rows_html}
        </tbody>
      </table>
    </div>
  </div>
</section>
''')

    # notable moments timeline
    moment_cards = []
    for yr, title, text in d["moments"]:
        moment_cards.append(f'''    <div class="bg-white rounded-xl shadow-md border border-golf-border p-6 flex gap-5">
      <div class="flex-shrink-0">
        <div class="w-16 text-center">
          <span class="font-display text-xl font-bold text-golf-green">{esc(yr)}</span>
        </div>
      </div>
      <div class="border-l border-golf-border pl-5">
        <h3 class="font-display text-lg font-semibold text-golf-dark mb-1">{esc(title)}</h3>
        <p class="text-golf-text text-sm leading-relaxed">{esc(text)}</p>
      </div>
    </div>''')
    moments_html = "\n".join(moment_cards)
    parts.append(f'''
<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
{section_header(ICON_CLOCK, "Notable Moments")}
  <p class="text-golf-muted text-sm mb-6">Defining rounds and championship moments in the history of {esc(name)}.</p>
  <div class="space-y-4">
{moments_html}
  </div>
</section>
''')

    # FAQ
    faq_cards = []
    for q, a in d["faqs"]:
        faq_cards.append(f'''    <div class="bg-white rounded-xl shadow-md border border-golf-border p-6">
      <h3 class="font-display text-lg font-semibold text-golf-dark">{esc(q)}</h3>
      <p class="text-golf-text text-sm mt-2 leading-relaxed">{esc(a)}</p>
    </div>''')
    faq_html = "\n".join(faq_cards)
    parts.append(f'''
<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
{section_header(ICON_QA, "Frequently Asked Questions")}
  <div class="space-y-4">
{faq_html}
  </div>
</section>
''')

    # explore more
    parts.append('''
<section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-16 mb-8">
  <h2 class="font-display text-2xl font-bold text-golf-dark mb-6">Explore More</h2>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
    <a href="../index.html" class="bg-white rounded-xl shadow-md border border-golf-border p-6 hover:shadow-lg hover:border-golf-accent transition no-underline group">
      <div class="w-12 h-12 bg-golf-green-lt rounded-lg flex items-center justify-center mb-4 group-hover:bg-golf-accent/20 transition">
        <i class="fas fa-flag text-golf-green text-xl"></i>
      </div>
      <h3 class="font-display text-lg font-semibold text-golf-dark mb-2">All Courses</h3>
      <p class="text-golf-muted text-sm leading-relaxed">Browse all 125 venues that have hosted major championships.</p>
    </a>
    <a href="../../majors/index.html" class="bg-white rounded-xl shadow-md border border-golf-border p-6 hover:shadow-lg hover:border-golf-accent transition no-underline group">
      <div class="w-12 h-12 bg-golf-green-lt rounded-lg flex items-center justify-center mb-4 group-hover:bg-golf-accent/20 transition">
        <i class="fas fa-trophy text-golf-green text-xl"></i>
      </div>
      <h3 class="font-display text-lg font-semibold text-golf-dark mb-2">Major Championships</h3>
      <p class="text-golf-muted text-sm leading-relaxed">Complete history of all four majors from 1860 to today.</p>
    </a>
    <a href="../../records/index.html" class="bg-white rounded-xl shadow-md border border-golf-border p-6 hover:shadow-lg hover:border-golf-accent transition no-underline group">
      <div class="w-12 h-12 bg-golf-green-lt rounded-lg flex items-center justify-center mb-4 group-hover:bg-golf-accent/20 transition">
        <i class="fas fa-medal text-golf-green text-xl"></i>
      </div>
      <h3 class="font-display text-lg font-semibold text-golf-dark mb-2">Records &amp; Firsts</h3>
      <p class="text-golf-muted text-sm leading-relaxed">Youngest, oldest, largest margins, and every major record.</p>
    </a>
  </div>
</section>
''')

    parts.append(FOOTER)
    return "".join(parts)


def main():
    count = 0
    for slug, d in COURSES.items():
        outdir = os.path.join(ROOT, "courses", slug)
        os.makedirs(outdir, exist_ok=True)
        page = build_page(slug, d)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page)
        count += 1
    print(f"Generated {count} course detail pages")

if __name__ == "__main__":
    main()
