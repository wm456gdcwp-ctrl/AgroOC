# -*- coding: utf-8 -*-
"""AgroOS server — bitta ma'lumot bazasi, ko'p foydalanuvchi."""
import os, json, sqlite3, secrets, hashlib, time
from functools import wraps
from flask import Flask, request, jsonify, session, send_from_directory, Response

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("AGROOS_DB", os.path.join(APP_DIR, "agroos.db"))

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_HTTPONLY=True,
                  PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30)

DEFAULT_USERS = [
    ("asqar",     "Asqar",             "owner",  "1111"),
    ("bobur",     "Bobur",             "qozo",   "2222"),
    ("zuhriddin", "Zuhriddin",         "tosh",   "3333"),
    ("akmal",     "Akmal Karimov",     "yem",    "4444"),
    ("xasan",     "Xasan Toshpolatov", "ferma",  "5555"),
]

def h(pin: str) -> str:
    return hashlib.sha256(("agroos$" + pin).encode()).hexdigest()

def db():
    c = sqlite3.connect(DB_PATH, timeout=15)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c

def init():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        login TEXT PRIMARY KEY, name TEXT, role TEXT, pin TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS state(
        id INTEGER PRIMARY KEY CHECK (id=1), doc TEXT, rev INTEGER, ts REAL, who TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS backups(
        id INTEGER PRIMARY KEY AUTOINCREMENT, doc TEXT, rev INTEGER, ts REAL, who TEXT)""")
    if not c.execute("SELECT 1 FROM state WHERE id=1").fetchone():
        c.execute("INSERT INTO state(id,doc,rev,ts,who) VALUES(1,?,?,?,?)",
                  ("{}", 0, time.time(), ""))
    for login, name, role, pin in DEFAULT_USERS:
        if not c.execute("SELECT 1 FROM users WHERE login=?", (login,)).fetchone():
            c.execute("INSERT INTO users(login,name,role,pin) VALUES(?,?,?,?)",
                      (login, name, role, h(pin)))
    c.commit(); c.close()

init()

def need_login(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("login"):
            return jsonify(ok=False, error="auth"), 401
        return f(*a, **k)
    return w

@app.after_request
def no_cache(r):
    if request.path.endswith((".html", "/")) or request.path.startswith("/api"):
        r.headers["Cache-Control"] = "no-store, must-revalidate"
    return r

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "app.html")

@app.get("/manifest.webmanifest")
def manifest():
    return Response(json.dumps({
        "name": "AgroOC Holdings", "short_name": "AgroOC", "start_url": "/", "display": "standalone",
        "background_color": "#F6F5F0", "theme_color": "#1E7B2E",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"}
        ]
    }), mimetype="application/manifest+json")

@app.get("/icon-<int:size>.png")
def icon_png(size):
    if size not in (180, 192, 512):
        size = 192
    return send_from_directory(app.static_folder, f"icon-{size}.png", max_age=86400)

@app.post("/api/login")
def login():
    d = request.get_json(silent=True) or {}
    pin = str(d.get("pin", "")).strip()
    row = db().execute("SELECT * FROM users WHERE pin=?", (h(pin),)).fetchone()
    if not row:
        time.sleep(0.6)
        return jsonify(ok=False, error="PIN noto'g'ri"), 401
    session.permanent = True
    session["login"], session["name"], session["role"] = row["login"], row["name"], row["role"]
    return jsonify(ok=True, name=row["name"], role=row["role"])

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)

@app.get("/api/me")
def me():
    if not session.get("login"):
        return jsonify(ok=False), 401
    return jsonify(ok=True, name=session["name"], role=session["role"], login=session["login"])

@app.get("/api/data")
@need_login
def get_data():
    r = db().execute("SELECT doc,rev,ts,who FROM state WHERE id=1").fetchone()
    return jsonify(ok=True, doc=json.loads(r["doc"] or "{}"), rev=r["rev"], ts=r["ts"], who=r["who"])

@app.get("/api/rev")
@need_login
def get_rev():
    r = db().execute("SELECT rev,ts,who FROM state WHERE id=1").fetchone()
    return jsonify(ok=True, rev=r["rev"], ts=r["ts"], who=r["who"])

@app.post("/api/data")
@need_login
def put_data():
    d = request.get_json(silent=True) or {}
    doc, base = d.get("doc"), d.get("rev")
    if not isinstance(doc, dict):
        return jsonify(ok=False, error="doc"), 400
    c = db()
    cur = c.execute("SELECT rev FROM state WHERE id=1").fetchone()["rev"]
    if base is not None and int(base) != int(cur):
        r = c.execute("SELECT doc,rev,ts,who FROM state WHERE id=1").fetchone()
        c.close()
        return jsonify(ok=False, error="conflict", doc=json.loads(r["doc"] or "{}"),
                       rev=r["rev"], who=r["who"]), 409
    rev = cur + 1
    txt = json.dumps(doc, ensure_ascii=False)
    who = session.get("name", "")
    c.execute("UPDATE state SET doc=?,rev=?,ts=?,who=? WHERE id=1", (txt, rev, time.time(), who))
    if rev % 20 == 0:
        c.execute("INSERT INTO backups(doc,rev,ts,who) VALUES(?,?,?,?)", (txt, rev, time.time(), who))
        c.execute("DELETE FROM backups WHERE id NOT IN (SELECT id FROM backups ORDER BY id DESC LIMIT 50)")
    c.commit(); c.close()
    return jsonify(ok=True, rev=rev)

@app.get("/api/users")
@need_login
def users():
    if session.get("role") != "owner":
        return jsonify(ok=False, error="faqat egasi"), 403
    rows = db().execute("SELECT login,name,role FROM users ORDER BY login").fetchall()
    return jsonify(ok=True, users=[dict(r) for r in rows])

@app.post("/api/pin")
@need_login
def set_pin():
    d = request.get_json(silent=True) or {}
    login = d.get("login") or session["login"]
    pin = str(d.get("pin", "")).strip()
    if len(pin) < 4:
        return jsonify(ok=False, error="PIN kamida 4 raqam"), 400
    if login != session["login"] and session.get("role") != "owner":
        return jsonify(ok=False, error="faqat egasi"), 403
    c = db(); c.execute("UPDATE users SET pin=? WHERE login=?", (h(pin), login)); c.commit(); c.close()
    return jsonify(ok=True)

@app.get("/api/backup")
@need_login
def backup():
    r = db().execute("SELECT doc,rev FROM state WHERE id=1").fetchone()
    return Response(r["doc"] or "{}", mimetype="application/json",
                    headers={"Content-Disposition": f'attachment; filename="agroos-{int(time.time())}.json"'})

@app.get("/favicon.ico")
def favicon():
    return Response(status=204)

@app.get("/healthz")
def healthz():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
