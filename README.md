# Brilliant Dance Festival — Website

A dependency-free static HTML/CSS/JS rebuild of the Brilliant Dance Festival website (brilliantdancefestival.com) — matched to the live site's navy/cream ballroom theme (Playfair Display + Montserrat, pill buttons) — plus a password-protected admin dashboard so the organizer can edit every piece of content herself: event date, judges, leadership, prizes, schedule, vendors, hotel, contact info, and more.

## How content works

Every page is generated from **`data/content.json`** by **`scripts/build.py`**. There are two ways to edit the site:

1. **Admin dashboard** (recommended) — log in at `/admin`, edit any section, click **Save & Publish**. This writes `data/content.json` and regenerates every `.html` page automatically.
2. **Edit `data/content.json` directly**, then run `python3 scripts/build.py` to regenerate the pages.

Either way, don't hand-edit the generated `.html` files — they get overwritten on the next build.

## Pages

| Page | File |
|---|---|
| Home | `index.html` |
| About | `about.html` |
| Partner Search | `partner-search.html` |
| Judges & Officials | `judges.html` |
| Vendors | `vendors.html` |
| Hotel | `hotel.html` |
| Prizes | `prizes.html` |
| Schedule | `schedule.html` |
| Camp | `camp.html` |
| Contact | `contact.html` |
| Registration | `registration.html` |
| Rules & Regulations | `rules-regulations.html` |
| 404 | `404.html` |
| **Admin dashboard** | `/admin` (served by the backend, not a static file) |

## Running it locally

### Just viewing/editing the static site (no admin login needed)

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

### With the admin dashboard (recommended)

The dashboard is a small Python/Flask backend (`server/app.py`) that serves the whole site **and** the `/admin` editor, and rebuilds the static pages whenever you save.

```bash
cd server
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 app.py
```

Then open **http://localhost:5050**. The first time it runs, it prints a generated admin password to the terminal, e.g.:

```
No admin password set yet — generated one for you:
  a1B2c3D4e5
Log in at /admin, then change it from the dashboard.
```

Log in at `http://localhost:5050/admin` with that password, then change it immediately from the **Change Password** section in the sidebar. The password is stored as a hash in `server/admin_auth.json` (not committed to git).

## What's editable from the admin dashboard

Every top-level section of `data/content.json` gets its own page in the dashboard sidebar:

- **Event & Site Info** — event date, camp dates, Heat List / Score Sheets links, Instagram
- **Homepage Hero** — headline and intro text
- **Leadership / Organizers** — currently just Nina Estrina; add/remove organizers, edit name/role/bio
- **Judging Panel** and **Homepage Featured Judges** — full add/remove/edit for every judge (name, role, quote)
- **Officials**, **Why Choose Us**, **Values/Pillars**
- **Homepage Schedule** and **Full Schedule** (Schedule page tracks)
- **Homepage Prizes** and **Prizes Page** tables
- **Camp**: daily schedule, pricing, standard/Latin coaches
- **Partner Search**, **Vendors**, **Sponsors**, **Hotel**, **Contact Info**
- **Registration Forms** and **Payment Info**
- **Rules & Regulations**
- **Advanced: Raw JSON** — a direct editor over the entire content file, for anything not covered by a dedicated section

Saving always rewrites `data/content.json`, regenerates every HTML page, and the live site reflects the change immediately.

## Deploying

The static frontend can be hosted anywhere static files work (Vercel, Netlify, GitHub Pages, S3, etc. — see `vercel.json`). **The admin dashboard needs a persistent Node/Python-capable host**, since it writes to a local file (`data/content.json`) — this won't work on Vercel serverless functions, which have a read-only/ephemeral filesystem. Good options: Render, Railway, Fly.io, a small VPS, or just running `python3 server/app.py` on a machine you control (e.g. behind a reverse proxy with HTTPS).

Environment variables the backend understands:

- `PORT` — port to listen on (default `5050`)
- `SECRET_KEY` — session signing key (auto-generated and persisted to `server/.secret_key` if not set)
- `FLASK_DEBUG=1` — enable Flask's debug/reload mode (development only)

## About the images

Real photos of people (judges, coaches, organizers, dancers) aren't used — every headshot is a placeholder navy-monogram avatar generated from initials (see `avatar()` in `scripts/build.py`). Swap these for real photos any time by replacing the generated `<svg>`/`<img>` in the relevant page, or by extending `content.json` with a photo URL field and updating `build.py` to use it.

The **logo and the three sanctioning-body badges** (NDCA, Fordney Foundation, Best of the Best Dancesport) are placeholder SVGs — replace `assets/logo.svg`, `assets/logo-ndca.svg`, `assets/logo-fordney.svg`, `assets/logo-botb.svg` with the real artwork (same filenames).

The **six registration PDFs in `assets/forms/`** are placeholders generated by `scripts/make_assets.py` — replace them with real entry forms.

## Contact form

The contact form on `contact.html` is currently front-end only (see `js/main.js`). Wire it to Formspree, a serverless function, or similar — see the comment in `main.js`.

## Structure

```
.
├── index.html, about.html, ... (13 pages — generated, don't hand-edit)
├── css/style.css          — theme (navy/cream, Playfair Display + Montserrat); CSS variables at the top
├── js/main.js              — mobile nav toggle, active-link highlighting, contact form handler
├── assets/                  — logo, badges, favicon, registration form PDFs
├── data/content.json        — single source of truth for all site content
├── scripts/
│   ├── build.py              — generates every HTML page from data/content.json
│   └── make_assets.py        — regenerates placeholder logo/badge/PDF assets
├── server/
│   ├── app.py                 — Flask backend: static file serving + /admin API + auth
│   └── requirements.txt
├── admin/
│   ├── index.html              — admin dashboard shell (login + app)
│   ├── admin.css
│   └── admin.js                 — generic JSON-driven form editor
└── vercel.json
```
