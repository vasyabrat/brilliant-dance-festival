#!/usr/bin/env python3
"""
Static site generator for the Brilliant Dance Festival site.

Run: python3 scripts/build.py
Regenerates every .html file in the project root from data/content.json.

This is the SAME generator the admin backend (server/app.py) calls after a
save, so editing content.json by hand and re-running this script has exactly
the same effect as editing through the admin dashboard at /admin.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_PATH = os.path.join(ROOT, "data", "content.json")

LOGO = "assets/logo.svg"

NAV = [
    ("Home", "index.html"),
    ("About", "about.html"),
    ("Partner Search", "partner-search.html"),
    ("Judges", "judges.html"),
    ("Vendors", "vendors.html"),
    ("Hotel", "hotel.html"),
    ("Prizes", "prizes.html"),
    ("Schedule", "schedule.html"),
    ("Camp", "camp.html"),
    ("Contact", "contact.html"),
]

SANCTION_LOGOS = [
    ("NDCA", "http://NDCA.org", "assets/logo-ndca.svg"),
    ("Fordney Foundation", "http://fordneyfoundation.org/", "assets/logo-fordney.svg"),
    ("Best of the Best Dancesport", "http://bestofthebestdancesport.com/", "assets/logo-botb.svg"),
]


def load_content():
    with open(CONTENT_PATH, "r") as f:
        return json.load(f)


def avatar(name, size=140):
    """Inline SVG placeholder avatar with initials — swap for a real photo any
    time by replacing the generated <img>/<svg> in the HTML."""
    initials = "".join([p[0].upper() for p in name.split() if p])[:2]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}" '
        f'role="img" aria-label="{name}">'
        f'<rect width="100" height="100" fill="#15224b"/>'
        f'<text x="50" y="58" font-family="Georgia, serif" font-size="34" fill="#ffffff" '
        f'text-anchor="middle">{initials}</text></svg>'
    )


def person_card(name, role="", quote=""):
    svg = avatar(name)
    quote_html = f'<p class="quote">&ldquo;{quote}&rdquo;</p>' if quote else ""
    role_html = f'<span class="role">{role}</span>' if role else ""
    return f"""
    <div class="person">
      <div class="photo">{svg}</div>
      <h4>{name}</h4>
      {role_html}
      {quote_html}
    </div>"""


def head(site_name, title, description):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | {site_name}</title>
<meta name="description" content="{description}">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="stylesheet" href="css/style.css">
</head>
<body>
"""


def header_html(content, active_href):
    site = content["site"]
    links = []
    for label, href in NAV:
        cls = ' class="active"' if href == active_href else ""
        links.append(f'<li><a href="{href}"{cls}>{label}</a></li>')
    links_html = "\n          ".join(links)
    return f"""
<div class="topbar">
  <div class="container">
    <span class="event-date">Tournament date: {site['eventDate']}</span>
    <div class="quick-links">
      <a href="{site['heatListUrl']}" target="_blank" rel="noopener">Heat List</a>
      <a href="{site['scoreSheetsUrl']}" target="_blank" rel="noopener">Score Sheets</a>
      <a href="registration.html">Register</a>
    </div>
  </div>
</div>
<header class="site-header">
  <div class="container nav-wrap">
    <a class="brand" href="index.html" aria-label="{site['name']} home">
      <img src="{LOGO}" alt="{site['name']} logo">
    </a>
    <nav class="main-nav">
      <ul>
          {links_html}
      </ul>
    </nav>
    <div class="nav-cta">
      <a class="btn btn-outline" href="registration.html">Register</a>
      <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false">&#9776;</button>
    </div>
  </div>
</header>
"""


