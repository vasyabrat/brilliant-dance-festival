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


def person_card(p, role_default=""):
    role = p.get("role") or role_default
    photo = f'<img src="{e(p["photo"])}" alt="{e(p["name"])}" loading="lazy" decoding="async">' if p.get("photo") else ""
    quote = f'<p class="quote">&ldquo;{e(p["quote"])}&rdquo;</p>' if p.get("quote") else ""
    role_html = f'<span class="role">{e(role)}</span>' if role else ""
    return f'<li class="person {reveal()}">{photo}<h3>{e(p["name"])}</h3>{role_html}{quote}</li>'


def people_list(people, role_default=""):
    return '<ul class="people">' + "".join(person_card(p, role_default) for p in people) + "</ul>"


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
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
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
    days = [
        (site["campStartISO"], "Training Camp", "Day 1", "camp"),
        (site["campEndISO"], "Training Camp", "Day 2", "camp"),
        (site["eventDateISO"], "Competition", "Competition day", "comp"),
    ]
    cards = ""
    for iso, kind, sub, cls in days:
        wd, month, num = day_parts(iso)
        href = "camp.html" if cls == "camp" else "competition.html"
        cards += f"""
    <li class="day {cls} {reveal()}">
      <p class="day-wd">{wd}</p>
      <p class="day-num"><span>{num}</span> {month}</p>
      <p class="day-kind">{kind}</p>
      <p class="day-sub">{sub}</p>
      <p class="day-note">Times to be confirmed</p>
      <a class="text-link" href="{href}">{'Camp details' if cls == 'camp' else 'Competition details'}{ARROW}</a>
    </li>"""
    return f'<ol class="days">{cards}</ol>'


