#!/usr/bin/env python3
"""
Brilliant Dance Festival — admin backend.

Serves the static site + a password-protected admin dashboard at /admin that
can edit every piece of editable content (event date, leadership/organizers,
judges, officials, schedule, prizes, vendors, hotel, contact info, camp,
rules, registration forms...). Saving in the admin dashboard writes
data/content.json and regenerates every .html page via scripts/build.py, so
what you see on the live pages always matches what's in the dashboard.

Run:
    cd server
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python3 app.py

First run prints a generated admin password to the console (also saved to
server/admin_auth.json) — use it to log in at /admin, then change it from
the dashboard's "Change Password" panel.
"""
import json
import os
import secrets
import sys
import time

from flask import Flask, jsonify, request, session, send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SERVER_DIR)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build as site_builder  # noqa: E402

CONTENT_PATH = os.path.join(ROOT, "data", "content.json")
AUTH_PATH = os.path.join(SERVER_DIR, "admin_auth.json")
SECRET_KEY_PATH = os.path.join(SERVER_DIR, ".secret_key")

app = Flask(__name__, static_folder=None)

# ---------------------------------------------------------------------------
# Secret key (persisted across restarts so sessions survive a server reload)
# ---------------------------------------------------------------------------
if os.environ.get("SECRET_KEY"):
    app.secret_key = os.environ["SECRET_KEY"]
elif os.path.exists(SECRET_KEY_PATH):
    with open(SECRET_KEY_PATH) as f:
        app.secret_key = f.read().strip()
else:
    key = secrets.token_hex(32)
    with open(SECRET_KEY_PATH, "w") as f:
        f.write(key)
    app.secret_key = key

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)


# ---------------------------------------------------------------------------
# Admin auth (single admin account, password hash on disk)
# ---------------------------------------------------------------------------
def load_auth():
    if os.path.exists(AUTH_PATH):
        with open(AUTH_PATH) as f:
            return json.load(f)
    return None


def save_auth(password_hash):
    with open(AUTH_PATH, "w") as f:
        json.dump({"password_hash": password_hash}, f)


def bootstrap_auth():
    auth = load_auth()
    if auth:
        return
    generated = secrets.token_urlsafe(9)
    save_auth(generate_password_hash(generated, method="pbkdf2:sha256"))
    print("=" * 60)
    print(" No admin password set yet — generated one for you:")
    print(f"   {generated}")
    print(" Log in at /admin, then change it from the dashboard.")
    print(" (Saved as a hash in server/admin_auth.json)")
    print("=" * 60)


# Very small in-memory rate limiter for the login endpoint.
_login_attempts = {}


def rate_limited(ip):
    now = time.time()
    window = [t for t in _login_attempts.get(ip, []) if now - t < 60]
    _login_attempts[ip] = window
    return len(window) >= 8


def record_attempt(ip):
    _login_attempts.setdefault(ip, []).append(time.time())


def require_auth():
    if not session.get("admin"):
        abort(401)


# ---------------------------------------------------------------------------
# Static site + admin dashboard file serving
# ---------------------------------------------------------------------------
@app.route("/")
def root_index():
    return send_from_directory(ROOT, "index.html")


@app.route("/admin")
@app.route("/admin/")
def admin_index():
    return send_from_directory(os.path.join(ROOT, "admin"), "index.html")


@app.route("/admin/<path:filename>")
def admin_static(filename):
    return send_from_directory(os.path.join(ROOT, "admin"), filename)


@app.route("/<path:filename>")
def static_files(filename):
    # Serve any other file in the repo (html pages, css, js, assets) as-is.
    full_path = os.path.join(ROOT, filename)
    if not os.path.abspath(full_path).startswith(ROOT):
        abort(404)
    if os.path.isfile(full_path):
        return send_from_directory(ROOT, filename)
    abort(404)


# ---------------------------------------------------------------------------
# Auth API
# ---------------------------------------------------------------------------
@app.route("/api/login", methods=["POST"])
def login():
    ip = request.remote_addr or "unknown"
    if rate_limited(ip):
        return jsonify({"error": "Too many attempts. Wait a minute and try again."}), 429
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    auth = load_auth()
    if not auth or not check_password_hash(auth["password_hash"], password):
        record_attempt(ip)
        return jsonify({"error": "Incorrect password."}), 401
    session["admin"] = True
    session.permanent = True
    return jsonify({"ok": True})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("admin", None)
    return jsonify({"ok": True})


@app.route("/api/session")
def session_status():
    return jsonify({"authenticated": bool(session.get("admin"))})


@app.route("/api/admin/change-password", methods=["POST"])
def change_password():
    require_auth()
    data = request.get_json(silent=True) or {}
    current = data.get("currentPassword", "")
    new = data.get("newPassword", "")
    auth = load_auth()
    if not auth or not check_password_hash(auth["password_hash"], current):
        return jsonify({"error": "Current password is incorrect."}), 401
    if len(new) < 8:
        return jsonify({"error": "New password must be at least 8 characters."}), 400
    save_auth(generate_password_hash(new, method="pbkdf2:sha256"))
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Content API
# ---------------------------------------------------------------------------
@app.route("/api/admin/content", methods=["GET"])
def get_content():
    require_auth()
    with open(CONTENT_PATH) as f:
        return jsonify(json.load(f))


@app.route("/api/admin/content", methods=["PUT"])
def put_content():
    require_auth()
    new_content = request.get_json(silent=True)
    if not isinstance(new_content, dict):
        return jsonify({"error": "Invalid content payload."}), 400

    required_top_level = {
        "site", "hero", "pillars", "organizers", "missionText", "whyChooseUs",
        "homeFeaturedJudges", "judgingPanel", "officials", "partnerSearch",
        "vendors", "sponsors", "hotel", "contact", "homeSchedule",
        "scheduleTracks", "homePrizes", "prizeTables", "campSchedule",
        "campPricing", "campCoaches", "registrationForms",
        "registrationPayment", "rules",
    }
    missing = required_top_level - set(new_content.keys())
    if missing:
        return jsonify({"error": f"Missing sections: {', '.join(sorted(missing))}"}), 400
    if not new_content.get("organizers"):
        return jsonify({"error": "At least one organizer is required."}), 400
    if not new_content.get("site", {}).get("eventDate"):
        return jsonify({"error": "Event date is required."}), 400

    # Back up the previous version before overwriting.
    backup_dir = os.path.join(ROOT, "data", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    if os.path.exists(CONTENT_PATH):
        with open(CONTENT_PATH) as f:
            previous = f.read()
        stamp = time.strftime("%Y%m%d-%H%M%S")
        with open(os.path.join(backup_dir, f"content-{stamp}.json"), "w") as f:
            f.write(previous)
        # Keep only the last 20 backups.
        backups = sorted(os.listdir(backup_dir))
        for old in backups[:-20]:
            os.remove(os.path.join(backup_dir, old))

    with open(CONTENT_PATH, "w") as f:
        json.dump(new_content, f, indent=2)
        f.write("\n")

    try:
        site_builder.build_all()
    except Exception as e:
        return jsonify({"error": f"Content saved, but the site failed to rebuild: {e}"}), 500

    return jsonify({"ok": True})


@app.errorhandler(401)
def unauthorized(_e):
    return jsonify({"error": "Not logged in."}), 401


@app.errorhandler(404)
def not_found(_e):
    path = os.path.join(ROOT, "404.html")
    if os.path.exists(path):
        with open(path) as f:
            return f.read(), 404
    return "Not found", 404


if __name__ == "__main__":
    bootstrap_auth()
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