def footer_html(content):
    site = content["site"]
    nav_items = "\n        ".join([f'<li><a href="{href}">{label}</a></li>' for label, href in NAV])
    sanction = "\n        ".join(
        [f'<a href="{url}" target="_blank" rel="noopener"><img src="{logo}" alt="{name}"></a>' for name, url, logo in SANCTION_LOGOS]
    )
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="brand-block">
        <img src="{LOGO}" alt="{site['name']} logo">
        <p>{site['name']} is a leading junior ballroom competition that celebrates young dancers, offering professional judging, generous awards, and a platform for future stars to shine.</p>
        <div class="social">
          <a href="{site['instagram']}" target="_blank" rel="noopener">Instagram &#8599;</a>
        </div>
      </div>
      <div>
        <h4>Explore</h4>
        <ul>
        {nav_items}
        </ul>
      </div>
      <div>
        <h4>Resources</h4>
        <ul>
          <li><a href="rules-regulations.html">Rules &amp; Regulations</a></li>
          <li><a href="{site['heatListUrl']}" target="_blank" rel="noopener">Heat List</a></li>
          <li><a href="{site['scoreSheetsUrl']}" target="_blank" rel="noopener">Score Sheets</a></li>
          <li><a href="registration.html">Registration</a></li>
        </ul>
      </div>
    </div>
    <div class="sanction-logos">
      {sanction}
    </div>
    <div class="bottom-bar">
      <span>Copyright &copy; 2026 {site['name']}</span>
      <span><a href="/admin">Admin</a></span>
    </div>
  </div>
</footer>
<script src="js/main.js"></script>
</body>
</html>
"""


def page(filename, site_name, title, description, active_href, body, content):
    with open(os.path.join(ROOT, filename), "w") as f:
        f.write(head(site_name, title, description))
        f.write(header_html(content, active_href))
        f.write(body)
        f.write(footer_html(content))


# ---------------------------------------------------------------------------
# PAGES
# ---------------------------------------------------------------------------

def build_home(content):
    site = content["site"]
    judges = "".join([person_card(j["name"], j["role"], j.get("quote", "")) for j in content["homeFeaturedJudges"]])
    pillars = "".join(f'<span class="pill">{v}</span>' for v in content["pillars"])
    organizer = content["organizers"][0] if content["organizers"] else {"name": "", "bio": ""}
    home_schedule = "".join(
        f'<li><span>{s["label"]}</span><span class="time">{s["time"]}</span></li>' for s in content["homeSchedule"]
    )
    top_studio = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in content["homePrizes"]["topStudio"])
    top_teacher = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in content["homePrizes"]["topTeacher"])
    organizer_names = " &amp; ".join(o["name"] for o in content["organizers"]) or "the Organizers"

    body = f"""
<section class="hero">
  <div class="container hero-grid">
    <div>
      <span class="eyebrow">{site['name']}</span>
      <h1>{content['hero']['title']}</h1>
      <p class="lede">{content['hero']['lede']}</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="camp.html">Camp</a>
        <a class="btn btn-outline" href="registration.html">Register</a>
      </div>
    </div>
    <div class="hero-visual">{site['name']}</div>
  </div>
</section>

<div class="pill-bar">
  <div class="container" style="justify-content:center;gap:16px;">
    <a class="btn btn-outline" style="border-color:#fff;color:#fff;" href="{site['heatListUrl']}" target="_blank" rel="noopener">Score Sheets</a>
    <a class="btn btn-outline" style="border-color:#fff;color:#fff;" href="judges.html">Lineup Photos</a>
  </div>
</div>

<section>
  <div class="container">
    <div class="section-head">
      <h2>Values We Offer!</h2>
    </div>
    <div class="pill-list">
      {pillars}
    </div>
  </div>
</section>

<section>
  <div class="container two-col">
    <div>
      <div class="photo" style="width:220px;">{avatar(organizer.get("name", "Organizer"), 220)}</div>
    </div>
    <div>
      <span class="eyebrow">Mission &amp; Vision</span>
      <h2>Our Mission &amp; Vision</h2>
      <p>{content['missionText']}</p>
      <p class="signature">{organizer.get("name", "")}</p>
      <span class="signature-label">{organizer.get("role", "Organizer")}</span>
      <div style="margin-top:20px;">
        <a class="btn btn-primary" href="about.html">More About Us!</a>
      </div>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Why Choose Us</span>
      <h2>Why Choose Us!</h2>
    </div>
    <div class="grid grid-4">
      {"".join(f'<div class="card"><h3>{w["title"]}</h3><p>{w["text"]}</p></div>' for w in content["whyChooseUs"])}
    </div>
  </div>