# ---------------------------------------------------------------------------
# PAGES
# ---------------------------------------------------------------------------
def build_home(content):
    site = content["site"]
    forms = has_forms(content)
    hero_img = site_image(site, "hero", "Dancers at Brilliant Dance Festival", "(min-width: 900px) 46vw, 100vw")
    media = (
        f'<figure class="hero-photo {reveal("reveal-img")}">{hero_img}</figure>' if hero_img else
        f"""<div class="hero-year" aria-hidden="true"><span class="yr">2027</span><span class="yr-sub">January 8&ndash;10</span></div>"""
    )
    why = "".join(
        f'<li class="{reveal()}"><span class="num" aria-hidden="true">{i:02d}</span><div><h3>{e(w["title"])}</h3><p>{e(w["text"])}</p></div></li>'
        for i, w in enumerate(content["whyChooseUs"], 1)
    )
    details = f"""
<dl class="facts">
  <div><dt>Competition</dt><dd>{e(weekday(site['eventDateISO']))}, {e(site['eventDate'])}</dd></div>
  <div><dt>Training Camp</dt><dd>{e(weekday(site['campStartISO']))} &amp; {e(weekday(site['campEndISO']))}, {e(site['campDates'])}</dd></div>
  <div><dt>Entry types</dt><dd>{e(', '.join(f['name'] for f in content['registrationForms'])) if forms else 'Announced with registration'}</dd></div>
  <div><dt>Styles</dt><dd>International Ballroom, International Latin, American Smooth, American Rhythm</dd></div>
  <div><dt>Venue &amp; hotel</dt><dd>To be announced</dd></div>
  <div><dt>Judges &amp; officials</dt><dd>To be announced</dd></div>
</dl>"""
    steps = (
        """<ol class="steps">
  <li><h3>Choose your category</h3><p>Pick the entry form that matches how you dance.</p></li>
  <li><h3>Complete the form</h3><p>Fill in every field, then mark your dances and levels.</p></li>
  <li><h3>Submit and pay</h3><p>Email the form and send payment as listed on the registration page.</p></li>
</ol>""" if forms else
        '<p class="tba">2027 registration forms are coming soon. Registration details will appear here as soon as they are available.</p>'
    )
    body = f"""
<section class="hero">
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
    {media}
  </div>
</section>

{section(f'''
<div class="duo">
  <article class="path path-comp {reveal()}">
    <p class="path-kind">Competition</p>
    <h3>{e(site['eventDate'])}</h3>
    <p>A one-day competition in International Ballroom, International Latin, American Smooth and American Rhythm, for dancers from Minis through U21. Entries include solos, amateur couples and teacher/student.</p>
    {btn('Competition overview', 'competition.html', 'secondary')}
  </article>
  <article class="path path-camp {reveal()}">
    <p class="path-kind">Training Camp</p>
    <h3>{e(site['campDates'])}</h3>
    <p>Two days of training ahead of the competition: private lessons, lectures and practice rounds. Pricing, schedule and coaching faculty will be announced.</p>
    {btn('Camp information', 'camp.html', 'secondary')}
  </article>
</div>''', "", section_head("The weekend", "Two events, one festival", "Compete on Sunday, or train with coaches on Friday and Saturday. Dancers can take part in either or both.", "overview-title"), "overview-title")}

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

{section(three_days(content), "alt", section_head("Three days", "January 8&ndash;10 at a glance", "Camp runs Friday and Saturday; the competition is Sunday. Detailed times will be posted once confirmed.", "days-title"), "days-title")}

{section(f'''
<div class="info-split">
  <div class="{reveal()}">
    <h3 class="h3-display">Event details</h3>
    {details}
  </div>
  <div class="{reveal()}">
    <h3 class="h3-display">How registration works</h3>
    {steps}
    <p class="small-note">Please read the <a href="rules-regulations.html">Rules &amp; Regulations</a> before you enter.</p>
  </div>
</div>''', "", section_head("Plan your visit", "Event information", "", "info-title", "left"), "info-title")}

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
        "organizer": {"@type": "Person", "name": content["organizers"][0]["name"]} if content["organizers"] else None,
        "subEvent": [
            {"@type": "Event", "name": "Brilliant Ballroom Training Camp", "startDate": site["campStartISO"], "endDate": site["campEndISO"]},
            {"@type": "Event", "name": f"{site['name']} Competition", "startDate": site["eventDateISO"]},
        ],
    }
    event_ld = {k: v for k, v in event_ld.items() if v is not None}
    page("index.html", content, f"{site['name']} 2027 | Camp {site['campDates']} · Competition {site['eventDate']}",
         f"{site['name']} 2027: training camp {site['campDates']} and ballroom competition {site['eventDate']}. Registration, camp and event information.",
         "index.html", body, ld_json(event_ld) + "\n")


def build_competition(content):
    site = content["site"]
    forms = has_forms(content)
    cats = "".join(
        f'<li class="{reveal()}"><h3>{e(f["name"])}</h3><p>{e(f.get("detail", ""))}</p></li>' for f in content["registrationForms"]
    ) if forms else tba("Entry categories will be listed when the 2027 registration forms are published.")
    cats = f'<ul class="chips-list">{cats}</ul>' if forms else cats
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
      <div><dt>Styles</dt><dd>International Ballroom, International Latin, American Smooth, American Rhythm</dd></div>
      <div><dt>Age categories</dt><dd>Minis (3&ndash;5), TB (6&ndash;7), PT1 (8&ndash;9), PT2 (10&ndash;11), J1 (12&ndash;13), J2 (14&ndash;15), Youth (16&ndash;18), U21 (19&ndash;20)</dd></div>
      <div><dt>Rules</dt><dd>NDCA rules and regulations apply</dd></div>
      <div><dt>Venue</dt><dd>To be announced</dd></div>
    </dl>
  </div>
  <div class="{reveal()}">
    <h3 class="h3-display">Entry categories</h3>
    {cats}
    <p class="small-note">Fees, levels and dance lists are on each registration form.</p>
  </div>
</div>""", "", section_head("Details", "What to know before you enter", "", "comp-title", "left"), "comp-title") + section(f"""
<ul class="link-rows">
  <li class="{reveal()}"><a href="registration.html"><span><strong>Registration</strong><em>Forms, submission and payment</em></span>{ARROW}</a></li>
  <li class="{reveal()}"><a href="schedule.html"><span><strong>Schedule</strong><em>Event-day structure</em></span>{ARROW}</a></li>
  <li class="{reveal()}"><a href="judges.html"><span><strong>Judges &amp; Officials</strong><em>To be announced</em></span>{ARROW}</a></li>
  <li class="{reveal()}"><a href="prizes.html"><span><strong>Prizes</strong><em>To be announced</em></span>{ARROW}</a></li>
  <li class="{reveal()}"><a href="partner-search.html"><span><strong>Partner Search</strong><em>Dancers looking for a Latin partner</em></span>{ARROW}</a></li>
</ul>""", "alt", section_head("Explore", "More about the competition", "", "explore-title", "left"), "explore-title")
    page("competition.html", content, "Competition", f"Brilliant Dance Festival competition, {site['eventDate']}: styles, age categories, entry types and links to registration, schedule and rules.", "competition.html", body)


