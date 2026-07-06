# 30-Day Backend & Agentic AI Bootcamp — Newsletter Automation

Automatically generates and emails a premium daily engineering newsletter using the **DeepSeek API**, delivered via **GitHub Actions**.

---

## How It Works

```
GitHub Actions (daily cron 7 AM IST)
        │
        ▼
read day_tracker.txt  →  Day N
        │
        ▼
generate_newsletter.py  →  DeepSeek API  →  newsletter_output.html
        │
        ▼
send_email.py  →  SMTP  →  Sagarmurali2004@gmail.com
        │
        ▼
day_tracker.txt  →  Day N+1  →  git commit & push
```

---

## Setup (5 minutes)

### Step 1 — Fork / push this repo to GitHub

```bash
git init
git add .
git commit -m "feat: initial newsletter automation"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2 — Add GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name       | Value                                      |
|-------------------|--------------------------------------------|
| `DEEPSEEK_API_KEY`| Your DeepSeek API key from platform.deepseek.com |
| `SMTP_HOST`       | `smtp.gmail.com`                           |
| `SMTP_PORT`       | `587`                                      |
| `SMTP_USER`       | Your Gmail address (e.g. you@gmail.com)    |
| `SMTP_PASS`       | Your **Gmail App Password** (see below)    |
| `TO_EMAIL`        | `Sagarmurali2004@gmail.com`                |

> **Gmail App Password** (required — not your regular password):
> 1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
> 2. Enable **2-Step Verification** if not already on
> 3. Search for **"App passwords"** → create one for "Mail"
> 4. Use the 16-character generated password as `SMTP_PASS`

### Step 3 — Enable Actions

Go to your repo → **Actions tab** → enable workflows if prompted.

### Step 4 — Test immediately (optional)

Go to **Actions → Daily Bootcamp Newsletter → Run workflow** and optionally set a `day_override` to test a specific day.

---

## Schedule

Runs automatically at **7:00 AM IST** every day (1:30 AM UTC via cron).

---

## Day Tracking

- `day_tracker.txt` stores the current day number (1–30)
- After each successful run, the bot auto-increments and commits it
- After Day 30, it resets to Day 1 automatically
- You can manually override the day using the `day_override` input on workflow_dispatch

---

## File Structure

```
.
├── .github/
│   └── workflows/
│       └── newsletter.yml       # GitHub Actions workflow
├── scripts/
│   ├── generate_newsletter.py   # Calls DeepSeek API, saves HTML
│   └── send_email.py            # Sends HTML via SMTP
├── day_tracker.txt              # Persists current day (auto-updated)
├── .gitignore
└── README.md
```

---

## Customization

- **Change recipient**: Update `TO_EMAIL` secret or edit the default in `send_email.py`
- **Change schedule**: Edit the `cron` expression in `newsletter.yml`
- **Change model**: Edit `"model": "deepseek-chat"` in `generate_newsletter.py` (e.g. `deepseek-reasoner` for R1)
- **Adjust max tokens**: Change `"max_tokens": 8192` — DeepSeek supports up to 8192 on `deepseek-chat`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Email not received | Check spam folder; verify App Password is correct |
| `401 Unauthorized` | DeepSeek API key is wrong or expired |
| Gmail clips email | Newsletter > 102KB — full content is in the HTML attachment |
| Workflow not running | Check Actions are enabled; verify cron syntax |
| Day not advancing | Ensure `contents: write` permission is set in the workflow |