</section>

<section>
  <div class="container two-col">
    <div>
      <span class="eyebrow">{site['eventDate']}</span>
      <h2>Schedule of Events</h2>
      <p>Final schedule will be posted the week of the event and is subject to change based on registration.</p>
      <ul class="schedule-list">
        {home_schedule}
      </ul>
      <div style="margin-top:26px;">
        <a class="btn btn-outline" href="schedule.html">See All The Event Schedules</a>
      </div>
    </div>
    <div>
      <div class="hero-visual" style="min-height:280px;">Ballroom Competition</div>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Awards</span>
      <h2>Awards &amp; Prizes</h2>
      <p>Compete for top honors with generous cash prizes for studios, teachers, and the prestigious Fordney Foundation Championship.</p>
    </div>
    <div class="grid grid-2">
      <table class="prize-table">
        <thead><tr><th colspan="2">Top Studio</th></tr></thead>
        <tbody>{top_studio}</tbody>
      </table>
      <table class="prize-table">
        <thead><tr><th colspan="2">Top Teacher</th></tr></thead>
        <tbody>{top_teacher}</tbody>
      </table>
    </div>
    <div class="text-center" style="margin-top:30px;">
      <a class="btn btn-outline" style="border-color:#fff;color:#fff;" href="prizes.html">See All Prize Categories</a>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Meet The Panel</span>
      <h2>Judges</h2>
    </div>
    <div class="people-grid">
      {judges}
    </div>
    <div class="text-center" style="margin-top:30px;">
      <a class="btn btn-outline" href="judges.html">Meet All Judges &amp; Officials</a>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Thank You</span>
      <h2>Our Vendors</h2>
    </div>
    <div class="text-center">
      <a class="btn btn-outline" href="vendors.html">See All Vendors &amp; Sponsors</a>
    </div>
  </div>
</section>
"""
    page("index.html", site["name"], "Home", f"{site['name']} — celebrating the next generation of ballroom dance stars. Junior ballroom competition, {site['eventDate']}.", "index.html", body, content)


def build_about(content):
    site = content["site"]
    judges = "".join([person_card(j["name"], j["role"], j.get("quote", "")) for j in content["judgingPanel"]])
    organizers_html = "".join(person_card(o["name"], o["role"], o.get("bio", "")) for o in content["organizers"])
    organizer_names = ", ".join(o["name"] for o in content["organizers"]) or "our organizers"
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">About Us</span>
    <h1>The Future of Dance Starts&hellip; HERE!</h1>
    <p class="lede">We honor young dancers as future professionals, emphasizing respect and recognition throughout the entire competition experience.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Leadership</span>
      <h2>Meet the Team Behind {site['name']}</h2>
    </div>
    <div class="people-grid" style="max-width:560px;margin:0 auto;">
      {organizers_html}
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="container text-center">
    <span class="eyebrow">Mission &amp; Vision</span>
    <h2>Building the Premier Kids&rsquo; Ballroom Competition</h2>
    <p style="max-width:680px;margin:0 auto;">We are committed to the next generation of ballroom dancers, aiming to create the premier kids&rsquo; ballroom competition in the United States, and ultimately a global event.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Why Choose Us</span>
      <h2>What Sets Us Apart</h2>
    </div>
    <div class="grid grid-4">
      {"".join(f'<div class="card"><h3>{w["title"]}</h3><p>{w["text"]}</p></div>' for w in content["whyChooseUs"])}
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Officials</span>
      <h2>Judge Profiles</h2>
    </div>
    <div class="people-grid">{judges}</div>
  </div>
</section>
"""
    page("about.html", site["name"], "About", f"About {site['name']} — our mission, organized by {organizer_names}, and what makes us unique.", "about.html", body, content)


