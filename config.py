# ─────────────────────────────────────────────────────────
#  JobRadar — Configuration  (edit this file to customise)
# ─────────────────────────────────────────────────────────

# Keywords to search — scraper runs each one on every active site
KEYWORDS = [
    "python developer",
    "data analyst",
    "machine learning engineer",
    "backend developer",
    "software engineer",
]

# Preferred locations (used in filters & alerts)
LOCATIONS = ["Rajasthan", "Remote", "Jaipur", "Delhi", "India"]

# Active scrapers — comment out any you want to disable
ACTIVE_SCRAPERS = [
    "internshala",   # internshala.com  — jobs & internships
    "timesjobs",     # timesjobs.com    — mid-level roles
    "indeed",        # in.indeed.com    — large aggregator
    "naukri",        # naukri.com       — India's biggest board
    "shine",         # shine.com        — HT Media job board
    "foundit",       # foundit.in       — ex-Monster India
    "ncs",           # ncs.gov.in       — Govt / NCS portal
]

# ── Telegram Bot (optional — leave blank to skip) ─────────
TELEGRAM_TOKEN   = ""    # from BotFather: 123456:ABCxyz...
TELEGRAM_CHAT_ID = ""    # your chat ID

# ── Gmail alerts (optional — leave blank to skip) ─────────
GMAIL_ADDRESS      = ""  # your@gmail.com
GMAIL_APP_PASSWORD = ""  # Gmail App Password (not login password)

# ── Scraper behaviour ──────────────────────────────────────
SCRAPE_INTERVAL_HOURS = 4   # auto-scrape every N hours
MIN_RELEVANCE_SCORE   = 5   # only alert if score >= this (1–10)
DELAY_BETWEEN_SITES   = 3   # seconds pause between different sites