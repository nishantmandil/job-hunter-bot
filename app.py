"""
╔══════════════════════════════════════════════════════════════════╗
║      DEVOPS JOB HUNTER BOT  —  Flask Web UI + Groq AI           ║
╚══════════════════════════════════════════════════════════════════╝

Run:
    pip install flask groq requests python-dotenv
    python app.py

Then open: http://localhost:5000
"""

import os, json, sqlite3, smtplib, datetime, csv, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for

try:
    from groq import Groq
    import requests as req
    from dotenv import load_dotenv
except ImportError:
    print("\n[!] Run:  pip install flask groq requests python-dotenv\n")
    raise

load_dotenv()

app       = Flask(__name__)
BASE_DIR  = Path(__file__).parent
DB_PATH   = BASE_DIR / "applications.db"
CFG_PATH  = BASE_DIR / "config.json"
LOG_PATH  = BASE_DIR / "sent_log.csv"
GROQ_MODEL = "llama-3.3-70b-versatile"

# ── defaults ───────────────────────────────────────────────────────
DEFAULT_CFG = {
    "profile": {
        "name": "", "experience_years": "3-5", "title": "DevOps Engineer",
        "location": "Delhi, India (open to remote)",
        "linkedin": "", "github": "",
        "achievement_1": "", "achievement_2": "",
        "skills": ["Docker","Kubernetes","CI/CD","AWS","Terraform","GitLab CI"],
        "target_roles": "DevOps Engineer, SRE, Platform Engineer"
    },
    "api_keys": {
        "groq": "", "hunter_io": "", "gmail_address": "", "gmail_app_password": ""
    },
    "settings": {
        "max_emails_per_day": 20,
        "followup_day_1": 5, "followup_day_2": 12, "followup_day_3": 21,
        "dry_run": True
    }
}

# ══════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════

def load_cfg():
    if CFG_PATH.exists():
        with open(CFG_PATH) as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CFG.items():
            if k not in cfg: cfg[k] = v
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    if kk not in cfg[k]: cfg[k][kk] = vv
        return cfg
    return DEFAULT_CFG.copy()

