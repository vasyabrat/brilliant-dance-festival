#!/usr/bin/env python3
"""
Generates placeholder visual assets (logo, sanctioning-body badges, favicon,
registration form PDFs) since this build environment could not download the
live site's actual binary files (see README > "About the images").

Run: python3 scripts/make_assets.py
"""
import os
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
FORMS = os.path.join(ASSETS, "forms")
os.makedirs(FORMS, exist_ok=True)

GOLD = "#cfa15c"
DARK = "#0f0d10"
CREAM = "#faf6ee"


def svg_wordmark(path, text, sub="", width=320, height=110):
    with open(path, "w") as f:
        f.write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="{DARK}" rx="8"/>
  <text x="50%" y="46%" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="26" fill="{GOLD}" dominant-baseline="middle">{text}</text>
  {f'<text x="50%" y="74%" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" letter-spacing="2" fill="{CREAM}" dominant-baseline="middle">{sub}</text>' if sub else ''}
</svg>''')


def svg_badge(path, text, width=200, height=90):
    with open(path, "w") as f:
        f.write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#ffffff" rx="6" stroke="#e5d9c0" stroke-width="1"/>
  <text x="50%" y="50%" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#3a332c" dominant-baseline="middle">{text}</text>
</svg>''')


# Site logo + favicon
svg_wordmark(os.path.join(ASSETS, "logo.png".replace(".png", ".svg")), "Brilliant", "DANCE FESTIVAL")
svg_wordmark(os.path.join(ASSETS, "favicon.svg"), "BDF", width=64, height=64)

# Sanctioning body placeholder badges
svg_badge(os.path.join(ASSETS, "logo-ndca.svg"), "NDCA")
svg_badge(os.path.join(ASSETS, "logo-fordney.svg"), "Fordney Foundation")
svg_badge(os.path.join(ASSETS, "logo-botb.svg"), "Best of the Best")

# Placeholder registration PDFs
FORMS_LIST = [
    ("solos.pdf", "Solos — Entry Form"),
    ("amateur-couples.pdf", "Amateur Couples — Entry Form"),
    ("mixedam-teacher-student.pdf", "MixedAm — Teacher/Student Entry Form"),
    ("smooth-rhythm.pdf", "Smooth/Rhythm Solos, MixedAm & Couples — Entry Form"),
    ("coaching-pass.pdf", "Coaching Pass — Entry Form"),
    ("partner-search.pdf", "Partner Search Announcement Form"),
]

for filename, title in FORMS_LIST:
    c = canvas.Canvas(os.path.join(FORMS, filename), pagesize=LETTER)
    width, height = LETTER
    c.setFillColorRGB(0.05, 0.05, 0.06)
    c.rect(0, height - 90, width, 90, fill=1, stroke=0)
    c.setFillColorRGB(0.81, 0.63, 0.36)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 55, "Brilliant Dance Festival")
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 130, title)
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 160, "This is a placeholder PDF generated during the site rebuild.")
    c.drawString(50, height - 178, "Replace this file with the real registration form in assets/forms/.")
    c.showPage()
    c.save()

print("Assets generated.")
