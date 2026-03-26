[README.md](https://github.com/user-attachments/files/26278952/README.md)
# CT Legislature Amendment Tracker
### Powered by Claude Code Agent (Headless Mode)

Monitors the CT General Assembly's amendment report pages every weekday at 9 AM Eastern.
Unlike a basic scraper, the **Claude Code agent reasons about the changes** — it tells you
"HB 5001 received 2 new amendments from Rep. Smith" rather than dumping raw text diffs.

---

## How It Works

```
GitHub Actions (schedule: weekdays 9 AM ET)
    └── claude -p "Check CT amendments, compare, email report"
            ├── Reads CLAUDE.md for standing instructions
            ├── curl → fetches House + Senate amendment pages
            ├── Reads ./data/ snapshots from last run
            ├── Reasons about what changed legislatively
            ├── Writes HTML report → /tmp/ct_report.html
            ├── python3 scripts/send_email.py → delivers email
            └── Writes updated snapshots → ./data/
    └── git commit → snapshots saved for next comparison
```

---

## Setup (~7 minutes)

### Step 1 — Create a GitHub repo

Push this folder to a new GitHub repository. Private is fine.

### Step 2 — Add GitHub Secrets

**Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key ([console.anthropic.com](https://console.anthropic.com)) |
| `EMAIL_SENDER` | Gmail address sending the alerts |
| `EMAIL_PASSWORD` | Gmail **App Password** (see below) |
| `EMAIL_TO` | Recipient(s), comma-separated |

> **Gmail App Password:**
> 1. Enable 2-factor auth on your Google account
> 2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
> 3. Generate a password named "CT Amendment Tracker"
> 4. Use the 16-character code as `EMAIL_PASSWORD`

### Step 3 — Enable Actions

Go to the **Actions** tab → click **Enable workflows** if prompted.

### Step 4 — First run

**Actions → CT Amendment Tracker → Run workflow**

This sets the baseline snapshots and emails a "first run" report.
Subsequent runs will diff against it.

---

## Cost

Each daily run uses Claude to reason about the pages — typically well under **$0.05/run**
(capped at $0.15 as a safety limit in the workflow). At 5 days/week that's roughly
**$0.50–$1.00/month** in API costs.

---

## File Structure

```
ct-amendments/
├── CLAUDE.md                          ← Agent's standing instructions (read every run)
├── .github/
│   └── workflows/
│       └── ct_amendments.yml          ← Schedule + headless claude -p invocation
├── scripts/
│   └── send_email.py                  ← Email helper called by the agent
├── data/
│   ├── house_amendments.txt           ← Auto-updated snapshots
│   └── senate_amendments.txt
└── README.md
```

---

## Customizing the Agent

Edit **`CLAUDE.md`** to change what the agent pays attention to:
- Track specific bill numbers only
- Change the email format or tone
- Add more URLs to monitor (e.g., committee calendars)
- Post to Slack instead of email

The agent reads `CLAUDE.md` fresh on every run, so changes take effect immediately —
no code changes needed.