def build_about(content):
    site = content["site"]
    pillars = "".join(f"<li>{e(v)}</li>" for v in content["pillars"])
    why = "".join(
        f'<li class="{reveal()}"><span class="num" aria-hidden="true">{i:02d}</span><div><h3>{e(w["title"])}</h3><p>{e(w["text"])}</p></div></li>'
        for i, w in enumerate(content["whyChooseUs"], 1)
    )
    body = page_hero("About", "The future of dance starts here",
                     "We honor young dancers as future professionals, emphasizing respect and recognition throughout the entire competition experience.") \
        + section(organizer_block(content), "", "", "organizer-title") \
        + section(f"""
<div class="split-text">
  <div class="{reveal()}">
    <p class="eyebrow">Mission &amp; Vision</p>
    <h2 id="mission-title">Building the premier kids&rsquo; ballroom competition</h2>
  </div>
  <div class="{reveal()}">
    <p class="lead">We are committed to the next generation of ballroom dancers, aiming to create the premier kids&rsquo; ballroom competition in the United States, and ultimately a global event.</p>
    <p>{e(content['missionText'])}</p>
  </div>
</div>""", "alt", "", "mission-title") \
        + section(f'<ol class="why">{why}</ol>', "", section_head("What sets us apart", "How we run the festival", "", "apart-title", "left"), "apart-title") \
        + section(f'<ul class="values {reveal()}">{pillars}</ul>', "alt", section_head("Values", "What we stand for", "", "values-title"), "values-title")
    page("about.html", content, "About", f"About {site['name']}: our mission, and {content['organizers'][0]['name'] if content['organizers'] else 'our organizer'}, the organizer behind the festival.", "about.html", body)


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
    body = page_hero(e(site["eventDate"]), "Judges &amp; Officials", "The 2027 judging panel and officials will be published here once confirmed.") \
        + section(f"""
<div class="duo">
  <div class="panel {reveal()}"><h2 class="h3-display">Judging panel</h2>{j_html}</div>
  <div class="panel {reveal()}"><h2 class="h3-display">Officials</h2>{o_html}</div>
</div>""") \
        + section(organizer_block(content, compact=True), "alt", "", "organizer-title")
    page("judges.html", content, "Judges & Officials", f"Judges and officials for {site['name']} 2027, to be announced.", "judges.html", body)


def build_vendors(content):
    site = content["site"]
    vendors = "".join(
        f"""<li class="vendor {reveal()}"><h3>{e(v["name"])}</h3><p>{e(v["desc"])}</p><p>{'<a href="' + e(v["link"]) + '" target="_blank" rel="noopener">' + e(v["contact"]) + '</a>' if v.get("link") else e(v["contact"])}</p></li>"""
        for v in content["vendors"]
    )
    sponsors = "".join(
        f"""<li class="vendor {reveal()}"><h3>{e(s["name"])}</h3><p>{e(s["desc"])}</p><p>{e(s["contact"])}</p></li>""" for s in content["sponsors"]
    )
    v_html = f'<ul class="vendor-list">{vendors}</ul>' if vendors else tba("Vendors will be announced.")
    s_html = f'<ul class="vendor-list">{sponsors}</ul>' if sponsors else tba("Sponsors will be announced.")
    body = page_hero(e(site["eventDate"]), "Vendors &amp; Sponsors", f"Businesses and service providers supporting {e(site['name'])}.") \
        + section(f"""
<div class="duo">
  <div class="panel {reveal()}"><h2 class="h3-display">Vendors</h2>{v_html}</div>
  <div class="panel {reveal()}"><h2 class="h3-display">Sponsors</h2>{s_html}</div>
</div>
<p class="small-note center">Interested in being a vendor or sponsor? <a href="contact.html">Get in touch</a>.</p>""")
    page("vendors.html", content, "Vendors & Sponsors", f"Vendors and sponsors of {site['name']} 2027.", "vendors.html", body)


