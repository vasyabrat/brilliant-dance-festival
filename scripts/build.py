#!/usr/bin/env python3
"""
Static site generator for the Brilliant Dance Festival rebuild.

Run: python3 scripts/build.py
Regenerates every .html file in the project root from the templates below.
Edit CONTENT / PEOPLE / page functions in this file, then re-run, OR just
hand-edit the generated .html files directly — both are plain, dependency-free
HTML/CSS/JS so either workflow works.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_NAME = "Brilliant Dance Festival"
EVENT_DATE = "January 11th, 2026"
LOGO = "assets/logo.svg"
INSTAGRAM = "https://www.instagram.com/brilliant.dance.festival"
HEAT_LIST = "https://www.comp-mngr.com/brilliant2026/Brilliant2026_HeatLists.htm"
SCORE_SHEETS = "http://www.comp-mngr.com/brilliant2026/Brilliant2026_ScoresheetsByPerson.htm"

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


def avatar(name, size=140):
    """Generate an inline SVG placeholder avatar with initials, so no
    mismatched/unverified photos of real people are used. Swap the <img>
    this produces for a real headshot any time — see /assets/README.md."""
    initials = "".join([p[0].upper() for p in name.split() if p])[:2]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}" '
        f'role="img" aria-label="{name}">'
        f'<rect width="100" height="100" fill="#201c24"/>'
        f'<text x="50" y="58" font-family="Georgia, serif" font-size="34" fill="#cfa15c" '
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


def head(title, description):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | {SITE_NAME}</title>
<meta name="description" content="{description}">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="stylesheet" href="css/style.css">
</head>
<body>
"""


def header_html(active_href):
    links = []
    for label, href in NAV:
        cls = ' class="active"' if href == active_href else ""
        links.append(f'<li><a href="{href}"{cls}>{label}</a></li>')
    links_html = "\n          ".join(links)
    return f"""
<div class="topbar">
  <div class="container">
    <span class="event-date">{EVENT_DATE}</span>
    <div class="quick-links">
      <a href="{HEAT_LIST}" target="_blank" rel="noopener">Heat List</a>
      <a href="{SCORE_SHEETS}" target="_blank" rel="noopener">Score Sheets</a>
      <a href="registration.html">Register</a>
    </div>
  </div>
</div>
<header class="site-header">
  <div class="container nav-wrap">
    <a class="brand" href="index.html" aria-label="{SITE_NAME} home">
      <img src="{LOGO}" alt="{SITE_NAME} logo">
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


def footer_html():
    nav_items = "\n        ".join([f'<li><a href="{href}">{label}</a></li>' for label, href in NAV])
    sanction = "\n        ".join(
        [f'<a href="{url}" target="_blank" rel="noopener"><img src="{logo}" alt="{name}"></a>' for name, url, logo in SANCTION_LOGOS]
    )
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="brand-block">
        <img src="{LOGO}" alt="{SITE_NAME} logo">
        <p>Brilliant Dance Festival is a leading junior ballroom competition that celebrates young dancers, offering professional judging, generous awards, and a platform for future stars to shine.</p>
        <div class="social">
          <a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram &#8599;</a>
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
          <li><a href="{HEAT_LIST}" target="_blank" rel="noopener">Heat List</a></li>
          <li><a href="{SCORE_SHEETS}" target="_blank" rel="noopener">Score Sheets</a></li>
          <li><a href="registration.html">Registration</a></li>
        </ul>
      </div>
    </div>
    <div class="sanction-logos">
      {sanction}
    </div>
    <div class="bottom-bar">
      <span>Copyright &copy; 2026 {SITE_NAME}</span>
      <span>Rebuilt static site &mdash; edit freely.</span>
    </div>
  </div>
</footer>
<script src="js/main.js"></script>
</body>
</html>
"""


def page(filename, title, description, active_href, body):
    with open(os.path.join(ROOT, filename), "w") as f:
        f.write(head(title, description))
        f.write(header_html(active_href))
        f.write(body)
        f.write(footer_html())


# ---------------------------------------------------------------------------
# JUDGES data (shared between homepage teaser, about page, judges page)
# ---------------------------------------------------------------------------
FEATURED_JUDGES = [
    ("Vince Bailey", "Master of Ceremonies", ""),
    ("Sasha Nissengolts", "Judge", "Prioritizes attention to detail, preparation, fundamental understanding, and musical commitment."),
    ("Kiki Nyemchek", "Judge", "Looks for artistry, athleticism, technique, passion, and competitive spirit."),
    ("Jason Dai", "Judge", "Emphasizes attitude and dedication as paramount qualities."),
]

