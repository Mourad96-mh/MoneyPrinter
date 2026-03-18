# MoneyPrinter — MouDev Edition

Adapting [MoneyPrinterV2](https://github.com/FujiwaraChoki/MoneyPrinterV2) to scale [moudevpro.com](https://www.moudevpro.com/) — a digital agency based in Casablanca, Morocco.

---

## Current Marketing Setup

| Channel | Status | Purpose |
|---|---|---|
| Google Ads | ✅ Active + conversion tracking done | Paid lead generation |
| Google Business Profile | ✅ Created | Local SEO, Google Maps visibility |
| Facebook Page | ✅ Created | Social proof, organic reach |

---

## Progress

### ✅ Done — Option 1: Google Ads Conversion Tracking
- Conversion tracking set up and verified on moudevpro.com
- Tracks calls, form submissions, and WhatsApp clicks

### ✅ Done — Option 2: Local Business Outreach Bot
Fully built and ready to run.

**How it works:**
- Combines **73 business types × 29 Moroccan cities = 2,117 search queries**
- Scrapes Google Maps for businesses using a Go-based scraper
- Visits each business website to find their email address
- Sends a personalized cold email in French (or Arabic) via Gmail
- Skips duplicates automatically

**Files:**
```
main.py                  ← entry point: python main.py
config.json              ← your credentials (gitignored)
config.example.json      ← template for sharing
src/outreach.py          ← full outreach engine
templates/email_fr.html  ← French cold email
templates/email_ar.html  ← Arabic cold email
HOW_IT_WORKS.md          ← full explanation of the process
```

**Cities covered (29):**
Casablanca, Rabat, Marrakech, Fès, Tanger, Agadir, Meknès, Oujda, Kénitra, Tétouan,
Salé, Mohammedia, El Jadida, Béni Mellal, Nador, Safi, Settat, Khouribga, Larache,
Khémisset, Taza, Berkane, Ksar el-Kébir, Errachidia, Guelmim, Ouarzazate, Tiznit, Dakhla, Laâyoune

**Business sectors targeted:**
Food & Beverage, Health & Medical, Beauty & Wellness, Education, Home Services,
Automotive, Retail, Professional Services, Real Estate, Events, Transport

**To run:**
```bash
pip install -r requirements.txt
python main.py
```

---

### 🔲 Next — Option 3: Auto-Post Content to Facebook Page + Google Business Profile

**Goal:** Keep Facebook Page and GBP active automatically without manual work.

**What to build:**
- AI generates short digital marketing tips in French/Arabic (using free API)
- Auto-posts to **Facebook Page** on a schedule (3x per week)
- Auto-posts to **Google Business Profile** as weekly updates
- Content ideas: SEO tips, before/after websites, Google Ads advice, client results

**Why it matters:**
- GBP posts boost local SEO ranking
- Facebook posts build social proof for prospects who check the page before contacting
- Zero manual effort once set up

**Stack needed:**
- Facebook Graph API (free, needs Facebook Developer account)
- Google My Business API (free, needs Google Cloud account)
- OpenAI or Gemini API for content generation

---

### 🔲 Future — Option 4: YouTube Shorts Automation
Auto-generate short videos in French/Arabic positioning MouDev as the go-to web agency in Morocco.

### 🔲 Future — Option 5: Sell Automation as a Service
White-label this toolkit as an add-on service for SME clients — automated content marketing and lead generation.

---

## Roadmap

- [x] Google Ads conversion tracking verified
- [x] Google Business Profile created
- [x] Facebook Page created
- [x] Local Business Outreach bot built (73 types × 29 cities)
- [x] French + Arabic email templates written
- [x] Gmail App Password configured
- [x] Go installed and scraper ready
- [ ] Run first outreach campaign and track replies
- [ ] Build Facebook Page auto-poster
- [ ] Build Google Business Profile auto-poster
- [ ] Set up content generation (French/Arabic tips)
- [ ] YouTube Shorts pipeline

---

## Resources

- MoneyPrinterV2 repo: https://github.com/FujiwaraChoki/MoneyPrinterV2
- MouDev website: https://www.moudevpro.com/
- How the bot works: [HOW_IT_WORKS.md](HOW_IT_WORKS.md)
