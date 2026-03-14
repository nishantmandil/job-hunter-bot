<div align="center">

```
     ██╗ ██████╗ ██████╗     ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗
     ██║██╔═══██╗██╔══██╗    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
     ██║██║   ██║██████╔╝    ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██   ██║██║   ██║██╔══██╗    ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
╚█████╔╝╚██████╔╝██████╔╝    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
 ╚════╝  ╚═════╝ ╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
```

### **AI-powered cold email automation for DevOps engineers**
*Stop applying manually. Let AI do the work.*

<br>

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq_AI-Free-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://console.groq.com)
[![Gmail](https://img.shields.io/badge/Gmail-SMTP-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](https://mail.google.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/nishantmandil/job-hunter-bot?style=for-the-badge&color=FFD700)](https://github.com/nishantmandil/job-hunter-bot/stargazers)

<br>

<img src="https://raw.githubusercontent.com/nishantmandil/job-hunter-bot/main/docs/dashboard.png" alt="Dashboard Preview" width="85%" style="border-radius:12px"/>

> *Screenshot: Flask web dashboard — dark UI with live stats, funnel tracker, and one-click batch sending*

</div>

---

## 🔥 The Problem

You're a DevOps engineer with real skills — Kubernetes, Terraform, CI/CD, AWS.

But here's reality:

- You spend **3–4 hours/day** writing the same email with tiny tweaks
- You apply to **5–10 companies** manually and burn out
- You forget to **follow up**, and that's where 40% of replies come from
- You have **no visibility** into what you sent, to whom, and what happened

**Meanwhile, companies hire the person who showed up consistently — not the most qualified one.**

---

## ⚡ The Solution

**Job Hunter Bot** automates your entire outreach pipeline:

```
Add Companies → AI writes personalized email → Sends via Gmail → 
Tracks replies → Auto follow-ups on Day 5, 12, 21 → You get interviews
```

At **20 emails/day** → 100/week → expect **8–15 replies** → **3–5 interviews in 2 weeks.**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **Groq AI Emails** | LLaMA 3.3 70B writes a unique, personalized email for each company |
| 📬 **Gmail Automation** | Sends directly via SMTP — no manual copy-paste |
| 🔁 **Follow-up Engine** | Auto-schedules Day 5 nudge, Day 12 value-add, Day 21 break-up email |
| 📊 **Application Tracker** | SQLite-powered tracker — see every application, status, follow-up |
| 🏢 **Email Finder** | Hunter.io + Apollo.io integration to find real HR emails |
| 🌐 **Flask Web UI** | Beautiful dark dashboard — no terminal needed |
| 🛡️ **Dry-Run Mode** | Test everything safely before going live |
| 📥 **Bulk Import** | Paste a CSV of companies — imported in seconds |
| ⚡ **Batch Send** | Send up to your daily limit in one click |
| 🔒 **Local Storage** | All data stays on your machine — no cloud, no tracking |

---

## 🖥️ UI Preview

<div align="center">

| Dashboard | AI Composer | Tracker |
|:---------:|:-----------:|:-------:|
| Live funnel stats | Groq writes emails live | Filter by status |
| Daily progress bar | One-click Gmail send | Update with dropdown |
| Follow-up alerts | Session counter | Follow-up checkmarks |

</div>

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/nishantmandil/job-hunter-bot.git
cd job-hunter-bot
```

### 2. Install dependencies

```bash
pip install flask groq requests python-dotenv
```

### 3. Set up environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=gsk_your-key-here        # free at console.groq.com
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx # see Gmail setup below
```

### 4. Run

```bash
python app.py
```

Open **[http://localhost:5000](http://localhost:5000)** 🎉

---

## 🔑 API Keys

| Key | Where to get | Cost |
|-----|-------------|------|
| **Groq** (required) | [console.groq.com](https://console.groq.com) → API Keys | **FREE** |
| **Gmail App Password** (to send) | [myaccount.google.com](https://myaccount.google.com) → Security → App Passwords | **FREE** |
| **Hunter.io** (email finder, optional) | [hunter.io](https://hunter.io) → Dashboard → API | 25 free/month |
| **Apollo.io** (email finder, optional) | [apollo.io](https://app.apollo.io) → Settings → API | 50 free/month |

> **Gmail App Password ≠ your Gmail password.**  
> Enable 2FA first → Security → App Passwords → Create one → paste the 16-char code.

---

## 📁 Project Structure

```
job-hunter-bot/
│
├── app.py                  # Flask backend — all routes + AI logic
│
├── templates/
│   ├── base.html           # Dark UI layout, sidebar, toasts
│   ├── index.html          # Dashboard — stats, funnel, checklist
│   ├── companies.html      # Company manager + bulk import
│   ├── compose.html        # AI email composer
│   ├── followups.html      # Follow-up scheduler
│   ├── tracker.html        # Application tracker
│   └── setup.html          # Profile + API keys + settings
│
├── applications.db         # SQLite database (auto-created)
├── config.json             # Your profile + keys (auto-created)
├── sent_log.csv            # CSV log of every email sent
├── requirements.txt
└── .env.example
```

---

## 🔄 How the Follow-up Engine Works

```
Day 0  → Initial cold email (personalized by Groq AI)
Day 5  → Follow-up 1: gentle nudge referencing your original email
Day 12 → Follow-up 2: value-add (share a project insight or article)
Day 21 → Break-up email: final memorable touch, leaves door open
```

Every morning, open the app → go to **Follow-ups** → the bot shows exactly what's due and sends them all in one click.

> Research shows follow-up sequences increase reply rates by **30–40%** compared to a single cold email.

---

## 📊 Expected Results

```
Week 1:  100 emails sent  →  ~8–12 replies  →  ~2–4 interview calls
Week 2:  +100 emails      →  follow-ups hit →  +3–6 more replies
Week 3:  break-up emails  →  surprise replies from earlier sends
```

*Results vary by profile quality, target companies, and email personalization.*

---

## ⚙️ Configuration

All settings are saved in `config.json` and editable from the **Setup** page in the UI.

| Setting | Default | Description |
|---------|---------|-------------|
| `max_emails_per_day` | 20 | Gmail safe limit to avoid spam flags |
| `followup_day_1` | 5 | Days after send for first follow-up |
| `followup_day_2` | 12 | Days after send for second follow-up |
| `followup_day_3` | 21 | Days after send for break-up email |
| `dry_run` | `true` | Test mode — emails not actually sent |

> **Recommended:** Start with dry-run ON, review a few generated emails, then flip it off.

---

## 🛡️ Important Notes

- **LinkedIn scraping** violates their Terms of Service — this bot does **not** scrape LinkedIn
- Keep daily sends under **50/day** to maintain Gmail deliverability
- Use **Hunter.io** or **Apollo.io** for verified HR emails — the bot also guesses `hr@company.com` as a fallback
- All your data (emails, applications, config) stays **100% local** on your machine

---

## 🤝 Contributing

Pull requests are welcome! Some ideas for contributions:

- [ ] Outlook / Office365 SMTP support
- [ ] Resume PDF attachment support
- [ ] Browser extension for LinkedIn email capture
- [ ] Zapier / webhook integration for reply notifications
- [ ] Docker support for easy deployment
- [ ] Email open-tracking pixel

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

**Built by [Nishant Mandil](https://github.com/nishantmandil)**

*If this helped you land interviews, drop a ⭐ — it helps others find this tool.*

[![GitHub stars](https://img.shields.io/github/stars/nishantmandil/job-hunter-bot?style=social)](https://github.com/nishantmandil/job-hunter-bot/stargazers)

</div>