ALL_JUDGES = [
    ("Nina Estrina", "Organizer", "Focuses on creating an appreciative atmosphere for dancers and coaches."),
    ("Taysiya Andryeyeva", "Organizer", "Emphasizes inspiration, joy, and connection beyond competition."),
    ("Darina Jeleva", "Chairman", "I look for the beauty of coordination between two bodies and within the body."),
    ("Oleg Gorbatso", "Judge", "Values musicality, synchronization, and personality."),
    ("Sasha Nissengolts", "Judge", "Prioritizes attention to detail, preparation, fundamental understanding, and musical commitment."),
    ("Eric Groysman", "Judge", "Seeks technical accuracy combined with authentic expression."),
    ("Max Firestein", "Judge", "Values mechanics, musicality, partnering, and performance balance."),
    ("Liliya Furman", "Judge", "Emphasizes rhythm reflection, partnering skills, and classic figures."),
    ("Kiki Nyemchek", "Judge", "Looks for artistry, athleticism, technique, passion, and competitive spirit."),
    ("Jason Dai", "Judge", "Emphasizes attitude and dedication as paramount qualities."),
    ("Dakota Pizzi", "Judge", "Values posture, lines, athleticism, precision, and uniqueness."),
    ("Artem Kuklin", "Judge", "Prioritizes performance stability and clarity of body lines."),
    ("Yulia Samarskaya", "Judge", "Focuses on musicality and stability of the dancing pair."),
    ("Masha Kozobrod", "Judge", "Seeks balance between artistic and technical skills with genuine enjoyment."),
    ("Rita Algarra-Gekhman", "Judge", "Concentrates on movement quality."),
    ("Denys Drozdyuk", "Judge", "Values sincere enthusiasm, musicality, and individuality."),
    ("Szymon Kalinowski", "Judge", "Emphasizes balance between technique and expression."),
    ("Marek Kosaty", "Judge", "Technique empowers dancers to reveal their true selves."),
    ("Ilana Keselman", "Judge", "Seeks harmony of beauty, quality, and belief."),
    ("Darren Hammond & Marina Steshenko", "Judges", "Look for passion and the special spark that makes dancers unforgettable."),
    ("Aigars Stolcers", "Judge", ""),
    ("Maria Manusova", "Judge", ""),
    ("Erik Heer", "Judge", ""),
    ("Oleksandra Vereshchak", "Judge", "Emphasizes posture, musicality, footwork, and weight transfer."),
    ("Polina Skaskiv", "Judge", "Values personality expressed through high-quality movement."),
    ("Dennis Donskoi", "Judge", ""),
    ("Anna Oblakova", "Judge", "Looks for character expression, posture, footwork, and partnering skills."),
    ("Paul Ru", "Judge", ""),
    ("Georgi Kanev", "Judge", "Comprehensive perspective on artistry, technique, leadership, femininity, and overall presentation."),
    ("Valeria Bushueva", "Judge", "Values quality and couple interaction."),
]

OFFICIALS = [
    ("Vince Bailey", "Master of Ceremonies"),
    ("Michelle Friedman", "Music Director"),
    ("Nina Mayster", "Deck Captain"),
    ("Marie Robers", "Scrutineer"),
    ("Marielle Pabon", "Registrar"),
]

STANDARD_COACHES = [
    ("Szymon Kalinowski", "Emphasizes a natural look combined with the full use of fundamental principles."),
    ("Marek Kosaty", "Focuses on technique that empowers authentic dancer expression."),
    ("Artem Kuklin", "Prioritizes stability of the performance from beginning to end."),
    ("Rita Algarra-Gekhman", "Seeks the best quality of movement."),
    ("Dennis Donskoi", ""),
]

LATIN_COACHES = [
    ("Oleg Gorbatso", ""),
    ("Nina Estrina", ""),
    ("Taysiya Andryeyeva", ""),
    ("Darren Hammond & Marina Steshenko", "Seeks passion, enthusiasm and personality shining through &mdash; that special spark."),
    ("Kiki Nyemchek", "Values a strong sense of artistry and athleticism."),
    ("Aigars Stolcers", ""),
    ("Maria Manusova", ""),
]

