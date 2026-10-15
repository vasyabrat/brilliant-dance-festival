#!/usr/bin/env python3
"""
Static site generator for the Brilliant Dance Festival site.

Run: python3 scripts/build.py
Regenerates every .html file in the project root from data/content.json.

This is the SAME generator the admin backend (server/app.py) calls after a
save, so editing content.json by hand and re-running this script has exactly
the same effect as editing through the admin dashboard at /admin.

Dates live in content.json > site (eventDate, campDates, eventDateRange and the
ISO fields). Every page reads them from there, so a future update is one edit.
"""
import datetime
import json
import os
from html import escape
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_PATH = os.path.join(ROOT, "data", "content.json")

LOGO = "assets/logo.png"
LOGO_W, LOGO_H = 900, 229
FONTS = (
    "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700"
    "&family=Inter:wght@400;500;600;700&display=swap"
)

# (label, href, children) — a group with no href is a dropdown-only button.
NAV = [
    ("Competition", "", [
        ("Competition Overview", "competition.html"),
        ("Schedule", "schedule.html"),
        ("Prizes", "prizes.html"),
        ("Judges & Officials", "judges.html"),
        ("Partner Search", "partner-search.html"),
        ("Rules & Regulations", "rules-regulations.html"),
    ]),
    ("Camp", "camp.html", []),
    ("Event Information", "", [
        ("Registration", "registration.html"),
        ("Hotel", "hotel.html"),
        ("Vendors & Sponsors", "vendors.html"),
    ]),
    ("About", "about.html", []),
    ("Contact", "contact.html", []),
]

CHEVRON = '<svg class="chev" viewBox="0 0 12 8" width="12" height="8" aria-hidden="true"><path d="M1 1.5l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW = '<svg class="arrow" viewBox="0 0 16 10" width="16" height="10" aria-hidden="true"><path d="M1 5h13M10 1l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def load_content():
    with open(CONTENT_PATH, "r") as f:
        return json.load(f)


def e(text):
    return escape(str(text), quote=True)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def weekday(iso):
    return datetime.date.fromisoformat(iso).strftime("%A")