def build_partner_search(content):
    site = content["site"]
    cards = "".join(f"""
      <div class="card">
        <div class="photo" style="width:120px;margin-bottom:18px;">{avatar(p["name"], 120)}</div>
        <h3>{p["name"]}</h3>
        <p><strong>Level:</strong> {p["level"]}<br>
        <strong>Studio:</strong> {p["studio"]}<br>
        <strong>Coaches:</strong> {p["coaches"]}<br>
        <strong>Contact:</strong> {p["contact"]}</p>
        <p>{p["note"]}</p>
      </div>""" for p in content["partnerSearch"])
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">Latin Only</span>
    <h1>Partner Search</h1>
    <p class="lede">Dancers currently looking for a Latin partner ahead of {site['eventDate']}.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="grid grid-2">{cards}</div>
    <p class="text-center" style="margin-top:40px;">Want to be listed here? Submit the <a href="registration.html">Partner Search Announcement Form</a> on the registration page.</p>
  </div>
</section>
"""
    page("partner-search.html", site["name"], "Partner Search", f"{site['name']} partner search — Latin partner listings for upcoming junior ballroom dancers.", "partner-search.html", body, content)


def build_judges(content):
    site = content["site"]
    officials = "".join([person_card(o["name"], o["role"]) for o in content["officials"]])
    judges_html = "".join([person_card(o["name"], o["role"], o.get("bio", "")) for o in content["organizers"]])
    judges_html += "".join([person_card(j["name"], j["role"], j.get("quote", "")) for j in content["judgingPanel"]])
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{site['eventDate']}</span>
    <h1>Judges &amp; Officials</h1>
    <p class="lede">A panel of renowned experts bringing experience, fairness, and valuable feedback to every performance!</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head"><h2>Judging Panel</h2></div>
    <div class="people-grid">{judges_html}</div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head"><h2>Officials</h2></div>
    <div class="people-grid">{officials}</div>
  </div>
</section>
"""
    page("judges.html", site["name"], "Judges & Officials", f"Meet the judging panel and officials of {site['name']}.", "judges.html", body, content)


def build_vendors(content):
    site = content["site"]
    vendor_html = "".join(
        f"""<div class="vendor-item"><h4>{v["name"]}</h4><p>{v["desc"]}</p><p>{'<a class="ext" href="'+v["link"]+'" target="_blank" rel="noopener">'+v["contact"]+'</a>' if v.get("link") else v["contact"]}</p></div>"""
        for v in content["vendors"]
    )
    sponsor_html = "".join(
        f"""<div class="vendor-item"><h4>{s["name"]}</h4><p>{s["desc"]}</p><p>{s["contact"]}</p></div>"""
        for s in content["sponsors"]
    )
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{site['eventDate']}</span>
    <h1>Our Vendors</h1>
    <p class="lede">Businesses and service providers supporting {site['name']}.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head"><h2>Beauty, Styling &amp; Photography</h2></div>
    <div class="vendor-list">{vendor_html}</div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head"><h2>Sponsors</h2></div>
    <div class="vendor-list">{sponsor_html}</div>
  </div>
</section>
"""
    page("vendors.html", site["name"], "Vendors", f"Vendors and sponsors of {site['name']}.", "vendors.html", body, content)


def build_hotel(content):
    site = content["site"]
    hotel = content["hotel"]
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">Where To Stay</span>
    <h1>Hotel</h1>
    <p class="lede">Camp {site['campDates']} &middot; Festival {site['eventDate']}</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="info-card text-center">
      <h3>{hotel['name']}</h3>
      <span class="label">Address</span>
      <span class="value">{hotel['address']}</span>
      <span class="label">Dates</span>
      <span class="value">Camp {site['campDates']} &middot; Festival {site['eventDate']}</span>
      <div style="margin-top:26px;">
        <a class="btn btn-primary" href="{hotel['bookUrl']}" target="_blank" rel="noopener">Book The Hotel</a>
      </div>
    </div>
  </div>
</section>
"""
    page("hotel.html", site["name"], "Hotel", f"Official hotel for {site['name']} — {hotel['name']}.", "hotel.html", body, content)


