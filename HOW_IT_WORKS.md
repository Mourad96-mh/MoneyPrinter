# How the Outreach Bot Works

## The Big Picture

The bot does automatically what you would normally do manually:
find businesses → get their email → send them a pitch.

```
config.json (your settings)
        ↓
Step 1: Generate search queries
        ↓
Step 2: Scrape Google Maps for businesses
        ↓
Step 3: Find their email address
        ↓
Step 4: Send personalized cold email
        ↓
Repeat for every city × every business type
```

---

## Step by Step

### Step 1 — Generate Search Queries

The bot reads your `config.json` and combines every business type with every city:

```
"restaurant"  +  "Casablanca"  →  "restaurant Casablanca"
"restaurant"  +  "Rabat"       →  "restaurant Rabat"
"dentiste"    +  "Casablanca"  →  "dentiste Casablanca"
"dentiste"    +  "Marrakech"   →  "dentiste Marrakech"
...and so on
```

With 73 business types × 29 cities = **2,117 search queries** total.

---

### Step 2 — Scrape Google Maps

For each search query, the bot runs a tool called **Google Maps Scraper**
(written in Go, that's why we installed Go).

This scraper searches Google Maps exactly like you would manually,
and collects business information into a CSV file:

```
name              | address          | website              | phone
------------------|------------------|----------------------|----------
Cabinet Dentaire  | Bd Hassan II,    | www.cabinet-x.ma    | 0522-xxx
Dr. Alami         | Casablanca       |                      | 0661-xxx
Clinique Salam    | Rue Omar...      |                      | 0522-xxx
```

---

### Step 3 — Find the Email Address

The scraper gives us the business website URL.
The bot then visits each website and scans the page for an email address
(looks for anything that matches `@` pattern like `contact@business.ma`).

```
Visit www.cabinet-x.ma
        ↓
Scan the page HTML
        ↓
Find: contact@cabinet-x.ma ✅
```

If no email is found → the business is skipped.

---

### Step 4 — Send the Cold Email

Once an email is found, the bot:
1. Opens your Gmail (using the App Password you set up)
2. Loads the French email template from `templates/email_fr.html`
3. Replaces the placeholders with real data:
   - `{{COMPANY_NAME}}` → "Cabinet Dentaire Dr. Alami"
   - `{{SENDER_NAME}}` → "Mourad - MouDev Pro"
   - `{{AGENCY_WEBSITE}}` → "https://www.moudevpro.com"
   - `{{AGENCY_PHONE}}` → "+212 754-610009"
4. Sends the email
5. Waits 5 seconds (to avoid Gmail blocking)
6. Moves to the next business

```
Template:
"Bonjour, j'ai remarqué que {{COMPANY_NAME}} n'a pas de site web..."

Becomes:
"Bonjour, j'ai remarqué que Cabinet Dentaire Dr. Alami n'a pas de site web..."
```

---

### Anti-Duplicate Protection

The bot keeps track of every email it has already sent to.
If the same business appears in two different search queries,
it won't send them two emails — it skips them automatically.

---

## What Happens After It Runs?

- The bot prints every action in the terminal: `[SENT]`, `[SKIP]`, `[ERROR]`
- CSV files are saved locally with all scraped business data
- You start receiving replies in your Gmail inbox from interested businesses

---

## File Structure

```
MoneyPrinter/
├── main.py                  ← Start here: python main.py
├── config.json              ← Your credentials + cities + business types
├── config.example.json      ← Template (safe to share, no credentials)
├── requirements.txt         ← Python dependencies
├── src/
│   └── outreach.py          ← The brain: all the logic lives here
└── templates/
    ├── email_fr.html        ← French email sent to businesses
    └── email_ar.html        ← Arabic version (optional)
```

---

## Summary

| What | Who does it |
|---|---|
| Generate search queries | Python (config.json) |
| Search Google Maps | Go scraper binary |
| Find emails on websites | Python (requests + regex) |
| Send emails | Python (yagmail + Gmail SMTP) |
| Avoid duplicates | Python (in-memory set) |

The whole process runs automatically. You just launch it and wait for replies.