VENDORS = [
    ("Lux Beauty", "Beauty services", "201-306-4550 &middot; luxbeautystudio2024@gmail.com", None),
    ("Glam By AK", "Beauty services", "Instagram", "https://instagram.com"),
    ("Girls Muah", "Cosmetics &amp; beauty", "Instagram", "https://instagram.com"),
    ("Nadezda Vlasova", "Professional beauty services", "Instagram", "https://instagram.com"),
    ("Brilliant Dance Boutique", "Dance apparel", "Instagram", "https://instagram.com"),
    ("NZM Dance Photography", "Event photography &mdash; booking for BDF via Google Form", "Instagram", "https://instagram.com"),
]

SPONSORS = [
    ("InnovaRx", "Healthcare", "innovarxhealth.com"),
    ("Bristol Auto Mall", "Vehicle dealer", "(215) 486-5002"),
    ("GE Insurance", "Insurance services", "(215) 421-4555"),
    ("Kidology Inc", "Services", "215-330-4116"),
    ("Vyz Law", "Legal services", "215-969-3004"),
]

# ---------------------------------------------------------------------------
# PAGES
# ---------------------------------------------------------------------------

def build_home():
    judges = "".join([person_card(n, r, q) for n, r, q in FEATURED_JUDGES])
    body = f"""
<section class="hero">
  <div class="container">
    <span class="eyebrow">{EVENT_DATE}</span>
    <h1>Brilliant Dance Festival</h1>
    <p class="lede">Celebrating the Next Generation of Ballroom Dance Stars. A professional-grade platform inviting talented young dancers to compete with skill, passion, and dedication.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="camp.html">Camp</a>
      <a class="btn btn-light" href="registration.html">Register</a>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">What We Stand For</span>
      <h2>Eight Pillars of Brilliant Dance Festival</h2>
    </div>
    <div class="pill-list">
      {"".join(f'<span class="pill">{v}</span>' for v in ["Inspiration","Professional Recognition","Dedication","Commitment","Professionalism","Unique &amp; Memorable","Fearlessness","Positive Impact"])}
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="container two-col">
    <div>
      <div class="photo" style="width:220px;">{avatar("Nina Estrina", 220)}</div>
    </div>
    <div>
      <span class="eyebrow">Mission &amp; Vision</span>
      <h2>Led by Nina Estrina, Organizer</h2>
      <p>Brilliant Dance Festival recognizes young ballroom dancer talent with professionalism and respect, positioning the event as a leading competition for aspiring professionals.</p>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Why Choose Us</span>
      <h2>A Professional-Grade Experience</h2>
    </div>
    <div class="grid grid-4">
      <div class="card"><h3>Professional Recognition</h3><p>We honor young dancers with the respect they deserve, offering a professional-grade competition experience.</p></div>
      <div class="card"><h3>Top-Tier Judges</h3><p>Our experienced judges provide expert feedback, ensuring fairness and high standards.</p></div>
      <div class="card"><h3>Exceptional Awards</h3><p>Generous prizes celebrate the dedication and achievements of every participant.</p></div>
      <div class="card"><h3>Unique Platform</h3><p>A unique opportunity for rising ballroom stars to shine on a national stage.</p></div>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">{EVENT_DATE}</span>
      <h2>Schedule</h2>
      <p>Final schedule posted the week prior to the event, subject to change.</p>
    </div>
    <ul class="schedule-list">
      <li><span>Registration Opens</span><span class="time">7:00 AM</span></li>
      <li><span>Ballroom Opens</span><span class="time">8:00 AM</span></li>
      <li><span>Events Begin</span><span class="time">8:30 AM</span></li>
    </ul>
    <div class="text-center" style="margin-top:30px;">
      <a class="btn btn-outline" href="schedule.html">View Full Schedule</a>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Awards</span>
      <h2>Prizes</h2>
    </div>
    <div class="grid grid-2">
      <table class="prize-table">
        <thead><tr><th colspan="2">Top Studio</th></tr></thead>
        <tbody>
          <tr><td>1st Place</td><td>$1,000</td></tr>
          <tr><td>2nd Place</td><td>$750</td></tr>
          <tr><td>3rd Place</td><td>$500</td></tr>
        </tbody>
      </table>
      <table class="prize-table">
        <thead><tr><th colspan="2">Top Teacher</th></tr></thead>
        <tbody>
          <tr><td>1st Place</td><td>$1,000</td></tr>
          <tr><td>2nd Place</td><td>$750</td></tr>
          <tr><td>3rd Place</td><td>$500</td></tr>
        </tbody>
      </table>
    </div>
    <div class="text-center" style="margin-top:30px;">
      <a class="btn btn-outline" href="prizes.html">See All Prize Categories</a>
    </div>
  </div>
</section>

<section class="section-alt">
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

<section>
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
    page("index.html", "Home", "Brilliant Dance Festival — celebrating the next generation of ballroom dance stars. Junior ballroom competition, " + EVENT_DATE + ".", "index.html", body)


def build_about():
    judges = "".join([person_card(n, r, q) for n, r, q in FEATURED_JUDGES])
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
      <span class="eyebrow">Organizers</span>
      <h2>Meet the Team Behind BDF</h2>
    </div>
    <div class="people-grid" style="max-width:560px;margin:0 auto;">
      {person_card("Nina Estrina", "Organizer")}
      {person_card("Taysiya Andryeyeva", "Organizer")}
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
      <h2>What Sets BDF Apart</h2>
    </div>
    <div class="grid grid-4">
      <div class="card"><h3>Professional Recognition</h3><p>Respect and professional-grade competition standards for every dancer.</p></div>
      <div class="card"><h3>Top-Tier Judges</h3><p>Expert feedback that ensures fairness and high standards.</p></div>
      <div class="card"><h3>Exceptional Awards</h3><p>Generous prizes celebrating dedication and achievement.</p></div>
      <div class="card"><h3>Unique Platform</h3><p>A national stage for rising ballroom stars.</p></div>
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
    page("about.html", "About", "About Brilliant Dance Festival — our mission, organizers Nina Estrina and Taysiya Andryeyeva, and what makes BDF unique.", "about.html", body)


def build_partner_search():
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">Latin Only</span>
    <h1>Partner Search</h1>
    <p class="lede">Dancers currently looking for a Latin partner ahead of {EVENT_DATE}.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="grid grid-2">
      <div class="card">
        <div class="photo" style="width:120px;margin-bottom:18px;">{avatar("Nika Shashkina", 120)}</div>
        <h3>Nika Shashkina</h3>
        <p><strong>Level:</strong> PT2/JR1 Silver Level<br>
        <strong>Studio:</strong> DNA Dance Academy<br>
        <strong>Coaches:</strong> Denys Drozdyuk &amp; Antonina Skobina<br>
        <strong>Contact:</strong> 347-656-2617</p>
        <p>Willing to relocate for training and competition.</p>
      </div>
      <div class="card">
        <div class="photo" style="width:120px;margin-bottom:18px;">{avatar("Sophie Gugilev", 120)}</div>
        <h3>Sophie Gugilev</h3>
        <p><strong>Level:</strong> PT2/JR1 Gold/Open Gold<br>
        <strong>Studio:</strong> DNA Dance Academy<br>
        <strong>Coaches:</strong> Denys Drozdyuk &amp; Antonina Skobina<br>
        <strong>Contact:</strong> 347-656-2617</p>
        <p>Open to travel, training, and short-term hosting arrangements.</p>
      </div>
    </div>
    <p class="text-center" style="margin-top:40px;">Want to be listed here? Submit the <a href="registration.html">Partner Search Announcement Form</a> on the registration page.</p>
  </div>
</section>
"""
    page("partner-search.html", "Partner Search", "Brilliant Dance Festival partner search — Latin partner listings for upcoming junior ballroom dancers.", "partner-search.html", body)