def day_parts(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%A"), d.strftime("%B"), str(d.day)


def has_forms(content):
    return bool(content["registrationForms"])


def reg_label(content):
    """Honest label: details only while forms are unavailable."""
    return "Register" if has_forms(content) else "Registration Details"


def btn(label, href, kind="primary", arrow=True, extra=""):
    return f'<a class="btn btn-{kind}" href="{e(href)}"{extra}>{e(label)}{ARROW if arrow else ""}</a>'


def tba(text):
    """Compact 'to be announced' message."""
    return f'<p class="tba">{e(text)}</p>'


def reveal(cls=""):
    return f'reveal {cls}'.strip()


def picture(base, alt, sizes, cls="", eager=False, widths=(600, 900, 1200), ratio=(1200, 1500)):
    srcset = ", ".join(f"{base}-{w}.jpg {w}w" for w in widths)
    loading = "eager" if eager else "lazy"
    return (
        f'<img class="{cls}" src="{base}-{widths[1]}.jpg" srcset="{srcset}" sizes="{sizes}" '
        f'width="{ratio[0]}" height="{ratio[1]}" alt="{e(alt)}" loading="{loading}" decoding="async">'
    )


def organizer_photo(org, sizes, eager=False):
    if not org.get("photo"):
        return ""
    return picture(org["photo"], org.get("photoAlt") or f"Portrait of {org['name']}", sizes, eager=eager)


def site_image(site, key, alt, sizes="(min-width: 900px) 50vw, 100vw"):
    """Optional section photo. Set site.images.<key> to a path in content.json."""
    src = (site.get("images") or {}).get(key, "")
    if not src:
        return ""
    return f'<img src="{e(src)}" alt="{e(alt)}" sizes="{sizes}" loading="lazy" decoding="async">'


def initials(name):
    parts = [w for w in name.replace("&", " ").split() if w]
    return "".join(w[0] for w in parts[:2]).upper()


def person_card(p, role_default=""):
    """One portrait card. Without a supplied photo, a clean initials tile keeps the grid even."""
    role = p.get("role") or role_default
    if p.get("photo"):
        frame = f'<div class="frame"><img src="{e(p["photo"])}" alt="{e(p["name"])}" width="500" height="600" loading="lazy" decoding="async"></div>'
    else:
        frame = f'<div class="frame frame-initials" aria-hidden="true"><span>{e(initials(p["name"]))}</span></div>'
    quote = f'<p class="quote">&ldquo;{e(p["quote"])}&rdquo;</p>' if p.get("quote") else ""
    role_html = f'<span class="role">{e(role)}</span>' if role else ""
    return f'<li class="person {reveal()}">{frame}<h3>{e(p["name"])}</h3>{role_html}{quote}</li>'


def joint_card(members):
    """Shared photograph for two people: both names shown, each counted separately."""
    photo = members[0].get("photo", "")
    names = " &amp; ".join(e(m["name"]) for m in members)
    alt = " and ".join(m["name"] for m in members)
    roles = " / ".join(dict.fromkeys(m.get("role", "") for m in members if m.get("role")))
    if photo:
        frame = f'<div class="frame"><img src="{e(photo)}" alt="{e(alt)}" width="500" height="600" loading="lazy" decoding="async"></div>'
    else:
        frame = f'<div class="frame frame-initials" aria-hidden="true"><span>{e(initials(members[0]["name"]))}</span></div>'
    return f'<li class="person person-joint {reveal()}">{frame}<h3>{names}</h3><span class="role">{e(roles)}</span></li>'


def people_list(people, role_default=""):
    """Render people in order; consecutive entries sharing a `joint` key become one card."""
    out, i = [], 0
    while i < len(people):
        p = people[i]
        key = p.get("joint")
        if key:
            group = [q for q in people[i:] if q.get("joint") == key]
            # only merge when they are adjacent
            n = 0
            while i + n < len(people) and people[i + n].get("joint") == key:
                n += 1
            out.append(joint_card(people[i:i + n]))
            i += n
        else:
            out.append(person_card(p, role_default))
            i += 1
    return '<ul class="people">' + "".join(out) + "</ul>"


def cutout(name, w, h, cls, eager=False):
    """Decorative transparent cutout (not a confirmed participant). Hidden from assistive tech."""
    loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return (
        f'<div class="cutout {cls} {reveal()}" aria-hidden="true">'
        f'<picture><source srcset="assets/images/{name}.webp" type="image/webp">'
        f'<img src="assets/images/{name}.png" alt="" width="{w}" height="{h}" {loading} decoding="async"></picture></div>'
    )


RESOURCES = [("heatListUrl", "Heat Lists", "Coming soon"), ("scoreSheetsUrl", "Score Sheets", "Not yet available")]


def resource_status(site):
    """Heat lists / score sheets: shown as unreleased until a URL is set in content.json > site."""
    items = ""
    for key, label, state in RESOURCES:
        url = site.get(key, "")
        if url:
            items += f'<li class="is-live"><a href="{e(url)}" target="_blank" rel="noopener">{e(label)}</a></li>'
        else:
            items += f'<li><span class="res-name">{e(label)}</span><span class="res-state">{e(state)}</span></li>'
    return f'<ul class="resource-list">{items}</ul>'


def ld_json(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------
def head(content, title, description, extra_head=""):
    site = content["site"]
    full_title = title if title.startswith(site["name"]) else f"{title} | {site['name']} 2027"
    og_img = (site.get("images") or {}).get("og", "")
    og_image_tags = f'\n<meta property="og:image" content="{e(og_img)}">' if og_img else ""
    card = "summary_large_image" if og_img else "summary"
    return f"""<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<meta name="theme-color" content="#101c3f">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(site['name'])}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(description)}">{og_image_tags}
<meta name="twitter:card" content="{card}">
<meta name="twitter:title" content="{e(full_title)}">
<meta name="twitter:description" content="{e(description)}">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="assets/icons/icon-48.png">
<link rel="icon" type="image/png" sizes="192x192" href="assets/icons/icon-192.png">
<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="css/style.css">
<script>document.documentElement.className='js';setTimeout(function(){{if(!document.documentElement.classList.contains('js-ready'))document.documentElement.classList.add('js-failed')}},2500);</script>
{extra_head}</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
"""


def header_html(content, active_href):
    site = content["site"]
    items = []
    for i, (label, href, children) in enumerate(NAV):
        if children:
            current = any(c_href == active_href for _, c_href in children)
            subs = "".join(
                '<li><a href="%s"%s>%s</a></li>' % (c_href, ' aria-current="page"' if c_href == active_href else "", e(c_label))
                for c_label, c_href in children
            )
            if label == "Competition":
                subs += "".join(
                    f'<li><a href="{e(site[k])}" target="_blank" rel="noopener">{e(lbl)}</a></li>' if site.get(k)
                    else f'<li class="submenu-status"><span><strong>{e(lbl)}</strong> &mdash; {e(state)}</span></li>'
                    for k, lbl, state in RESOURCES
                )
            items.append(
                f'<li class="has-menu{" is-current" if current else ""}">'
                f'<button type="button" class="menu-btn" aria-expanded="false" aria-controls="menu-{i}">{e(label)}{CHEVRON}</button>'
                f'<ul class="submenu" id="menu-{i}">{subs}</ul></li>'
            )
        else:
            cur = ' aria-current="page"' if href == active_href else ""
            items.append(f'<li><a class="nav-link" href="{href}"{cur}>{e(label)}</a></li>')
    items.append(f'<li class="nav-cta"><a class="btn btn-primary" href="registration.html">{e(reg_label(content))}</a></li>')
    nav = "\n          ".join(items)
    return f"""
<div class="announce">
  <div class="container">
    <p><span><strong>Training Camp</strong> {e(site['campDates'])}</span><span class="dot" aria-hidden="true"></span><span><strong>Competition</strong> {e(site['eventDate'])}</span></p>
  </div>
</div>
<header class="site-header">
  <div class="container nav-wrap">
    <a class="brand" href="index.html" aria-label="{e(site['name'])} — home">
      <img src="{LOGO}" alt="{e(site['name'])}" width="{LOGO_W}" height="{LOGO_H}">
    </a>
    <button type="button" class="nav-toggle" aria-expanded="false" aria-controls="site-nav"><span class="bars" aria-hidden="true"></span><span class="sr-only">Menu</span></button>
    <nav id="site-nav" class="main-nav" aria-label="Primary">
      <ul>
          {nav}
      </ul>
    </nav>
  </div>
</header>
<main id="main">
"""


def footer_html(content):
    site = content["site"]
    contact = content["contact"]
    footer_results = "".join(
        f'<li><a href="{e(site[k])}" target="_blank" rel="noopener">{e(lbl)}</a></li>' if site.get(k)
        else f'<li class="footer-status"><span>{e(lbl)} &mdash; {e(state)}</span></li>'
        for k, lbl, state in RESOURCES
    )
    social = f'<a href="{e(site["instagram"])}" target="_blank" rel="noopener">Instagram<span class="sr-only"> (opens in a new tab)</span></a>' if site.get("instagram") else ""
    return f"""
</main>
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <p class="footer-name">{e(site['name'])}</p>
        <p>A ballroom and Latin competition and training camp celebrating young dancers.</p>
        <p class="footer-dates"><strong>Training Camp</strong> {e(site['campDates'])}<br><strong>Competition</strong> {e(site['eventDate'])}</p>
      </div>
      <nav aria-label="Competition">
        <h2>Competition</h2>
        <ul>
          <li><a href="competition.html">Overview</a></li>
          <li><a href="registration.html">Registration</a></li>
          <li><a href="schedule.html">Schedule</a></li>
          <li><a href="rules-regulations.html">Rules &amp; Regulations</a></li>
          {footer_results}
        </ul>
      </nav>
      <nav aria-label="Event information">
        <h2>Event</h2>
        <ul>
          <li><a href="camp.html">Training Camp</a></li>
          <li><a href="judges.html">Judges &amp; Officials</a></li>
          <li><a href="hotel.html">Hotel</a></li>
          <li><a href="vendors.html">Vendors &amp; Sponsors</a></li>
        </ul>
      </nav>
      <div>
        <h2>Contact</h2>
        <ul>
          <li>{e(contact['name'])}, {e(contact['role'])}</li>
          <li><a href="mailto:{e(contact['email'])}">{e(contact['email'])}</a></li>
          <li><a href="tel:{e(contact['phone'].replace('-', ''))}">{e(contact['phone'])}</a></li>
          <li>{social}</li>
        </ul>
      </div>
    </div>
    <div class="bottom-bar">
      <span>&copy; 2027 {e(site['name'])}</span>
      <span><a href="about.html">About</a> &middot; <a href="/admin">Admin</a></span>
    </div>
  </div>
</footer>
<script src="js/main.js" defer></script>
</body>
</html>
"""


def page(filename, content, title, description, active_href, body, extra_head=""):
    with open(os.path.join(ROOT, filename), "w") as f:
        f.write(head(content, title, description, extra_head))
        f.write(header_html(content, active_href))
        f.write(body)
        f.write(footer_html(content))


def page_hero(eyebrow, title, lede="", actions=""):
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    actions_html = f'<div class="actions">{actions}</div>' if actions else ""
    return f"""
<section class="page-hero">
  <div class="container narrow-left">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{title}</h1>
    {lede_html}
    {actions_html}
  </div>
</section>
"""


def section(inner, cls="", head_html="", label=""):
    aria = f' aria-labelledby="{label}"' if label else ""
    return f'<section class="section {cls}"{aria}><div class="container">{head_html}{inner}</div></section>'


def section_head(eyebrow, title, intro="", hid="", align=""):
    idattr = f' id="{hid}"' if hid else ""
    intro_html = f'<p class="lead">{intro}</p>' if intro else ""
    eb = f'<p class="eyebrow">{eyebrow}</p>' if eyebrow else ""
    return f'<div class="section-head {align} {reveal()}">{eb}<h2{idattr}>{title}</h2>{intro_html}</div>'


def organizer_block(content, compact=False):
    org = content["organizers"][0] if content["organizers"] else None
    if not org:
        return ""
    photo = organizer_photo(org, "(min-width: 900px) 420px, (min-width: 600px) 60vw, 90vw")
    return f"""
<div class="organizer {'is-compact' if compact else ''}">
  <figure class="portrait {reveal('reveal-img')}">{photo}</figure>
  <div class="organizer-copy {reveal()}">
    <p class="eyebrow">Meet the Organizer</p>
    <h2 id="organizer-title">{e(org['name'])}</h2>
    <p class="role-line">{e(org['role'])}</p>
    <p>{e(org['name'])} organizes {e(content['site']['name'])}. {e(org.get('bio', ''))}</p>
    <p>{e(org['name'])} is also the main contact for questions about registration, camp and the competition.</p>
    <div class="actions">{btn('About the festival', 'about.html', 'secondary')}{btn('Contact Nina', 'contact.html', 'text')}</div>
  </div>
</div>"""


def three_days(content):
    site = content["site"]
    camp_rows = "".join(f'<li><span class="time">{e(s["time"])}</span><span>{e(s["label"])}</span></li>' for s in content["campSchedule"])
    comp_rows = "".join(f'<li><span class="time">{e(s["time"])}</span><span>{e(s["label"])}</span></li>' for s in content["homeSchedule"])
    days = [
        (site["campStartISO"], "Training Camp", "Day 1", "camp", camp_rows, "camp.html", "Camp details"),
        (site["campEndISO"], "Training Camp", "Day 2", "camp", camp_rows, "camp.html", "Camp details"),
        (site["eventDateISO"], "Competition", "Competition day", "comp", comp_rows, "schedule.html", "Full schedule"),
    ]
    cards = ""
    for iso, kind, sub, cls, rows, href, link in days:
        wd, month, num = day_parts(iso)
        cards += f"""
    <li class="day {cls} {reveal()}">
      <div class="day-date"><p class="day-wd">{wd}</p><p class="day-num"><span>{num}</span> {month}</p></div>
      <div class="day-main">
        <p class="day-kind">{kind} <span class="day-sub">&middot; {sub}</span></p>
        <ul class="day-times">{rows}</ul>
        <a class="text-link" href="{href}">{link}{ARROW}</a>
      </div>
    </li>"""
    return f'<ol class="days">{cards}</ol>'


# ---------------------------------------------------------------------------
# PAGES
# ---------------------------------------------------------------------------
def build_home(content):
    site = content["site"]
    forms = has_forms(content)
    hotel = content["hotel"]
    maps = "https://www.google.com/maps/search/?api=1&query=" + quote(hotel["address"])
    why = "".join(
        f'<li class="{reveal()}"><span class="num" aria-hidden="true">{i:02d}</span><div><h3>{e(w["title"])}</h3><p>{e(w["text"])}</p></div></li>'
        for i, w in enumerate(content["whyChooseUs"], 1)
    )
    n_judges = len(content["judgingPanel"])
    n_off = len(content["officials"])
    judges_fact = (
        '<a href="judges.html">Meet the judges &amp; officials</a>' if n_judges else "To be announced"
    )
    venue_fact = (
        f'{e(hotel["name"])}<br><a href="{e(maps)}" target="_blank" rel="noopener">Directions</a> &middot; <a href="hotel.html">Venue details</a>'
        if hotel.get("name") else "To be announced"
    )
    if hotel.get("bookUrl"):
        hotel_fact = f'<a class="btn btn-primary btn-sm" href="{e(hotel["bookUrl"])}" target="_blank" rel="noopener">Book your stay{ARROW}</a>'
        if hotel.get("discountCode"):
            hotel_fact += f'<br><span class="code-note">Discount code <strong class="code">{e(hotel["discountCode"])}</strong></span>'
    elif hotel.get("name") and hotel.get("bookingStatus"):
        hotel_fact = e(hotel["bookingStatus"])
    else:
        hotel_fact = "To be announced"
    details = f"""
<dl class="facts">
  <div><dt>Competition</dt><dd>{e(weekday(site['eventDateISO']))}, {e(site['eventDate'])}</dd></div>
  <div><dt>Training Camp</dt><dd>{e(weekday(site['campStartISO']))} &amp; {e(weekday(site['campEndISO']))}, {e(site['campDates'])}</dd></div>
  <div><dt>Venue</dt><dd>{venue_fact}</dd></div>
  <div><dt>Hotel booking</dt><dd>{hotel_fact}</dd></div>
  <div><dt>Entry types</dt><dd>{e(', '.join(f['name'] for f in content['registrationForms'])) if forms else 'Announced with registration'}</dd></div>
  <div><dt>Styles</dt><dd>International Ballroom, International Latin, American Smooth, American Rhythm</dd></div>
  <div><dt>Judging panel</dt><dd>{judges_fact}</dd></div>
  <div><dt>Heat lists &amp; scores</dt><dd>Heat Lists &mdash; Coming soon<br>Score Sheets &mdash; Not yet available</dd></div>
</dl>"""
    steps = (
        """<ol class="steps">
  <li><h3>Choose your category</h3><p>Pick the entry form that matches how you dance.</p></li>
  <li><h3>Complete the form</h3><p>Fill in every field, then mark your dances and levels.</p></li>
  <li><h3>Submit and pay</h3><p>Email the form and send payment as listed on the registration page.</p></li>
</ol>""" if forms else
        '<p class="tba">2027 registration forms are coming soon. Registration details will appear here as soon as they are available.</p>'
    )
    camp_price_line = (
        " &middot; ".join(e(p["amount"]) + " " + e(p.get("short") or p["title"].lower()) for p in content["campPricing"]) + "."
        if content["campPricing"] else "Pricing and schedule will be announced."
    )
    body = f"""
<section class="hero hero-art">
  <div class="container hero-grid">
    <div class="hero-copy">
      <p class="eyebrow on-dark">2027 Edition</p>
      <h1>{e(content['hero']['title'])}</h1>
      <p class="hero-tagline">A stage for the next generation of ballroom dancers.</p>
      <p class="hero-lede">{e(content['hero']['lede'])}</p>
      <dl class="hero-dates">
        <div><dt>Training Camp</dt><dd>{e(site['campDates'])}</dd></div>
        <div><dt>Competition</dt><dd>{e(site['eventDate'])}</dd></div>
      </dl>
      <div class="actions">
        {btn('Competition ' + ('Registration' if forms else 'Details'), 'registration.html', 'light')}
        {btn('Camp Information', 'camp.html', 'ghost')}
      </div>
    </div>
    {cutout("camp-couple", 765, 1000, "cutout--couple", eager=True)}
  </div>
</section>

{section(f'''
<div class="duo">
  <article class="path path-camp {reveal()}">
    <p class="path-kind">Training Camp</p>
    <h3>{e(site['campDates'])}</h3>
    <p>Two days of training ahead of the competition: private lessons, lectures and practice rounds. {camp_price_line}</p>
    {btn('Camp information', 'camp.html', 'secondary')}
  </article>
  <article class="path path-comp {reveal()}">
    <p class="path-kind">Competition</p>
    <h3>{e(site['eventDate'])}</h3>
    <p>A one-day competition in International Ballroom, International Latin, American Smooth and American Rhythm, for dancers from Minis through U21. Entries include solos, amateur couples and teacher/student.</p>
    {btn('Competition overview', 'competition.html', 'secondary')}
  </article>
</div>''', "", section_head("The weekend", "Two events, one festival", "Train with coaches on Friday and Saturday, then compete on Sunday. Dancers can take part in either or both.", "overview-title"), "overview-title")}

{section(f'''
<div class="split-text">
  <div class="{reveal()}">
    <p class="eyebrow">Why Brilliant</p>
    <h2 id="why-title">Built around young dancers</h2>
    <p class="lead">{e(content['missionText'])}</p>
  </div>
  <ol class="why">{why}</ol>
</div>''', "alt", "", "why-title")}

{section(organizer_block(content), "", "", "organizer-title")}

<section class="section alt days-section" aria-labelledby="days-title">
  <div class="container days-grid">
    {cutout("camp-high-kick", 511, 1000, "cutout--kick")}
    <div class="days-body">
      {section_head("Three days", "January 8&ndash;10 at a glance", "Camp runs Friday and Saturday; the competition is Sunday. Competition scheduling is finalized during event week.", "days-title", "left")}
      {three_days(content)}
    </div>
  </div>
</section>

<section class="section info-section" aria-labelledby="info-title">
  <div class="container info-grid">
    <div class="{reveal()}">
      <p class="eyebrow">Plan your visit</p>
      <h2 id="info-title">Event information</h2>
      {details}
    </div>
    <div class="info-reg {reveal()}">
      <h3 class="h3-display">How registration works</h3>
      {steps}
      <p class="small-note">Please read the <a href="rules-regulations.html">Rules &amp; Regulations</a> before you enter.</p>
    </div>
    {cutout("camp-boy", 466, 700, "cutout--boy")}
  </div>
</section>

<section class="cta-band">
  <div class="container {reveal()}">
    <h2>Ready to dance at Brilliant?</h2>
    <p>{'Choose your entry category and download the form.' if forms else 'Registration details will be posted here as soon as the 2027 forms are ready.'}</p>
    <div class="actions center">{btn(reg_label(content), 'registration.html', 'light')}{btn('Ask a question', 'contact.html', 'ghost')}</div>
  </div>
</section>
"""
    event_ld = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": f"{site['name']} 2027",
        "description": "Ballroom and Latin competition and training camp for young dancers.",
        "startDate": site["campStartISO"],
        "endDate": site["eventDateISO"],
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "organizer": {"@type": "Person", "name": content["organizers"][0]["name"]} if content["organizers"] else None,
        "location": {"@type": "Place", "name": hotel["name"], "address": hotel["address"]} if hotel.get("name") else None,
        "subEvent": [
            {"@type": "Event", "name": "Brilliant Ballroom Training Camp", "startDate": site["campStartISO"], "endDate": site["campEndISO"]},
            {"@type": "Event", "name": f"{site['name']} Competition", "startDate": site["eventDateISO"]},
        ],
    }
    event_ld = {k: v for k, v in event_ld.items() if v is not None}
    page("index.html", content, f"{site['name']} 2027 | Camp {site['campDates']} · Competition {site['eventDate']}",
         f"{site['name']} 2027: Training Camp {site['campDates']} and ballroom competition {site['eventDate']} at {hotel['name'] or 'the festival venue'}. Registration, schedule and event information.",
         "index.html", body, ld_json(event_ld) + "\n")


def build_competition(content):
    site = content["site"]
    forms = has_forms(content)
    hotel = content["hotel"]
    cats = "".join(
        f'<li class="{reveal()}"><h3>{e(f["name"])}</h3><p>{e(f.get("detail", ""))}</p></li>' for f in content["registrationForms"]
    )
    cats = f'<ul class="chips-list">{cats}</ul>' if forms else tba("Entry categories will be listed when the 2027 registration forms are published.")
    program = program_rows(content["homeSchedule"]) + program_rows(content["competitionSchedule"])
    n_j, n_o = len(content["judgingPanel"]), len(content["officials"])
    prize_names = ", ".join(t["title"] for t in content["prizeTables"]) if content["prizeTables"] else "To be announced"
    body = page_hero(
        e(site["eventDate"]), "Competition",
        "A professional-grade ballroom and Latin competition giving young dancers the recognition they deserve.",
        btn(reg_label(content), "registration.html", "light") + btn("Rules & Regulations", "rules-regulations.html", "ghost"),
    ) + section(f"""
<div class="info-split">
  <div class="{reveal()}">
    <h3 class="h3-display">At a glance</h3>
    <dl class="facts">
      <div><dt>Date</dt><dd>{e(weekday(site['eventDateISO']))}, {e(site['eventDate'])}</dd></div>
      <div><dt>Venue</dt><dd>{e(hotel['name']) if hotel.get('name') else 'To be announced'}{' &middot; <a href="hotel.html">Venue details</a>' if hotel.get('name') else ''}</dd></div>
      <div><dt>Styles</dt><dd>International Ballroom, International Latin, American Smooth, American Rhythm</dd></div>
      <div><dt>Age categories</dt><dd>Minis (3&ndash;5), TB (6&ndash;7), PT1 (8&ndash;9), PT2 (10&ndash;11), J1 (12&ndash;13), J2 (14&ndash;15), Youth (16&ndash;18), U21 (19&ndash;20)</dd></div>
      <div><dt>Rules</dt><dd>NDCA rules and regulations apply</dd></div>
    </dl>
  </div>
  <div class="{reveal()}">
    <h3 class="h3-display">Entry categories</h3>
    {cats}
    <p class="small-note">Fees, levels and dance lists are on each registration form.</p>
  </div>
</div>""", "", section_head("Details", "What to know before you enter", "", "comp-title", "left"), "comp-title") + section(f"""
<ul class="program program-wide {reveal()}">{program}</ul>
<p class="small-note">Times are local venue time. This is the published program; final scheduling is posted during event week and may change with entries. <a href="schedule.html">See the full schedule</a>.</p>""",
        "alt", section_head("Sunday, " + e(site["eventDate"]), "Competition-day program", "", "prog-title", "left"), "prog-title") + section(f"""
<ul class="link-rows">
  <li class="{reveal()}"><a href="registration.html"><span><strong>Registration</strong><em>Forms, submission and payment</em></span>{ARROW}</a></li>
  <li class="{reveal()}"><a href="schedule.html"><span><strong>Schedule</strong><em>Camp days and competition day</em></span>{ARROW}</a></li>
  <li class="{reveal()}"><a href="judges.html"><span><strong>Judges &amp; Officials</strong><em>Meet the judging panel and officials</em></span>{ARROW}</a></li>
  <li class="{reveal()}"><a href="prizes.html"><span><strong>Prizes</strong><em>{e(prize_names)}</em></span>{ARROW}</a></li>
  <li class="{reveal()}"><a href="partner-search.html"><span><strong>Partner Search</strong><em>Dancers looking for a Latin partner</em></span>{ARROW}</a></li>
</ul>
<div class="resource-row {reveal()}"><h3 class="h3-display">Results</h3>{resource_status(site)}</div>""", "", section_head("Explore", "More about the competition", "", "explore-title", "left"), "explore-title")
    page("competition.html", content, "Competition", f"Brilliant Dance Festival competition, {site['eventDate']}: styles, age categories, entry types, program and links to registration, schedule and rules.", "competition.html", body)


def build_about(content):
    site = content["site"]
    about = content["about"]
    pillars = "".join(f"<li>{e(v)}</li>" for v in content["pillars"])
    why = "".join(
        f'<li class="{reveal()}"><span class="num" aria-hidden="true">{i:02d}</span><div><h3>{e(w["title"])}</h3><p>{e(w["text"])}</p></div></li>'
        for i, w in enumerate(content["whyChooseUs"], 1)
    )
    preview = people_list(content["homeFeaturedJudges"]) if content["homeFeaturedJudges"] else ""
    org = content["organizers"][0]["name"] if content["organizers"] else "our organizer"
    body = page_hero("About", e(about["headline"]), e(about["story"])) \
        + section(organizer_block(content), "", "", "organizer-title") \
        + section(f"""
<div class="split-text">
  <div class="{reveal()}">
    <p class="eyebrow">Mission &amp; Vision</p>
    <h2 id="mission-title">Our mission &amp; vision</h2>
  </div>
  <div class="{reveal()}">
    <p class="lead">{e(about['mission'])}</p>
    <p>{e(about['vision'])}</p>
  </div>
</div>""", "alt", "", "mission-title") \
        + section(f'<ol class="why">{why}</ol>', "", section_head("Why choose us", "Why choose us", "A competition that celebrates young ballroom talent with professionalism, expert judges, and exceptional awards.", "apart-title", "left"), "apart-title") \
        + (section(preview + f'<div class="actions">{btn("Meet all judges &amp; officials".replace("&amp;", "&"), "judges.html", "secondary")}</div>', "alt", section_head("Judges", "Meet our judges", "A panel of experts bringing experience, fairness, and valuable feedback to every performance.", "judges-title", "left"), "judges-title") if preview else "") \
        + section(f'<ul class="values {reveal()}">{pillars}</ul>', "", section_head("Values", "Values we offer", "", "values-title"), "values-title")
    page("about.html", content, "About", f"About {site['name']}: our mission and vision, and {org}, the organizer behind the festival.", "about.html", body)


def build_partner_search(content):
    site = content["site"]
    cards = "".join(
        f"""<li class="listing {reveal()}"><h3>{e(p["name"])}</h3>
        <p><strong>Level:</strong> {e(p["level"])}<br><strong>Studio:</strong> {e(p["studio"])}<br><strong>Coaches:</strong> {e(p["coaches"])}<br><strong>Contact:</strong> {e(p["contact"])}</p>
        <p>{e(p["note"])}</p></li>""" for p in content["partnerSearch"]
    )
    inner = f'<ul class="listings">{cards}</ul>' if cards else f'<div class="notice {reveal()}"><h2>No listings yet</h2><p>Dancers looking for a Latin partner for the 2027 festival will be listed here. To be listed or to ask about partners, <a href="contact.html">contact the organizer</a>.</p></div>'
    body = page_hero("Latin only", "Partner Search", f"Dancers looking for a Latin partner ahead of {e(site['eventDate'])}.") + section(inner)
    page("partner-search.html", content, "Partner Search", f"Partner search for {site['name']} 2027: dancers looking for a Latin partner.", "partner-search.html", body)


def build_judges(content):
    site = content["site"]
    judges, officials = content["judgingPanel"], content["officials"]
    j_html = people_list(judges) if judges else tba("The judging panel will be announced.")
    o_html = people_list(officials) if officials else tba("Officials will be announced.")
    count = len(judges)
    body = page_hero(e(site["eventDate"]), "Judges &amp; Officials",
                     f"The judging panel and officials for the {e(site['eventDate'])} competition.") \
        + section(f"""
<div class="roster-block">
  <h2 class="h3-display {reveal()}">Judges</h2>
  {j_html}
</div>""", "") \
        + section(f"""
<div class="roster-block">
  <h2 class="h3-display {reveal()}">Officials</h2>
  {o_html}
</div>""", "alt") \
        + section(organizer_block(content, compact=True), "", "", "organizer-title")
    page("judges.html", content, "Judges & Officials", f"Judges and officials for {site['name']} 2027, {site['eventDate']}.", "judges.html", body)


def vendor_card(v):
    logo = (
        f'<div class="vendor-logo"><img src="{e(v["logo"])}" alt="{e(v["name"])} logo" loading="lazy" decoding="async"></div>'
        if v.get("logo") else f'<div class="vendor-logo vendor-wordmark" aria-hidden="true"><span>{e(v["name"])}</span></div>'
    )
    links = []
    if v.get("buttonLabel") and v.get("buttonUrl"):
        links.append(f'<a class="btn btn-primary" href="{e(v["buttonUrl"])}" target="_blank" rel="noopener">{e(v["buttonLabel"])}{ARROW}</a>')
    meta = []
    if v.get("website") and not (v.get("buttonUrl") == v.get("website")):
        meta.append(f'<a href="{e(v["website"])}" target="_blank" rel="noopener">{e(v.get("websiteLabel") or "Website")}</a>')
    if v.get("instagram"):
        meta.append(f'<a href="{e(v["instagram"])}" target="_blank" rel="noopener">Instagram</a>')
    if v.get("phone"):
        digits = "".join(ch for ch in v["phone"] if ch.isdigit() or ch == "+")
        if not digits.startswith("+"):
            digits = "+1" + digits
        meta.append(f'<a href="tel:{e(digits)}">{e(v["phone"])}</a>')
    if v.get("email"):
        meta.append(f'<a href="mailto:{e(v["email"])}">{e(v["email"])}</a>')
    meta_html = '<ul class="vendor-links">' + "".join(f"<li>{m}</li>" for m in meta) + "</ul>" if meta else ""
    note = f'<p class="vendor-note">{e(v["note"])}</p>' if v.get("note") else ""
    cat = f'<p class="vendor-cat">{e(v["category"])}</p>' if v.get("category") else ""
    desc = f'<p>{e(v["desc"])}</p>' if v.get("desc") and v.get("desc") != v.get("category") else ""
    btn_html = f'<div class="vendor-actions">{"".join(links)}</div>' if links else ""
    return f'<li class="vendor-card {reveal()}">{logo}<div class="vendor-body">{cat}<h3>{e(v["name"])}</h3>{desc}{note}{meta_html}{btn_html}</div></li>'


def build_vendors(content):
    site = content["site"]
    vendors = "".join(vendor_card(v) for v in content["vendors"])
    sponsors = "".join(vendor_card(s) for s in content["sponsors"])
    v_html = f'<ul class="vendor-grid">{vendors}</ul>' if vendors else tba("Vendors will be announced.")
    s_html = f'<ul class="vendor-grid">{sponsors}</ul>' if sponsors else tba("Sponsors will be announced.")
    body = page_hero(e(site["eventDate"]), "Vendors &amp; Sponsors", f"Businesses and service providers supporting {e(site['name'])}.") \
        + section(v_html, "", section_head("Vendors", "Beauty, apparel, photography &amp; video", "", "vendors-title", "left"), "vendors-title") \
        + section(s_html, "alt", section_head("Sponsors", "Thank you to our sponsors", "", "sponsors-title", "left"), "sponsors-title") \
        + section('<p class="small-note center">Interested in being a vendor or sponsor? <a href="contact.html">Get in touch</a>.</p>', "")
    page("vendors.html", content, "Vendors & Sponsors", f"Vendors and sponsors of {site['name']} 2027.", "vendors.html", body)


def build_hotel(content):
    site = content["site"]
    hotel = content["hotel"]
    photos = "".join(
        f'<figure class="venue-photo {reveal("reveal-img")}"><img src="{e(src)}" alt="{e(hotel["name"])}" loading="lazy" decoding="async"></figure>'
        for src in hotel.get("images", [])
    )
    maps = "https://www.google.com/maps/search/?api=1&query=" + quote(hotel["address"])
    blank = ' target="_blank" rel="noopener"'
    code = hotel.get("discountCode", "")
    if hotel.get("bookUrl"):
        book = '<div class="actions">' + btn("Get directions", maps, "secondary", True, blank) + "</div>"
        code_html = (
            f'<p class="code-line">Use code <strong class="code">{e(code)}</strong> for the Brilliant Dance Festival discount.</p>'
            if code else ""
        )
        status = (
            f'<p>Book your room through the Brilliant Dance Festival group page at Hilton. The festival group rate is applied automatically.</p>'
            + code_html
            + '<div class="actions">' + btn("Book your stay", hotel["bookUrl"], "primary", True, blank) + "</div>"
        )
    else:
        book = '<div class="actions">' + btn("Get directions", maps, "primary", True, blank) + "</div>"
        status = f'<p class="tba">{e(hotel.get("bookingStatus") or "Group booking details are pending confirmation.")}</p>'
    body = page_hero("Venue &amp; hotel", e(hotel["name"]),
                     f"Training Camp {e(site['campDates'])} &middot; Competition {e(site['eventDate'])}") + section(f"""
<div class="info-split">
  <div class="{reveal()}">
    <h2 class="h3-display">Event venue</h2>
    <dl class="facts">
      <div><dt>Venue</dt><dd>{e(hotel['name'])}</dd></div>
      <div><dt>Address</dt><dd>{e(hotel['address'])}</dd></div>
      <div><dt>Training Camp</dt><dd>Friday &amp; Saturday, {e(site['campDates'])}</dd></div>
      <div><dt>Competition</dt><dd>Sunday, {e(site['eventDate'])}</dd></div>
    </dl>
    {book}
  </div>
  <div class="{reveal()}">
    <h2 class="h3-display">Hotel booking</h2>
    {status}
    <p class="small-note">Questions about rooms or the venue? <a href="contact.html">Contact the organizer</a>.</p>
  </div>
</div>""") + (section(f'<div class="venue-photos">{photos}</div>', "alt") if photos else "")
    page("hotel.html", content, "Venue & Hotel", f"{hotel['name']}, {hotel['address']}: venue for {site['name']} 2027, {site['eventDateRange']}.", "hotel.html", body)


def build_prizes(content):
    site = content["site"]
    tables = "".join(
        f"""<table class="prize-table {reveal()}"><caption>{e(t['title'])}</caption><tbody>{''.join(f'<tr><th scope="row">{e(a)}</th><td>{e(b)}</td></tr>' for a, b in t['rows'])}</tbody></table>"""
        for t in content["prizeTables"]
    )
    inner = f'<div class="duo">{tables}</div>' if tables else f'<div class="notice {reveal()}"><h2>Prize details coming soon</h2><p>Prizes and awards for 2027 have not been confirmed yet. They will be published here once they are. Questions? <a href="contact.html">Contact the organizer</a>.</p></div>'
    body = page_hero(e(site["eventDate"]), "Prizes &amp; Awards", "Awards recognizing the dedication and achievement of every participant.") + section(inner)
    page("prizes.html", content, "Prizes & Awards", f"Prizes and awards at {site['name']} 2027.", "prizes.html", body)


def program_rows(items, time_key="time"):
    return "".join(
        f'<li><span class="time">{e(i[time_key])}</span><span>{e(i["label"])}</span></li>' for i in items
    )


def build_schedule(content):
    site = content["site"]
    camp = program_rows(content["campSchedule"])
    open_rows = program_rows(content["homeSchedule"])
    blocks = program_rows(content["competitionSchedule"])
    w1, m1, n1 = day_parts(site["campStartISO"]); w2, m2, n2 = day_parts(site["campEndISO"]); w3, m3, n3 = day_parts(site["eventDateISO"])
    results = resource_status(site)
    body = page_hero(e(site["eventDateRange"]), "Schedule",
                     "Training Camp on Friday and Saturday, competition on Sunday. Final competition scheduling is published during event week and may change with entries.") + section(f"""
<div class="timeline">
  <div class="tl-day camp {reveal()}"><div class="tl-date"><span>{w1}</span><strong>{m1} {n1}</strong></div>
    <div class="tl-body"><h2>Training Camp &mdash; Day 1</h2><ul class="program">{camp}</ul></div></div>
  <div class="tl-day camp {reveal()}"><div class="tl-date"><span>{w2}</span><strong>{m2} {n2}</strong></div>
    <div class="tl-body"><h2>Training Camp &mdash; Day 2</h2><ul class="program">{camp}</ul></div></div>
  <div class="tl-day comp {reveal()}"><div class="tl-date"><span>{w3}</span><strong>{m3} {n3}</strong></div>
    <div class="tl-body"><h2>Competition</h2>
      <ul class="program">{open_rows}</ul>
      <h3 class="program-sub">Published program</h3>
      <ul class="program">{blocks}</ul>
      <p class="small-note">Times are local venue time. This is the provisional session program, not final heat assignments; final scheduling is posted during event week and may change based on entries.</p>
    </div></div>
</div>""") + section(f'<div class="resource-row {reveal()}">{results}</div>', "alt", section_head("Results", "Heat lists &amp; score sheets", "", "results-title", "left"), "results-title")
    page("schedule.html", content, "Schedule", f"Schedule for {site['name']} 2027: Training Camp {site['campDates']} and competition {site['eventDate']}.", "schedule.html", body)


def build_camp(content):
    site = content["site"]
    forms = has_forms(content)
    camp_items = "".join(f'<li><span>{e(s["label"])}</span><span class="time">{e(s["time"])}</span></li>' for s in content["campSchedule"])
    w1, m1, n1 = day_parts(site["campStartISO"]); w2, m2, n2 = day_parts(site["campEndISO"])
    pricing = "".join(
        f'<div class="price {reveal()}"><h3>{e(p["title"])}</h3><p class="amount">{e(p["amount"])}</p><p>{e(p["note"])}</p>'
        + (f'<a class="btn btn-primary" href="{e(p["href"])}" target="_blank" rel="noopener">Pay for camp<span class="sr-only"> &mdash; {e(p["title"])}, {e(p["amount"])}</span>{ARROW}</a>' if p.get("href") else "")
        + '</div>' for p in content["campPricing"]
    )
    pricing_html = f'<div class="prices">{pricing}</div>' if pricing else tba("Camp pricing will be announced.")
    ball, latin = content["campCoaches"]["ballroom"], content["campCoaches"]["latin"]
    faculty = content["campCoaches"].get("faculty", [])
    parts = []
    if faculty:
        parts.append(f'<div class="roster-block"><h3 class="h3-display {reveal()}">Camp coaches</h3>{people_list(faculty, "Camp Coach")}</div>')
    if ball or latin:
        parts.append(
            f'<div class="roster-block"><h3 class="h3-display {reveal()}">Ballroom Coaches</h3>{people_list(ball, "Ballroom Coach") if ball else tba("Ballroom coaches to be announced.")}</div>'
            f'<div class="roster-block"><h3 class="h3-display {reveal()}">Latin Coaches</h3>{people_list(latin, "Latin Coach") if latin else tba("Latin coaches to be announced.")}</div>'
        )
    elif not faculty:
        parts.append(f'<div class="duo"><div class="panel {reveal()}"><h3 class="h3-display">Ballroom Coaches</h3>{tba("To be announced.")}</div><div class="panel {reveal()}"><h3 class="h3-display">Latin Coaches</h3>{tba("To be announced.")}</div></div>')
    else:
        parts.append(f'<p class="small-note">Additional ballroom and Latin coaches will be announced.</p>')
    coaches = '<div class="coach-stack">' + "".join(parts) + "</div>"
    coach_names = ", ".join(c["name"] for c in faculty + ball + latin) or "To be announced"
    paying = any(p.get("href") for p in content["campPricing"])
    status = (
        "Camp spots are paid online: choose one day or both days in the pricing section below. Session times and coaches will be posted on this page."
        if paying else "Camp registration and pricing details have not been announced yet. They will be posted on this page."
    )
    img = site_image(site, "camp", "Dancers at Brilliant Ballroom Training Camp")
    body = page_hero(e(site["campDates"]), "Brilliant Ballroom Training Camp",
                     "Two days of training &mdash; private lessons, lectures and practice rounds &mdash; leading into the competition on " + e(site["eventDate"]) + ".",
                     btn("Competition registration", "registration.html", "ghost") if forms else "") \
        + section(f"""
<div class="info-split">
  <div class="{reveal()}">
    <h3 class="h3-display">Camp at a glance</h3>
    <dl class="facts">
      <div><dt>Dates</dt><dd>{e(w1)} {e(m1)} {n1} &amp; {e(w2)} {e(m2)} {n2}, 2027</dd></div>
      <div><dt>Format</dt><dd>Private lessons, lectures (four per day) and practice rounds</dd></div>
      <div><dt>Coaches</dt><dd>{e(coach_names)}</dd></div>
      <div><dt>Pricing</dt><dd>{' &middot; '.join(e(p['amount']) + ' ' + e(p.get('short') or p['title'].lower()) for p in content['campPricing']) if content['campPricing'] else 'To be announced'}</dd></div>
      <div><dt>Registration</dt><dd>{'Pay online below' if paying else 'Details to be announced'}</dd></div>
    </dl>
  </div>
  <div class="{reveal()}">
    <div class="notice left"><h3 class="h3-display">Registration status</h3><p>{e(status)}</p>
      {'<div class="actions">' + btn("See pricing and pay", "#price-title", "primary") + '</div>' if paying else ''}<p class="small-note">The 2027 entry forms are for the competition. Questions about camp? <a href="contact.html">Contact the organizer</a>.</p></div>
    {'<figure class="photo-slot reveal reveal-img">' + img + '</figure>' if img else ''}
  </div>
</div>""", "", section_head("Overview", "Camp at Brilliant", "", "camp-title", "left"), "camp-title") \
        + section(f"""
<div class="duo">
  <div class="panel {reveal()}"><h3 class="h3-display">{w1}, {m1} {n1}</h3><p class="day-sub">Training Camp &mdash; Day 1</p><ul class="time-list">{camp_items}</ul></div>
  <div class="panel {reveal()}"><h3 class="h3-display">{w2}, {m2} {n2}</h3><p class="day-sub">Training Camp &mdash; Day 2</p><ul class="time-list">{camp_items}</ul></div>
</div>
<p class="small-note">Published daily program, repeated on both camp days. Lesson availability and coaching assignments will be announced.</p>""", "alt", section_head("Schedule", "Two days of training", "", "campdays-title", "left"), "campdays-title") \
        + section(pricing_html, "", section_head("Pricing", "Camp pricing", "", "price-title", "left"), "price-title") \
        + section(coaches, "alt", section_head("Faculty", "Coaches", "", "coach-title", "left"), "coach-title")
    page("camp.html", content, "Brilliant Ballroom Training Camp", f"Brilliant Ballroom Training Camp, {site['campDates']}: two days of training ahead of the {site['eventDate']} competition.", "camp.html", body)


def build_contact(content):
    site = content["site"]
    contact = content["contact"]
    org = content["organizers"][0] if content["organizers"] else None
    photo = organizer_photo(org, "(min-width: 900px) 240px, 40vw") if org else ""
    body = page_hero("Get in touch", "Contact", "Questions about registration, camp or the competition? Send a message or reach the organizer directly.") + section(f"""
<div class="contact-grid">
  <div class="contact-card {reveal()}">
    {'<figure class="portrait small">' + photo + '</figure>' if photo else ''}
    <h2>{e(contact['name'])}</h2>
    <p class="role-line">{e(contact['role'])}</p>
    <dl class="facts">
      <div><dt>Phone</dt><dd><a href="tel:{e(contact['phone'].replace('-', ''))}">{e(contact['phone'])}</a></dd></div>
      <div><dt>Email</dt><dd><a href="mailto:{e(contact['email'])}">{e(contact['email'])}</a></dd></div>
    </dl>
  </div>
  <form class="site-form {reveal()}" id="contact-form" data-mailto="{e(contact['email'])}">
    <h2 class="h3-display">Send a message</h2>
    <div class="row-2">
      <div><label for="name">Name <span aria-hidden="true">*</span></label><input type="text" id="name" name="name" autocomplete="name" required></div>
      <div><label for="email">Email <span aria-hidden="true">*</span></label><input type="email" id="email" name="email" autocomplete="email" required></div>
    </div>
    <div class="row-2">
      <div><label for="phone">Phone</label><input type="tel" id="phone" name="phone" autocomplete="tel"></div>
      <div><label for="subject">Subject</label><input type="text" id="subject" name="subject"></div>
    </div>
    <div><label for="message">Message</label><textarea id="message" name="message" rows="6"></textarea></div>
    <button type="submit" class="btn btn-primary">Send message</button>
    <p class="form-status" id="form-status" role="status" aria-live="polite"></p>
  </form>
</div>""")
    page("contact.html", content, "Contact", f"Contact {site['name']} organizer {contact['name']} with questions about registration, camp or the competition.", "contact.html", body)


def build_registration(content):
    site = content["site"]
    pay = content["registrationPayment"]
    forms = content["registrationForms"]
    if forms:
        cards = "".join(
            f"""<li class="form-card {reveal()}">
      <div><h3>{e(f['name'])}</h3><p>{e(f.get('detail', ''))}</p></div>
      <a class="btn btn-primary" href="{e(f['href'])}" target="_blank" rel="noopener" download>Download {e(f.get('format', 'PDF'))}<span class="sr-only"> for {e(f['name'])}</span></a>
    </li>""" for f in forms
        )
        step1 = f'<ul class="form-cards">{cards}</ul><p class="small-note">Fees, levels and dances are listed on each form.</p>'
        step2 = "<p>Fill in every field on the form: leader and follower NDCA numbers, studio or coach, address, email and phone number. Then mark your dances and levels.</p>"
        pay_items = ""
        if pay.get("submitTo"):
            pay_items += f'<div><dt>Email your registration to</dt><dd><a href="mailto:{e(pay["submitTo"])}">{e(pay["submitTo"])}</a></dd></div>'
        if pay.get("payableTo"):
            pay_items += f'<div><dt>Checks payable to</dt><dd>{e(pay["payableTo"])}</dd></div>'
        if pay.get("mailTo"):
            pay_items += f'<div><dt>Mail checks to</dt><dd>{e(pay["mailTo"])}</dd></div>'
        if pay.get("zelle"):
            pay_items += f'<div><dt>Zelle</dt><dd>{e(pay["zelle"])}</dd></div>'
        step3 = f'<dl class="facts">{pay_items}</dl>' if pay_items else "<p>Submission and payment instructions will be posted here.</p>"
        steps = f"""
<ol class="reg-steps">
  <li class="{reveal()}"><div class="step-n" aria-hidden="true">1</div><div><h2>Choose your category</h2>{step1}</div></li>
  <li class="{reveal()}"><div class="step-n" aria-hidden="true">2</div><div><h2>Complete the form</h2>{step2}</div></li>
  <li class="{reveal()}"><div class="step-n" aria-hidden="true">3</div><div><h2>Submit and pay</h2>{step3}</div></li>
</ol>"""
        lede = "Choose your category, complete the form, then email it in with payment."
    else:
        steps = f"""
<div class="notice {reveal()}">
  <h2>2027 registration forms coming soon</h2>
  <p>The entry forms for {e(site['eventDateRange'])} will be published here, along with submission and payment instructions. Questions in the meantime? <a href="contact.html">Contact the organizer</a>.</p>
</div>"""
        lede = "Registration forms for 2027 are coming soon."
    prices = content["campPricing"]
    if any(p.get("href") for p in prices):
        blank = ' target="_blank" rel="noopener"'
        links = "".join(
            "<li>" + btn("Pay %s \u2014 %s" % (p["amount"], p["title"]), p["href"], "primary", True, blank) + "</li>"
            for p in prices if p.get("href")
        )
        camp_body = f'<p>Training Camp ({e(site["campDates"])}) is paid online. Choose one day or both days; details are on the <a href="camp.html">camp page</a>.</p><ul class="pay-list">{links}</ul>'
    else:
        camp_body = f'<p>Camp ({e(site["campDates"])}) registration details have not been announced yet. They will be posted on the <a href="camp.html">camp page</a>.</p>'
    camp_note = f"""
<div class="notice left {reveal()}"><h2 class="h3-display">Training Camp registration</h2>
{camp_body}</div>"""
    body = page_hero(e(site["eventDate"]), "Competition Registration", lede) + section(steps) \
        + section(camp_note + f'<p class="small-note center">Please review the <a href="rules-regulations.html">Rules &amp; Regulations</a> before you enter.</p>', "alt")
    page("registration.html", content, "Registration", f"Register for {site['name']} {site['eventDate']}: choose your category, complete the form, and follow the submission and payment instructions.", "registration.html", body)


def build_rules(content):
    site = content["site"]
    items = "".join(f"<li>{e(r)}</li>" for r in content["rules"])
    body = page_hero("Before you enter", "Rules &amp; Regulations", 'Please review before registering. Full NDCA rules are at <a href="http://www.ndca.org" target="_blank" rel="noopener">ndca.org</a>.') + section(f"""
<div class="rules-wrap">
  <p class="small-note">Entry fees and categories are listed on the 2027 registration forms.</p>
  <ol class="rules-list">{items}</ol>
</div>""")
    page("rules-regulations.html", content, "Rules & Regulations", f"Rules and regulations for {site['name']} 2027.", "rules-regulations.html", body)


def build_404(content):
    body = """
<section class="page-hero">
  <div class="container narrow-left">
    <p class="eyebrow">404</p>
    <h1>Page not found</h1>
    <p class="lede">The page you&rsquo;re looking for doesn&rsquo;t exist or has moved.</p>
    <div class="actions"><a class="btn btn-light" href="index.html">Back to home</a></div>
  </div>
</section>
"""
    page("404.html", content, "Page Not Found", "Page not found.", "", body)


def build_all():
    content = load_content()
    build_home(content)
    build_competition(content)
    build_about(content)
    build_partner_search(content)
    build_judges(content)
    build_vendors(content)
    build_hotel(content)
    build_prizes(content)
    build_schedule(content)
    build_camp(content)
    build_contact(content)
    build_registration(content)
    build_rules(content)
    build_404(content)
    return content


if __name__ == "__main__":
    build_all()
    print("Built all pages from data/content.json.")