def build_hotel(content):
    site = content["site"]
    hotel = content["hotel"]
    if hotel.get("name"):
        blank = ' target="_blank" rel="noopener"'
        book = '<div class="actions">' + btn("Book the hotel", hotel["bookUrl"], "primary", True, blank) + "</div>" if hotel.get("bookUrl") else ""
        inner = f"""
<div class="notice {reveal()}">
  <h2>{e(hotel['name'])}</h2>
  <dl class="facts"><div><dt>Address</dt><dd>{e(hotel['address'])}</dd></div>
  <div><dt>Dates</dt><dd>Camp {e(site['campDates'])} &middot; Competition {e(site['eventDate'])}</dd></div></dl>
  {book}
</div>"""
    else:
        inner = f"""
<div class="notice {reveal()}">
  <h2>Hotel information coming soon</h2>
  <p>The 2027 hotel and any room-block details have not been confirmed yet. They will be posted here for {e(site['eventDateRange'])}. Questions? <a href="contact.html">Contact the organizer</a>.</p>
</div>"""
    body = page_hero("Where to stay", "Hotel", f"Training Camp {e(site['campDates'])} &middot; Competition {e(site['eventDate'])}") + section(inner)
    page("hotel.html", content, "Hotel", f"Hotel information for {site['name']} 2027, {site['eventDateRange']}.", "hotel.html", body)


def build_prizes(content):
    site = content["site"]
    tables = "".join(
        f"""<table class="prize-table {reveal()}"><caption>{e(t['title'])}</caption><tbody>{''.join(f'<tr><th scope="row">{e(a)}</th><td>{e(b)}</td></tr>' for a, b in t['rows'])}</tbody></table>"""
        for t in content["prizeTables"]
    )
    inner = f'<div class="duo">{tables}</div>' if tables else f'<div class="notice {reveal()}"><h2>Prize details coming soon</h2><p>Prizes and awards for 2027 have not been confirmed yet. They will be published here once they are. Questions? <a href="contact.html">Contact the organizer</a>.</p></div>'
    body = page_hero(e(site["eventDate"]), "Prizes &amp; Awards", "Awards recognizing the dedication and achievement of every participant.") + section(inner)
    page("prizes.html", content, "Prizes & Awards", f"Prizes and awards at {site['name']} 2027.", "prizes.html", body)


def build_schedule(content):
    site = content["site"]
    camp = "".join(f'<li><span>{e(s["label"])}</span><span class="time">{e(s["time"])}</span></li>' for s in content["campSchedule"])
    comp = "".join(f'<li><span>{e(s["label"])}</span><span class="time">{e(s["time"])}</span></li>' for s in content["homeSchedule"])
    tracks = "".join(
        f'<div class="panel {reveal()}"><h3 class="h3-display">{e(t["title"])}</h3><ul class="time-list">' +
        "".join(f'<li><span>{e(i["label"])}</span><span class="time">{e(i["time"])}</span></li>' for i in t["items"]) + "</ul></div>"
        for t in content["scheduleTracks"]
    )
    running = f'<div class="duo">{tracks}</div>' if tracks else tba("The preliminary running order will be posted closer to the event.")
    d = lambda iso: day_parts(iso)
    w1, m1, n1 = d(site["campStartISO"]); w2, m2, n2 = d(site["campEndISO"]); w3, m3, n3 = d(site["eventDateISO"])
    body = page_hero(e(site["eventDateRange"]), "Schedule", "Camp on Friday and Saturday, competition on Sunday. Times will be posted once confirmed.") + section(f"""
<div class="timeline">
  <div class="tl-day camp {reveal()}"><div class="tl-date"><span>{w1}</span><strong>{m1} {n1}</strong></div>
    <div class="tl-body"><h3>Training Camp &mdash; Day 1</h3><ul class="time-list">{camp}</ul></div></div>
  <div class="tl-day camp {reveal()}"><div class="tl-date"><span>{w2}</span><strong>{m2} {n2}</strong></div>
    <div class="tl-body"><h3>Training Camp &mdash; Day 2</h3><ul class="time-list">{camp}</ul></div></div>
  <div class="tl-day comp {reveal()}"><div class="tl-date"><span>{w3}</span><strong>{m3} {n3}</strong></div>
    <div class="tl-body"><h3>Competition</h3><ul class="time-list">{comp}</ul></div></div>
</div>
<p class="small-note">All times are to be confirmed and subject to change based on registration.</p>""", "", "") \
        + section(running, "alt", section_head("Competition day", "Preliminary running order", "", "run-title", "left"), "run-title")
    page("schedule.html", content, "Schedule", f"Schedule for {site['name']} 2027: camp {site['campDates']} and competition {site['eventDate']}.", "schedule.html", body)