def build_prizes(content):
    site = content["site"]
    tables = "".join(
        f"""<table class="prize-table"><thead><tr><th colspan="2">{t['title']}</th></tr></thead><tbody>{''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in t['rows'])}</tbody></table>"""
        for t in content["prizeTables"]
    )
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{site['eventDate']}</span>
    <h1>Prizes</h1>
    <p class="lede">Generous awards celebrating the dedication and achievement of every participant.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="grid grid-2">{tables}</div>
  </div>
</section>
"""
    page("prizes.html", site["name"], "Prizes", f"Prize money and awards at {site['name']}.", "prizes.html", body, content)


def build_schedule(content):
    site = content["site"]
    home_schedule = "".join(
        f'<li><span>{s["label"]}</span><span class="time">{s["time"]}</span></li>' for s in content["homeSchedule"]
    )
    tracks = "".join(f"""
      <div class="card">
        <h3>{t['title']}</h3>
        <ul class="schedule-list">
          {"".join(f'<li><span>{i["label"]}</span><span class="time">{i["time"]}</span></li>' for i in t['items'])}
        </ul>
      </div>""" for t in content["scheduleTracks"])
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{site['eventDate']}</span>
    <h1>Schedule</h1>
    <p class="lede">Final schedule will be posted the week of the event and is subject to change based on registration.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head"><h2>Day Overview</h2></div>
    <ul class="schedule-list">{home_schedule}</ul>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head"><h2>Preliminary Running Order</h2></div>
    <div class="grid grid-2">{tracks}</div>
    <p class="text-center" style="margin-top:30px;color:rgba(255,255,255,0.6);">This is a preliminary outline. Check the official <a href="{site['heatListUrl']}" target="_blank" rel="noopener" style="color:#8fa0e0;">Heat List</a> the week of the event for exact timing.</p>
  </div>
</section>
"""
    page("schedule.html", site["name"], "Schedule", f"Event day schedule for {site['name']}, {site['eventDate']}.", "schedule.html", body, content)


def build_camp(content):
    site = content["site"]
    standard = "".join([person_card(c["name"], "Standard Coach", c.get("quote", "")) for c in content["campCoaches"]["standard"]])
    latin = "".join([person_card(c["name"], "Latin Coach", c.get("quote", "")) for c in content["campCoaches"]["latin"]])
    camp_schedule = "".join(f'<li><span>{s["label"]}</span><span class="time">{s["time"]}</span></li>' for s in content["campSchedule"])
    pricing = "".join(
        f'<div class="price-card"><h3>{p["title"]}</h3><div class="amount">{p["amount"]}</div><p>{p["note"]}</p><a class="btn btn-primary" href="registration.html">Buy Now</a></div>'
        for p in content["campPricing"]
    )
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{site['campDates']}</span>
    <h1>Brilliant Ballroom Training Camp</h1>
    <p class="lede">Private lessons, lectures, and practice rounds with a world-class coaching faculty, ahead of the {site['eventDate']} festival.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head"><h2>Daily Schedule</h2></div>
    <ul class="schedule-list">{camp_schedule}</ul>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head"><h2>Pricing</h2></div>
    <div class="price-cards">{pricing}</div>
    <p class="text-center" style="margin-top:26px;"><a class="btn btn-outline" style="border-color:#fff;color:#fff;" href="registration.html">Request Specific Lessons</a></p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head"><h2>Standard Division Coaches</h2></div>
    <div class="people-grid">{standard}</div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head"><h2>Latin Division Coaches</h2></div>
    <div class="people-grid">{latin}</div>
  </div>