def build_judges():
    officials = "".join([person_card(n, r) for n, r in OFFICIALS])
    judges = "".join([person_card(n, r, q) for n, r, q in ALL_JUDGES])
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{EVENT_DATE}</span>
    <h1>Judges &amp; Officials</h1>
    <p class="lede">A panel of renowned experts bringing experience, fairness, and valuable feedback to every performance!</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head"><h2>Judging Panel</h2></div>
    <div class="people-grid">{judges}</div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head"><h2>Officials</h2></div>
    <div class="people-grid">{officials}</div>
  </div>
</section>
"""
    page("judges.html", "Judges & Officials", "Meet the judging panel and officials of Brilliant Dance Festival.", "judges.html", body)


def build_vendors():
    vendor_html = "".join(
        f"""<div class="vendor-item"><h4>{n}</h4><p>{d}</p><p>{c}</p></div>"""
        for n, d, c, _ in VENDORS
    )
    sponsor_html = "".join(
        f"""<div class="vendor-item"><h4>{n}</h4><p>{d}</p><p>{c}</p></div>"""
        for n, d, c in SPONSORS
    )
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{EVENT_DATE}</span>
    <h1>Our Vendors</h1>
    <p class="lede">Businesses and service providers supporting Brilliant Dance Festival.</p>
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
    page("vendors.html", "Vendors", "Vendors and sponsors of Brilliant Dance Festival.", "vendors.html", body)


def build_hotel():
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">Where To Stay</span>
    <h1>Hotel</h1>
    <p class="lede">Camp {"January 9 - 10"} &middot; Festival {EVENT_DATE}</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="info-card text-center">
      <h3>Embassy Suites by Hilton Berkeley Heights</h3>
      <span class="label">Address</span>
      <span class="value">250 Connell Dr, Berkeley Heights, NJ 07922, United States</span>
      <span class="label">Dates</span>
      <span class="value">Camp January 9 &ndash; 10 &middot; Festival {EVENT_DATE}</span>
      <div style="margin-top:26px;">
        <a class="btn btn-primary" href="https://www.hilton.com" target="_blank" rel="noopener">Book The Hotel</a>
      </div>
    </div>
  </div>
</section>
"""
    page("hotel.html", "Hotel", "Official hotel for Brilliant Dance Festival — Embassy Suites by Hilton Berkeley Heights.", "hotel.html", body)