def build_camp(content):
    site = content["site"]
    forms = has_forms(content)
    camp_items = "".join(f'<li><span>{e(s["label"])}</span><span class="time">{e(s["time"])}</span></li>' for s in content["campSchedule"])
    w1, m1, n1 = day_parts(site["campStartISO"]); w2, m2, n2 = day_parts(site["campEndISO"])
    pricing = "".join(
        f'<div class="price {reveal()}"><h3>{e(p["title"])}</h3><p class="amount">{e(p["amount"])}</p><p>{e(p["note"])}</p></div>' for p in content["campPricing"]
    )
    pricing_html = f'<div class="prices">{pricing}</div>' if pricing else tba("Camp pricing will be announced.")
    ball, latin = content["campCoaches"]["ballroom"], content["campCoaches"]["latin"]
    if ball or latin:
        coaches = (
            f'<div class="duo"><div class="panel"><h3 class="h3-display">Ballroom Coaches</h3>{people_list(ball, "Ballroom Coach") if ball else tba("Ballroom coaches to be announced.")}</div>'
            f'<div class="panel"><h3 class="h3-display">Latin Coaches</h3>{people_list(latin, "Latin Coach") if latin else tba("Latin coaches to be announced.")}</div></div>'
        )
    else:
        coaches = f'<div class="duo"><div class="panel {reveal()}"><h3 class="h3-display">Ballroom Coaches</h3>{tba("To be announced.")}</div><div class="panel {reveal()}"><h3 class="h3-display">Latin Coaches</h3>{tba("To be announced.")}</div></div>'
    status = (
        "Camp registration and pricing details have not been announced yet. They will be posted on this page."
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
      <div><dt>Format</dt><dd>Private lessons, lectures and practice rounds (details to be confirmed)</dd></div>
      <div><dt>Coaches</dt><dd>To be announced</dd></div>
      <div><dt>Registration</dt><dd>Details to be announced</dd></div>
    </dl>
  </div>
  <div class="{reveal()}">
    <div class="notice left"><h3 class="h3-display">Registration status</h3><p>{e(status)}</p>
      <p class="small-note">The 2027 forms currently available are for the competition. Questions about camp? <a href="contact.html">Contact the organizer</a>.</p></div>
    {'<figure class="photo-slot reveal reveal-img">' + img + '</figure>' if img else ''}
  </div>
</div>""", "", section_head("Overview", "Camp at Brilliant", "", "camp-title", "left"), "camp-title") \
        + section(f"""
<div class="duo">
  <div class="panel {reveal()}"><h3 class="h3-display">{w1}, {m1} {n1}</h3><p class="day-sub">Training Camp &mdash; Day 1</p><ul class="time-list">{camp_items}</ul></div>
  <div class="panel {reveal()}"><h3 class="h3-display">{w2}, {m2} {n2}</h3><p class="day-sub">Training Camp &mdash; Day 2</p><ul class="time-list">{camp_items}</ul></div>
</div>
<p class="small-note">Session details and times are to be confirmed for 2027.</p>""", "alt", section_head("Schedule", "Two days of training", "", "campdays-title", "left"), "campdays-title") \
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
    camp_note = f"""
<div class="notice left {reveal()}"><h2 class="h3-display">Training Camp registration</h2>
<p>Camp ({e(site['campDates'])}) registration details have not been announced yet. They will be posted on the <a href="camp.html">camp page</a>.</p></div>"""
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