</section>
"""
    page("camp.html", site["name"], "Camp", f"Brilliant Ballroom Training Camp — private lessons and lectures ahead of {site['name']}.", "camp.html", body, content)


def build_contact(content):
    site = content["site"]
    contact = content["contact"]
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">Get In Touch</span>
    <h1>Contact</h1>
  </div>
</section>

<section>
  <div class="container two-col">
    <div class="info-card">
      <div class="photo" style="width:110px;margin-bottom:16px;">{avatar(contact['name'], 110)}</div>
      <h3>{contact['name']}</h3>
      <span class="label">{contact['role']}</span>
      <span class="label">Phone</span>
      <span class="value"><a href="tel:{contact['phone'].replace('-', '')}">{contact['phone']}</a></span>
      <span class="label">Email</span>
      <span class="value"><a href="mailto:{contact['email']}">{contact['email']}</a></span>
    </div>
    <div>
      <form class="site-form" id="contact-form">
        <div class="row-2">
          <div>
            <label for="name">Name *</label>
            <input type="text" id="name" name="name" required>
          </div>
          <div>
            <label for="email">Email *</label>
            <input type="email" id="email" name="email" required>
          </div>
        </div>
        <div>
          <label for="phone">Phone Number</label>
          <input type="tel" id="phone" name="phone">
        </div>
        <div>
          <label for="subject">Subject</label>
          <input type="text" id="subject" name="subject">
        </div>
        <div>
          <label for="message">Message</label>
          <textarea id="message" name="message"></textarea>
        </div>
        <button type="submit" class="btn btn-primary">Send Message</button>
        <p class="form-status" id="form-status"></p>
      </form>
    </div>
  </div>
</section>
"""
    page("contact.html", site["name"], "Contact", f"Contact {site['name']} organizer {contact['name']}.", "contact.html", body, content)


def build_registration(content):
    site = content["site"]
    payment = content["registrationPayment"]
    doc_list = "".join(
        f'<li><span>{f["name"]}</span><a class="dl" href="{f["href"]}" download>Download PDF</a></li>' for f in content["registrationForms"]
    )
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{site['eventDate']}</span>
    <h1>Registration</h1>
    <p class="lede">Download the form you need, complete it, and mail it in with payment.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="info-card text-center" style="max-width:640px;">
      <h3>Payment</h3>
      <p>Make checks / money orders payable to: <strong>{payment['payableTo']}</strong><br>
      Mail to: {payment['mailTo']}</p>
      <p>Or pay via Zelle to <strong>{payment['zelle']}</strong></p>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head"><h2>Registration Forms</h2></div>
    <ul class="doc-list">{doc_list}</ul>
  </div>
</section>
"""
    page("registration.html", site["name"], "Registration", f"Register for {site['name']} — download entry forms and payment instructions.", "registration.html", body, content)


def build_rules(content):
    site = content["site"]
    items = "".join(f"<li>{r}</li>" for r in content["rules"])
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{site['eventDate']}</span>
    <h1>Rules &amp; Regulations</h1>
    <p class="lede">Please review before registering. Full NDCA rules at <a href="http://www.ndca.org" target="_blank" rel="noopener" style="color:#8fa0e0;">ndca.org</a>.</p>
  </div>
</section>

<section>
  <div class="container">
    <ol class="rules-list">{items}</ol>
  </div>
</section>
"""
    page("rules-regulations.html", site["name"], "Rules & Regulations", f"Official rules and regulations for {site['name']}.", "rules-regulations.html", body, content)


def build_404(content):
    site = content["site"]
    body = """
<section class="hero small">
  <div class="container">
    <h1>Page Not Found</h1>
    <p class="lede">The page you're looking for doesn't exist.</p>
    <a class="btn btn-primary" href="index.html">Back To Home</a>
  </div>
</section>
"""
    page("404.html", site["name"], "Page Not Found", "Page not found.", "", body, content)


def build_all():
    content = load_content()
    build_home(content)
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