def build_prizes():
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{EVENT_DATE}</span>
    <h1>Prizes</h1>
    <p class="lede">Generous awards celebrating the dedication and achievement of every participant.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="grid grid-2">
      <table class="prize-table">
        <thead><tr><th colspan="2">Top Teacher</th></tr></thead>
        <tbody>
          <tr><td>1st Place</td><td>$1,000</td></tr>
          <tr><td>2nd Place</td><td>$750</td></tr>
          <tr><td>3rd Place</td><td>$500</td></tr>
        </tbody>
      </table>
      <table class="prize-table">
        <thead><tr><th colspan="2">Top Studio</th></tr></thead>
        <tbody>
          <tr><td>1st Place</td><td>$800</td></tr>
          <tr><td>2nd Place</td><td>$500</td></tr>
          <tr><td>3rd Place</td><td>$300</td></tr>
        </tbody>
      </table>
      <table class="prize-table">
        <thead><tr><th colspan="2">Fordney Foundation Championship</th></tr></thead>
        <tbody>
          <tr><td>1st Place</td><td>$150</td></tr>
          <tr><td>2nd Place</td><td>$100</td></tr>
          <tr><td>3rd Place</td><td>$80</td></tr>
          <tr><td>4th Place</td><td>$60</td></tr>
          <tr><td>5th Place</td><td>$50</td></tr>
          <tr><td>6th Place</td><td>$40</td></tr>
        </tbody>
      </table>
      <table class="prize-table">
        <thead><tr><th colspan="2">Top Prize &mdash; Youth &amp; U21 Latin Style Champions</th></tr></thead>
        <tbody>
          <tr><td>Award</td><td>$750</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>