def save_cfg(cfg):
    with open(CFG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def today():
    return datetime.date.today().isoformat()

def future(days):
    return (datetime.date.today() + datetime.timedelta(days=days)).isoformat()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, domain TEXT, hr_email TEXT,
        contact_role TEXT DEFAULT 'HR / Recruiter',
        verified INTEGER DEFAULT 0, added_date TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, company_name TEXT, hr_email TEXT,
        subject TEXT, body TEXT, sent_date TEXT, status TEXT DEFAULT 'sent',
        followup_1_date TEXT, followup_2_date TEXT, followup_3_date TEXT,
        followup_1_sent INTEGER DEFAULT 0,
        followup_2_sent INTEGER DEFAULT 0,
        followup_3_sent INTEGER DEFAULT 0, notes TEXT)""")
    conn.commit(); conn.close()

def groq_key(cfg):
    return cfg["api_keys"].get("groq") or os.getenv("GROQ_API_KEY","")

def sent_today_count(cfg):
    conn = get_db()
    n = conn.execute("SELECT COUNT(*) FROM applications WHERE sent_date=?", (today(),)).fetchone()[0]
    conn.close()
    return n

# ══════════════════════════════════════════════════════════════════
#  AI
# ══════════════════════════════════════════════════════════════════

def build_profile(cfg):
    p = cfg["profile"]
    skills = ", ".join(p.get("skills",[])[:6]) or "Docker, Kubernetes, CI/CD, AWS"
    return (f"Name: {p.get('name') or 'DevOps Engineer'}\n"
            f"Experience: {p.get('experience_years','3-5')} years\n"
            f"Title: {p.get('title','DevOps Engineer')}\n"
            f"Location: {p.get('location','India')}\n"
            f"Skills: {skills}\n"
            f"Achievement 1: {p.get('achievement_1') or 'Built GitOps pipeline cutting deploy time 60%'}\n"
            f"Achievement 2: {p.get('achievement_2') or 'Reduced cloud costs through rightsizing'}\n"
            f"LinkedIn: {p.get('linkedin') or 'linkedin.com/in/yourprofile'}")

def generate_email(company, cfg, tone="Professional & concise", angle="Lead with top achievement", extra=""):
    key = groq_key(cfg)
    if not key:
        return _template_email(company, cfg)
    prompt = (f"Write a cold job application email for a DevOps engineer applying to {company}.\n\n"
              f"PROFILE:\n{build_profile(cfg)}\n\n"
              f"Tone: {tone}\nAngle: {angle}\nExtra context: {extra or 'None'}\n\n"
              f"RULES:\n1. Line 1: Subject: [subject]\n2. Blank line\n3. Body under 200 words\n"
              f"4. Use '{company}' directly — no [brackets]\n5. End with name + LinkedIn\n\nWrite now:")
    try:
        client = Groq(api_key=key)
        r = client.chat.completions.create(model=GROQ_MODEL, max_tokens=900,
            messages=[{"role":"user","content":prompt}])
        text  = r.choices[0].message.content.strip()
        lines = text.split("\n")
        subj  = next((l.split(":",1)[1].strip() for l in lines if l.lower().startswith("subject:")),
                     f"DevOps Engineer – {cfg['profile'].get('name','Application')}")
        body  = "\n".join(l for l in lines if not l.lower().startswith("subject:")).strip()
        return subj, body
    except Exception as e:
        return _template_email(company, cfg)

def _template_email(company, cfg):
    p    = cfg["profile"]
    name = p.get("name") or "Your Name"
    exp  = p.get("experience_years","3-5")
    sk   = ", ".join(p.get("skills",[])[:4]) or "Docker, Kubernetes, CI/CD, AWS"
    a1   = p.get("achievement_1") or "built a GitOps CI/CD pipeline reducing deploy time by 60%"
    li   = p.get("linkedin") or "linkedin.com/in/yourprofile"
    subj = f"DevOps Engineer — {exp} yrs | {name}"
    body = (f"Hi,\n\nI'm {name}, a DevOps engineer with {exp} years of experience. "
            f"I came across {company} and was impressed by your engineering culture.\n\n"
            f"I specialise in {sk}. Most recently, I {a1.lower().rstrip('.')}.\n\n"
            f"What I bring to {company}:\n"
            f"  • Automated CI/CD pipelines from day one\n"
            f"  • Cloud-native infra with Terraform + Kubernetes\n"
            f"  • SRE mindset — observability, SLOs, runbooks\n\n"
            f"I'd love a 20-minute chat. CV attached.\n\nBest,\n{name}\n{li}")
    return subj, body

def generate_followup(company, fnum, cfg):
    key  = groq_key(cfg)
    name = cfg["profile"].get("name") or "Your Name"
    fallback = {
        1:(f"Following up – DevOps role at {company}",
           f"Hi,\n\nFollowing up on my email last week about a DevOps role at {company}.\nStill very interested — would you have 15 minutes this week?\n\nBest,\n{name}"),
        2:(f"Something useful – {company}",
           f"Hi,\n\nI recently completed a GitOps migration with ArgoCD that cut release cycles from 2 weeks to same-day. Thought it might be relevant for {company}.\n\nStill keen to connect!\n\nBest,\n{name}"),
        3:(f"Last note – {company}",
           f"Hi,\n\nI'll make this my last message regarding a DevOps role at {company}. If timing ever changes, I'd love to connect.\n\nWishing {company} all the best.\n\n{name}")
    }
    if not key:
        return fallback[fnum]
    descs = {
        1:f"a polite 60-word follow-up to a cold job application sent 5 days ago to {company}",
        2:f"a 80-word value-add follow-up to {company}, mentioning a relevant DevOps project or insight",
        3:f"a 60-word professional break-up final email to {company}, memorable, not desperate"
    }
    try:
        client = Groq(api_key=key)
        r = client.chat.completions.create(model=GROQ_MODEL, max_tokens=350,
            messages=[{"role":"user","content":
                f"Write {descs[fnum]}. Applicant: {name}. Start with Subject: line. No [brackets]."}])
        text  = r.choices[0].message.content.strip()
        lines = text.split("\n")
        subj  = next((l.split(":",1)[1].strip() for l in lines if l.lower().startswith("subject:")),
                     f"Following up – {company}")
        body  = "\n".join(l for l in lines if not l.lower().startswith("subject:")).strip()
        return subj, body
    except:
        return fallback[fnum]

# ══════════════════════════════════════════════════════════════════
#  EMAIL SENDER
# ══════════════════════════════════════════════════════════════════

def send_gmail(to, subject, body, cfg):
    g  = cfg["api_keys"].get("gmail_address","")
    pw = cfg["api_keys"].get("gmail_app_password","")
    if not g or not pw:
        return False, "Gmail credentials not configured."
    if cfg["settings"].get("dry_run", True):
        return True, "dry_run"
    try:
        msg            = MIMEMultipart()
        msg["From"]    = g
        msg["To"]      = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(g, pw)
            s.sendmail(g, to, msg.as_string())
        with open(LOG_PATH, "a", newline="") as f:
            csv.writer(f).writerow([today(), to, subject, "sent"])
        return True, "sent"
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail auth failed — use an App Password, not your normal password."
    except Exception as e:
        return False, str(e)

# ══════════════════════════════════════════════════════════════════
#  ROUTES — PAGES
# ══════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    cfg  = load_cfg()
    conn = get_db()
    total_cos  = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    total_apps = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    replies    = conn.execute("SELECT COUNT(*) FROM applications WHERE status='replied'").fetchone()[0]
    interviews = conn.execute("SELECT COUNT(*) FROM applications WHERE status='interview'").fetchone()[0]
    sent_td    = sent_today_count(cfg)
    limit      = cfg["settings"]["max_emails_per_day"]
    t          = today()
    due1 = conn.execute("SELECT COUNT(*) FROM applications WHERE followup_1_date<=? AND followup_1_sent=0 AND status NOT IN ('replied','interview','offer')",(t,)).fetchone()[0]
    due2 = conn.execute("SELECT COUNT(*) FROM applications WHERE followup_2_date<=? AND followup_2_sent=0 AND status NOT IN ('replied','interview','offer')",(t,)).fetchone()[0]
    due3 = conn.execute("SELECT COUNT(*) FROM applications WHERE followup_3_date<=? AND followup_3_sent=0 AND status NOT IN ('replied','interview','offer')",(t,)).fetchone()[0]
    recent = conn.execute("SELECT company_name, hr_email, sent_date, status FROM applications ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    rate = f"{round(replies/total_apps*100)}%" if total_apps else "—"
    return render_template("index.html", cfg=cfg,
        stats=dict(companies=total_cos, sent=total_apps, replies=replies,
                   interviews=interviews, rate=rate, sent_today=sent_td,
                   limit=limit, due1=due1, due2=due2, due3=due3),
        recent=recent)

@app.route("/companies")
def companies():
    cfg  = load_cfg()
    conn = get_db()
    rows = conn.execute("SELECT * FROM companies ORDER BY name").fetchall()
    conn.close()
    return render_template("companies.html", cfg=cfg, companies=rows)

@app.route("/compose")
def compose():
    cfg  = load_cfg()
    conn = get_db()
    cos  = conn.execute("""SELECT c.id, c.name, c.hr_email FROM companies c
        WHERE c.id NOT IN (SELECT company_id FROM applications WHERE company_id IS NOT NULL)
        ORDER BY c.name""").fetchall()
    conn.close()
    return render_template("compose.html", cfg=cfg, companies=cos)

@app.route("/followups")
def followups():
    cfg  = load_cfg()
    t    = today()
    conn = get_db()
    due1 = conn.execute("SELECT a.id, a.company_name, a.hr_email, a.followup_1_date FROM applications a WHERE a.followup_1_date<=? AND a.followup_1_sent=0 AND a.status NOT IN ('replied','interview','offer') ORDER BY a.followup_1_date",(t,)).fetchall()
    due2 = conn.execute("SELECT a.id, a.company_name, a.hr_email, a.followup_2_date FROM applications a WHERE a.followup_2_date<=? AND a.followup_2_sent=0 AND a.status NOT IN ('replied','interview','offer') ORDER BY a.followup_2_date",(t,)).fetchall()
    due3 = conn.execute("SELECT a.id, a.company_name, a.hr_email, a.followup_3_date FROM applications a WHERE a.followup_3_date<=? AND a.followup_3_sent=0 AND a.status NOT IN ('replied','interview','offer') ORDER BY a.followup_3_date",(t,)).fetchall()
    conn.close()
    return render_template("followups.html", cfg=cfg, due1=due1, due2=due2, due3=due3)

@app.route("/tracker")
def tracker():
    cfg    = load_cfg()
    status = request.args.get("status","all")
    conn   = get_db()
    if status == "all":
        rows = conn.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
    else:
        rows = conn.execute("SELECT * FROM applications WHERE status=? ORDER BY id DESC",(status,)).fetchall()
    conn.close()
    return render_template("tracker.html", cfg=cfg, applications=rows, filter=status)

@app.route("/setup")
def setup():
    cfg = load_cfg()
    return render_template("setup.html", cfg=cfg)

# ══════════════════════════════════════════════════════════════════
#  ROUTES — API
# ══════════════════════════════════════════════════════════════════

@app.route("/api/save-config", methods=["POST"])
def api_save_config():
    cfg  = load_cfg()
    data = request.json
    section = data.get("section")
    if section == "profile":
        p = cfg["profile"]
        for k in ["name","experience_years","title","location","linkedin","github",
                  "achievement_1","achievement_2","target_roles"]:
            if k in data: p[k] = data[k]
        if "skills" in data:
            p["skills"] = [s.strip() for s in data["skills"].split(",") if s.strip()]
    elif section == "keys":
        k = cfg["api_keys"]
        for key in ["groq","hunter_io","gmail_address","gmail_app_password"]:
            if key in data: k[key] = data[key]
    elif section == "settings":
        s = cfg["settings"]
        for k in ["max_emails_per_day","followup_day_1","followup_day_2","followup_day_3"]:
            if k in data: s[k] = int(data[k])
        if "dry_run" in data: s["dry_run"] = bool(data["dry_run"])
    save_cfg(cfg)
    return jsonify({"ok": True})

@app.route("/api/add-company", methods=["POST"])
def api_add_company():
    data   = request.json
    cfg    = load_cfg()
    name   = data.get("name","").strip()
    domain = data.get("domain","").strip()
    email  = data.get("email","").strip()
    if not name:
        return jsonify({"ok":False,"error":"Company name required"})
    if not email and domain:
        # try Hunter.io
        if cfg["api_keys"].get("hunter_io"):
            try:
                r = req.get(f"https://api.hunter.io/v2/domain-search?domain={domain}&role=hr&limit=1&api_key={cfg['api_keys']['hunter_io']}",timeout=8)
                emails = r.json().get("data",{}).get("emails",[])
                if emails: email = emails[0].get("value","")
            except: pass
        if not email: email = f"hr@{domain}" if domain else ""
    role     = data.get("role","HR / Recruiter")
    verified = 1 if data.get("verified") else 0
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO companies (name,domain,hr_email,contact_role,verified,added_date) VALUES (?,?,?,?,?,?)",
                 (name,domain,email,role,verified,today()))
    conn.commit(); conn.close()
    return jsonify({"ok":True,"email":email})

@app.route("/api/delete-company/<int:cid>", methods=["DELETE"])
def api_delete_company(cid):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM companies WHERE id=?",(cid,))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/api/bulk-import", methods=["POST"])
def api_bulk_import():
    text  = request.json.get("csv","")
    added = 0
    conn  = sqlite3.connect(DB_PATH)
    for line in text.strip().split("\n"):
        parts = [p.strip() for p in line.split(",")]
        if not parts or not parts[0]: continue
        if parts[0].lower() in ("company","company name","name"): continue
        name   = parts[0]
        domain = parts[1] if len(parts)>1 else ""
        email  = parts[2] if len(parts)>2 else (f"hr@{domain}" if domain else "")
        conn.execute("INSERT INTO companies (name,domain,hr_email,contact_role,added_date) VALUES (?,?,?,?,?)",
                     (name,domain,email,"HR / Recruiter",today()))
        added += 1
    conn.commit(); conn.close()
    return jsonify({"ok":True,"added":added})

@app.route("/api/generate-email", methods=["POST"])
def api_generate_email():
    data    = request.json
    cfg     = load_cfg()
    co_id   = int(data.get("company_id",0))
    conn    = get_db()
    co      = conn.execute("SELECT name, hr_email FROM companies WHERE id=?",(co_id,)).fetchone()
    conn.close()
    if not co:
        return jsonify({"ok":False,"error":"Company not found"})
    subj, body = generate_email(co["name"], cfg,
                                tone=data.get("tone","Professional & concise"),
                                angle=data.get("angle","Lead with top achievement"),
                                extra=data.get("extra",""))
    return jsonify({"ok":True,"subject":subj,"body":body,"to":co["hr_email"],"company":co["name"]})

@app.route("/api/send-email", methods=["POST"])
def api_send_email():
    data    = request.json
    cfg     = load_cfg()
    co_id   = int(data.get("company_id",0))
    subject = data.get("subject","")
    body    = data.get("body","")
    to      = data.get("to","")
    sent_td = sent_today_count(cfg)
    limit   = cfg["settings"]["max_emails_per_day"]
    if sent_td >= limit:
        return jsonify({"ok":False,"error":f"Daily limit of {limit} reached."})
    ok_send, msg = send_gmail(to, subject, body, cfg)
    if ok_send:
        s = cfg["settings"]
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""INSERT INTO applications
            (company_id,company_name,hr_email,subject,body,sent_date,status,
             followup_1_date,followup_2_date,followup_3_date) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (co_id, data.get("company",""), to, subject, body, today(), "sent",
             future(s["followup_day_1"]), future(s["followup_day_2"]), future(s["followup_day_3"])))
        conn.commit(); conn.close()
        return jsonify({"ok":True,"dry_run": msg=="dry_run"})
    return jsonify({"ok":False,"error":msg})

@app.route("/api/generate-followup", methods=["POST"])
def api_generate_followup():
    data  = request.json
    cfg   = load_cfg()
    company = data.get("company","")
    fnum    = int(data.get("fnum",1))
    subj, body = generate_followup(company, fnum, cfg)
    return jsonify({"ok":True,"subject":subj,"body":body})

@app.route("/api/send-followup", methods=["POST"])
def api_send_followup():
    data   = request.json
    cfg    = load_cfg()
    app_id = int(data.get("app_id",0))
    fnum   = int(data.get("fnum",1))
    conn   = get_db()
    appl   = conn.execute("SELECT company_name, hr_email FROM applications WHERE id=?",(app_id,)).fetchone()
    conn.close()
    if not appl:
        return jsonify({"ok":False,"error":"Application not found"})
    subj, body = generate_followup(appl["company_name"], fnum, cfg)
    ok_send, msg = send_gmail(appl["hr_email"], subj, body, cfg)
    if ok_send:
        col = f"followup_{fnum}_sent"
        conn = sqlite3.connect(DB_PATH)
        conn.execute(f"UPDATE applications SET {col}=1 WHERE id=?",(app_id,))
        conn.commit(); conn.close()
        return jsonify({"ok":True,"dry_run": msg=="dry_run"})
    return jsonify({"ok":False,"error":msg})

@app.route("/api/update-status", methods=["POST"])
def api_update_status():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE applications SET status=? WHERE id=?",
                 (data["status"], int(data["app_id"])))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/api/toggle-dryrun", methods=["POST"])
def api_toggle_dryrun():
    cfg = load_cfg()
    cfg["settings"]["dry_run"] = not cfg["settings"].get("dry_run", True)
    save_cfg(cfg)
    return jsonify({"ok":True,"dry_run":cfg["settings"]["dry_run"]})

@app.route("/api/batch-send", methods=["POST"])
def api_batch_send():
    cfg     = load_cfg()
    sent_td = sent_today_count(cfg)
    limit   = cfg["settings"]["max_emails_per_day"]
    remaining = limit - sent_td
    if remaining <= 0:
        return jsonify({"ok":False,"error":f"Daily limit of {limit} reached."})
    conn = get_db()
    rows = conn.execute("""SELECT c.id, c.name, c.hr_email FROM companies c
        WHERE c.id NOT IN (SELECT company_id FROM applications WHERE company_id IS NOT NULL)
        AND c.hr_email IS NOT NULL AND c.hr_email!='' ORDER BY c.added_date LIMIT ?""",(remaining,)).fetchall()
    conn.close()
    results = []
    for co in rows:
        subj, body = generate_email(co["name"], cfg)
        ok_send, msg = send_gmail(co["hr_email"], subj, body, cfg)
        if ok_send:
            s = cfg["settings"]
            conn = sqlite3.connect(DB_PATH)
            conn.execute("""INSERT INTO applications
                (company_id,company_name,hr_email,subject,body,sent_date,status,
                 followup_1_date,followup_2_date,followup_3_date) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (co["id"],co["name"],co["hr_email"],subj,body,today(),"sent",
                 future(s["followup_day_1"]),future(s["followup_day_2"]),future(s["followup_day_3"])))
            conn.commit(); conn.close()
            results.append({"company":co["name"],"email":co["hr_email"],"ok":True})
        else:
            results.append({"company":co["name"],"email":co["hr_email"],"ok":False,"error":msg})
        time.sleep(1)
    return jsonify({"ok":True,"results":results})

if __name__ == "__main__":
    init_db()
    print("\n  ✔  DevOps Job Hunter running at → http://localhost:5000\n")
    app.run(debug=True, port=5000)