"""
    page("prizes.html", "Prizes", "Prize money and awards at Brilliant Dance Festival.", "prizes.html", body)


def build_schedule():
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{EVENT_DATE}</span>
    <h1>Schedule</h1>
    <p class="lede">Final schedule will be posted the week of the event and is subject to change based on registration.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head"><h2>Day Overview</h2></div>
    <ul class="schedule-list">
      <li><span>Registration Opens</span><span class="time">7:00 AM</span></li>
      <li><span>Ballroom Opens</span><span class="time">8:00 AM</span></li>
      <li><span>Events Begin</span><span class="time">8:30 AM</span></li>
    </ul>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head"><h2>Preliminary Running Order</h2></div>
    <div class="grid grid-2">
      <div class="card">
        <h3>Morning &amp; Afternoon</h3>
        <ul class="schedule-list">
          <li><span>Mixed Amateur Standard</span><span class="time">8:30&ndash;11:00 AM</span></li>
          <li><span>Solo Standard &amp; Latin</span><span class="time">&mdash;</span></li>
          <li><span>Standard &amp; Latin Awards</span><span class="time">&mdash;</span></li>
          <li><span>PreTeen &amp; Junior/Youth Couples (Standard &amp; Latin)</span><span class="time">&mdash;</span></li>
        </ul>
      </div>
      <div class="card">
        <h3>Alternate Track</h3>
        <ul class="schedule-list">
          <li><span>Mixed Amateur Standard</span><span class="time">8:30&ndash;9:30 AM</span></li>
          <li><span>Solo Standard</span><span class="time">9:30 AM</span></li>
          <li><span>PreTeen &amp; Junior categories</span><span class="time">Through evening</span></li>
          <li><span>Junior/Youth/Under 21 Couples Latin</span><span class="time">Concludes 9:00 PM</span></li>
        </ul>
      </div>
    </div>
    <p class="text-center" style="margin-top:30px;color:rgba(255,255,255,0.6);">This is a preliminary outline. Check the official <a href="{HEAT_LIST}" target="_blank" rel="noopener" style="color:#cfa15c;">Heat List</a> the week of the event for exact timing.</p>
  </div>
</section>
"""
    page("schedule.html", "Schedule", "Event day schedule for Brilliant Dance Festival, " + EVENT_DATE + ".", "schedule.html", body)


def build_camp():
    standard = "".join([person_card(n, "Standard Coach", q) for n, q in STANDARD_COACHES])
    latin = "".join([person_card(n, "Latin Coach", q) for n, q in LATIN_COACHES])
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">January 9&ndash;10</span>
    <h1>Brilliant Ballroom Training Camp</h1>
    <p class="lede">Private lessons, lectures, and practice rounds with a world-class coaching faculty, ahead of the {EVENT_DATE} festival.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head"><h2>Daily Schedule</h2></div>
    <ul class="schedule-list">
      <li><span>Private Lessons</span><span class="time">8:45 AM &ndash; 5:00 PM</span></li>
      <li><span>Lectures (4 per day)</span><span class="time">5:00 PM &ndash; 7:00 PM</span></li>
      <li><span>Practice Rounds</span><span class="time">7:00 PM &ndash; 9:00 PM</span></li>
    </ul>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head"><h2>Pricing</h2></div>
    <div class="price-cards">
      <div class="price-card"><h3>Single Day</h3><div class="amount">$180</div><p>January 9</p><a class="btn btn-primary" href="registration.html">Buy Now</a></div>
      <div class="price-card"><h3>Single Day</h3><div class="amount">$180</div><p>January 10</p><a class="btn btn-primary" href="registration.html">Buy Now</a></div>
      <div class="price-card"><h3>Two-Day Pass</h3><div class="amount">$350</div><p>January 9 &ndash; 10</p><a class="btn btn-primary" href="registration.html">Buy Now</a></div>
    </div>
    <p class="text-center" style="margin-top:26px;"><a class="btn btn-outline" href="registration.html">Request Specific Lessons</a></p>
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
    page("camp.html", "Camp", "Brilliant Ballroom Training Camp — private lessons and lectures ahead of Brilliant Dance Festival.", "camp.html", body)


def build_contact():
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
      <div class="photo" style="width:110px;margin-bottom:16px;">{avatar("Nina Estrina", 110)}</div>
      <h3>Nina Estrina</h3>
      <span class="label">Event Organizer</span>
      <span class="label">Phone</span>
      <span class="value"><a href="tel:2675664872">267-566-4872</a></span>
      <span class="label">Email</span>
      <span class="value"><a href="mailto:Dance@brilliantfestival.com">Dance@brilliantfestival.com</a></span>
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
    page("contact.html", "Contact", "Contact Brilliant Dance Festival organizer Nina Estrina.", "contact.html", body)


def build_registration():
    forms = [
        ("Solos", "assets/forms/solos.pdf"),
        ("Amateur Couples", "assets/forms/amateur-couples.pdf"),
        ("MixedAm — Teacher/Student", "assets/forms/mixedam-teacher-student.pdf"),
        ("Smooth/Rhythm Solos/MixedAm/Couples", "assets/forms/smooth-rhythm.pdf"),
        ("Coaching Pass", "assets/forms/coaching-pass.pdf"),
        ("Partner Search Announcement Form", "assets/forms/partner-search.pdf"),
    ]
    doc_list = "".join(
        f'<li><span>{name}</span><a class="dl" href="{href}" download>Download PDF</a></li>' for name, href in forms
    )
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{EVENT_DATE}</span>
    <h1>Registration</h1>
    <p class="lede">Download the form you need, complete it, and mail it in with payment.</p>
  </div>
</section>

<section>
  <div class="container">
    <div class="info-card text-center" style="max-width:640px;">
      <h3>Payment</h3>
      <p>Make checks / money orders payable to: <strong>Brilliant Dance Festival</strong><br>
      Mail to: Brilliant Dance Festival, Bensalem, PA</p>
      <p>Or pay via Zelle to <strong>dance@brilliantdancefestival.com</strong></p>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="section-head"><h2>Registration Forms</h2></div>
    <ul class="doc-list">{doc_list}</ul>
    <p class="form-note text-center">Replace the placeholder files in <code>assets/forms/</code> with your real PDFs.</p>
  </div>
</section>
"""
    page("registration.html", "Registration", "Register for Brilliant Dance Festival — download entry forms and payment instructions.", "registration.html", body)


def build_rules():
    rules = [
        "All attendees must follow National Dance Council of America (NDCA) rules and regulations.",
        "Participants waive claims against the NDCA, organizers, and representatives for injuries or losses.",
        "The festival assumes no responsibility for property damage or theft.",
        "Photography and videography rights belong to organizers; private videotaping requires permission.",
        "All dancers must be registered with NDCA with current proof.",
        "Minors require parental/guardian waivers.",
        "Complete entries include forms, waivers, accounting documentation, and full payment.",
        "Entry deadline is December 12; later submissions accepted at organizers&rsquo; discretion.",
        "Competitors must arrive 30 minutes early; events will not delay for latecomers.",
        "Events with fewer than 3 entries may be canceled or combined; prize money reduced accordingly.",
        "Judge decisions are final; questioning judges is prohibited.",
        "Posted marks cannot be removed without permission.",
        "Closed syllabus events use current NDCA element lists with potential penalties.",
        "Competitors must maintain civil, sportsmanlike conduct.",
        "The festival reserves the right to reject entries from previous rule violators.",
        "Cancellation refunds (minus $100 fee) apply only through the entry deadline.",
        "Mixed Amateur is limited to amateurs partnering outside their regular partnership; advanced amateurs can partner their student competitors.",
        "Student/Student is restricted to adult pro/am dancers, excludes those competing at &ldquo;Open Amateur&rdquo; level, and is limited to single dances only.",
        "Amateur Divisions include Pre-Teen, Junior, Youth, Adult, and Senior categories with age-based classifications.",
        "Newcomer category is for first-year competitors, bronze syllabus only.",
        "Age dancing rules: up one category for Pre-Teen/Junior/Youth; down one for Senior.",
        "Solo Stars are single competitions without partners.",
        "Syllabus restrictions follow NDCA guidelines; lifts are prohibited at all levels.",
        "Costumes follow NDCA requirements by age and syllabus level.",
        "Spectators should wear casual attire during the day, dressy for evening; no smoking in the ballroom, foyer, or changing rooms.",
    ]
    items = "".join(f"<li>{r}</li>" for r in rules)
    body = f"""
<section class="hero small">
  <div class="container">
    <span class="eyebrow">{EVENT_DATE}</span>
    <h1>Rules &amp; Regulations</h1>
    <p class="lede">Please review before registering. Full NDCA rules at <a href="http://www.ndca.org" target="_blank" rel="noopener" style="color:#e8caa0;">ndca.org</a>.</p>
  </div>
</section>

<section>
  <div class="container">
    <ol class="rules-list">{items}</ol>
  </div>
</section>
"""
    page("rules-regulations.html", "Rules & Regulations", "Official rules and regulations for Brilliant Dance Festival.", "rules-regulations.html", body)


def build_404():
    body = f"""
<section class="hero small">
  <div class="container">
    <h1>Page Not Found</h1>
    <p class="lede">The page you're looking for doesn't exist.</p>
    <a class="btn btn-primary" href="index.html">Back To Home</a>
  </div>
</section>
"""
    page("404.html", "Page Not Found", "Page not found.", "", body)


if __name__ == "__main__":
    build_home()
    build_about()
    build_partner_search()
    build_judges()
    build_vendors()
    build_hotel()
    build_prizes()
    build_schedule()
    build_camp()
    build_contact()
    build_registration()
    build_rules()
    build_404()
    print("Built all pages.")
