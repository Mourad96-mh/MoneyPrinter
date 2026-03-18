import os
import re
import sys
import csv
import json
import time
import subprocess
import yagmail
import requests
from datetime import datetime
from urllib.parse import quote

# Force UTF-8 output on Windows terminals
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_template(language: str, channel: str = "email") -> str:
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    ext = "html" if channel == "email" else "txt"
    template_file = os.path.join(templates_dir, f"{channel}_{language}.{ext}")
    if not os.path.exists(template_file):
        raise FileNotFoundError(f"Template not found: {template_file}")
    with open(template_file, "r", encoding="utf-8") as f:
        return f.read()


def fill_template(template: str, company_name: str, config: dict) -> str:
    return (
        template
        .replace("{{COMPANY_NAME}}", company_name)
        .replace("{{SENDER_NAME}}", config.get("sender_name", "MouDev Pro"))
        .replace("{{AGENCY_WEBSITE}}", config.get("agency_website", ""))
        .replace("{{AGENCY_PHONE}}", config.get("agency_phone", ""))
    )


_JUNK_DOMAINS = {
    "sentry.io", "sentry-next.wixpress.com", "wixpress.com",
    "example.com", "test.com", "schema.org", "w3.org",
    "amazonaws.com", "cloudfront.net", "googleapis.com",
}
_UUID_RE = re.compile(r"^[0-9a-f]{8,}[0-9a-f\-]{4,}@", re.I)


def _is_junk_email(email: str) -> bool:
    domain = email.split("@")[-1].lower()
    if domain in _JUNK_DOMAINS:
        return True
    if any(domain.endswith("." + d) for d in _JUNK_DOMAINS):
        return True
    if _UUID_RE.match(email):
        return True
    return False


def extract_email_from_website(website: str) -> str:
    try:
        r = requests.get(website, timeout=10)
        if r.status_code == 200:
            pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
            matches = re.findall(pattern, r.text)
            ignored_ext = {"png", "jpg", "jpeg", "gif", "svg", "webp", "woff", "woff2"}
            matches = [
                m for m in matches
                if m.split(".")[-1].lower() not in ignored_ext
                and not _is_junk_email(m)
            ]
            if matches:
                return matches[0]
    except Exception:
        pass
    return ""


def normalize_phone(raw: str) -> str:
    """Normalize a Moroccan phone number to E.164 format (+212XXXXXXXXX)."""
    digits = re.sub(r"[^\d+]", "", raw)
    # Already has country code
    if digits.startswith("+212"):
        return digits
    if digits.startswith("00212"):
        return "+" + digits[2:]
    # Local format: 0XXXXXXXXX → +212XXXXXXXXX
    if digits.startswith("0") and len(digits) == 10:
        return "+212" + digits[1:]
    return digits


_WHATSAPP_PROFILE = os.path.expanduser("~/.config/chrome-whatsapp")


def _ensure_xvfb():
    """Start Xvfb on :99 if no display is set (VPS mode)."""
    if os.environ.get("DISPLAY"):
        return
    try:
        subprocess.Popen(
            ["Xvfb", ":99", "-screen", "0", "1280x800x24", "-ac"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)
        os.environ["DISPLAY"] = ":99"
    except FileNotFoundError:
        pass  # Xvfb not installed — Chrome may still work


def init_wa_driver():
    """Open WhatsApp Web with persistent profile. Returns driver or None if not logged in."""
    _ensure_xvfb()
    options = Options()
    options.add_argument(f"--user-data-dir={_WHATSAPP_PROFILE}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1280,800")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.get("https://web.whatsapp.com")
    print("[WA] Loading WhatsApp Web...")
    for _ in range(30):
        time.sleep(1)
        # QR shown = not logged in
        if driver.find_elements(By.CSS_SELECTOR, "canvas[aria-label='Scan me!'], div[data-testid='qrcode'] canvas"):
            print("[WA ERROR] Not logged in — run: python3 setup_whatsapp.py")
            driver.quit()
            return None
        # Chat list visible = logged in
        if driver.find_elements(By.CSS_SELECTOR, "div[data-testid='chat-list'], div[aria-label='Chat list'], #side"):
            print("[WA] Logged in OK")
            return driver
    print("[WA ERROR] WhatsApp Web failed to load")
    driver.quit()
    return None


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=fr-MA")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def accept_cookies(driver):
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Tout accepter") or contains(., "Accept all") or contains(., "Accepter")]'))
        )
        btn.click()
        time.sleep(1)
    except Exception:
        pass


def scrape_google_maps(query: str, max_results: int = 20) -> list:
    driver = get_driver()
    businesses = []

    try:
        url = f"https://www.google.com/maps/search/{quote(query)}?hl=fr&gl=ma"
        driver.get(url)
        time.sleep(5)

        accept_cookies(driver)
        time.sleep(2)

        # Save debug screenshot for first query
        try:
            driver.save_screenshot("/tmp/maps_debug.png")
        except Exception:
            pass

        # Scroll the results panel to load more listings
        try:
            feed = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
            )
            for _ in range(5):
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                time.sleep(1.5)
        except Exception:
            pass

        # Collect all result links
        result_links = driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] a[href*="/maps/place/"]')
        result_links = result_links[:max_results]
        print(f"[INFO] Found {len(result_links)} listings for: {query}")

        for i, link in enumerate(result_links):
            try:
                driver.execute_script("arguments[0].click();", link)
                time.sleep(2.5)

                # Get business name from the detail panel
                name = ""
                for sel in [
                    "h1.DUwDvf",
                    "h1.fontHeadlineLarge",
                    '[class*="fontHeadlineLarge"]',
                    'div[role="main"] h1',
                ]:
                    try:
                        el = WebDriverWait(driver, 4).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                        )
                        candidate = el.text.strip()
                        if candidate and candidate.lower() not in ("résultats", "results", "resultats"):
                            name = candidate
                            break
                    except Exception:
                        pass

                if not name:
                    continue

                # Get website
                website = ""
                try:
                    website_el = driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
                    website = website_el.get_attribute("href") or ""
                except Exception:
                    pass

                # Get phone number (stored directly in data-item-id as "phone:tel:+212...")
                phone = ""
                try:
                    phone_el = driver.find_element(By.CSS_SELECTOR, '[data-item-id^="phone:tel:"]')
                    raw = phone_el.get_attribute("data-item-id").replace("phone:tel:", "")
                    phone = normalize_phone(raw)
                except Exception:
                    pass

                businesses.append({"name": name, "website": website, "phone": phone})
                print(f"  [{i+1}] {name} | {phone or 'no phone'} | {website or 'no website'}")

            except Exception as e:
                err_msg = str(e).splitlines()[0]  # first line only, no giant stacktrace
                print(f"  [SKIP] Listing {i+1}: {err_msg}")
                # If the session is dead, restart the driver and re-navigate
                if "invalid session id" in str(e).lower():
                    print(f"  [RECOVER] Session died — restarting driver at listing {i+1}")
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    driver = get_driver()
                    driver.get(url)
                    time.sleep(3)
                    accept_cookies(driver)
                    time.sleep(1)
                    try:
                        feed = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
                        )
                        for _ in range(5):
                            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                            time.sleep(1.5)
                    except Exception:
                        pass
                    result_links = driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] a[href*="/maps/place/"]')
                    result_links = result_links[:max_results]
                continue

    except Exception as e:
        print(f"[ERROR] Scraping failed for '{query}': {e}")
    finally:
        driver.quit()

    return businesses


def send_whatsapp_message(driver, phone: str, message: str) -> bool:
    """Send a WhatsApp message via WhatsApp Web using a persistent Selenium session."""
    from selenium.webdriver.common.keys import Keys
    try:
        phone_digits = phone.lstrip("+")
        url = f"https://web.whatsapp.com/send?phone={phone_digits}&text={quote(message)}"
        driver.get(url)
        time.sleep(3)

        # Dismiss "Continue to chat" popup if it appears
        for popup_sel in [
            'a[href*="open?phone"]',
            'div[data-testid="popup-contents"] button',
            'button[data-testid="popup-btn-ok"]',
        ]:
            try:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, popup_sel))
                )
                btn.click()
                time.sleep(2)
                break
            except Exception:
                pass

        # Wait for send button — try multiple selectors
        send_btn = None
        for sel in [
            'button[data-testid="send"]',
            'span[data-icon="send"]',
            'button[aria-label="Envoyer"]',
            'button[aria-label="Send"]',
            '[data-testid="compose-btn-send"]',
        ]:
            try:
                send_btn = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                )
                break
            except Exception:
                pass

        # Fallback: press Enter in the message input box
        if send_btn is None:
            for input_sel in [
                'div[data-testid="conversation-compose-box-input"]',
                'div[contenteditable="true"][data-tab="10"]',
                'footer div[contenteditable="true"]',
            ]:
                try:
                    input_box = driver.find_element(By.CSS_SELECTOR, input_sel)
                    input_box.send_keys(Keys.ENTER)
                    time.sleep(2)
                    print(f"[WA SENT via Enter] {phone}")
                    return True
                except Exception:
                    pass
            print(f"[WA ERROR] Send button not found for {phone}")
            return False

        send_btn.click()
        time.sleep(2)
        return True
    except Exception as e:
        print(f"[WA ERROR] {phone}: {str(e).splitlines()[0]}")
        return False


def build_niches(config: dict) -> list:
    cities = config.get("cities", [])
    business_types = config.get("business_types", [])
    legacy = config.get("niches", [])
    combinations = [f"{btype} {city}" for city in cities for btype in business_types]
    return combinations + legacy


LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "sent.csv")
LOG_FIELDS = ["timestamp", "channel", "company", "email", "phone", "niche", "website"]


def _init_log():
    log_dir = os.path.dirname(LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=LOG_FIELDS).writeheader()


def _log(channel: str, company: str, email: str, phone: str, niche: str, website: str):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=LOG_FIELDS).writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "channel": channel,
            "company": company,
            "email": email,
            "phone": phone,
            "niche": niche,
            "website": website,
        })


def _load_already_contacted() -> tuple[set, set]:
    """Load previously contacted emails and phones from the log file."""
    emails, phones = set(), set()
    if not os.path.exists(LOG_FILE):
        return emails, phones
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("email"):
                emails.add(row["email"])
            if row.get("phone"):
                phones.add(row["phone"])
    return emails, phones


def run_outreach(cities_override: list = None):
    config = load_config()
    if cities_override:
        config = {**config, "cities": cities_override}
    niches = build_niches(config)
    language = config.get("email_language", "fr")
    delay = config.get("delay_between_emails_seconds", 5)
    whatsapp_delay = config.get("delay_between_whatsapp_seconds", 20)
    enable_whatsapp = config.get("enable_whatsapp", False)
    email_config = config.get("email", {})
    max_results_per_niche = config.get("max_results_per_niche", 20)
    subject_fr = "Votre présence en ligne au Maroc — une opportunité à ne pas manquer"
    subject_ar = "حضوركم الرقمي في المغرب — فرصة لا تفوّت"
    subject = subject_fr if language == "fr" else subject_ar

    _init_log()
    already_emailed, already_whatsapped = _load_already_contacted()
    print(f"[INFO] Total combinations: {len(niches)} "
          f"({len(config.get('business_types', []))} types × {len(config.get('cities', []))} cities)")
    print(f"[INFO] Already contacted: {len(already_emailed)} emails, {len(already_whatsapped)} phones (from previous runs)")
    print(f"[INFO] WhatsApp: {'ENABLED' if enable_whatsapp else 'DISABLED'}")

    # Setup email client (port 587 = STARTTLS, port 465 = SSL)
    port = email_config.get("smtp_port", 587)
    yag = yagmail.SMTP(
        user=email_config["username"],
        password=email_config["password"],
        host=email_config.get("smtp_server", "smtp.gmail.com"),
        port=port,
        smtp_ssl=(port == 465),
    )

    email_template = load_template(language, channel="email")
    wa_template = load_template(language, channel="whatsapp") if enable_whatsapp else None

    # Init one WhatsApp driver for the whole session (avoids reopening Chrome per message)
    wa_driver = None
    if enable_whatsapp:
        wa_driver = init_wa_driver()
        if wa_driver is None:
            enable_whatsapp = False

    total_emails = 0
    total_wa = 0

    try:
        for niche in niches:
            print(f"\n[SEARCH] {niche}")
            businesses = scrape_google_maps(niche, max_results=max_results_per_niche)

            for biz in businesses:
                company_name = biz.get("name", "")
                website = biz.get("website", "")
                phone = biz.get("phone", "")

                # --- Email ---
                email = ""
                if website and website.startswith("http"):
                    email = extract_email_from_website(website)

                if email and "@" in email and email not in already_emailed:
                    body = fill_template(email_template, company_name, config)
                    try:
                        yag.send(to=email, subject=subject, contents=body)
                        print(f"[EMAIL SENT] {company_name} <{email}>")
                        already_emailed.add(email)
                        _log("email", company_name, email, phone, niche, website)
                        total_emails += 1
                        time.sleep(delay)
                    except Exception as e:
                        print(f"[EMAIL ERROR] {email}: {e}")
                else:
                    if not email:
                        print(f"[SKIP EMAIL] No email: {company_name}")

                # --- WhatsApp ---
                if enable_whatsapp and wa_driver and phone and phone not in already_whatsapped:
                    wa_body = fill_template(wa_template, company_name, config)
                    if send_whatsapp_message(wa_driver, phone, wa_body):
                        print(f"[WA SENT] {company_name} <{phone}>")
                        already_whatsapped.add(phone)
                        _log("whatsapp", company_name, "", phone, niche, website)
                        total_wa += 1
                        time.sleep(whatsapp_delay)
                elif enable_whatsapp and not phone:
                    print(f"[SKIP WA] No phone: {company_name}")

    finally:
        if wa_driver:
            wa_driver.quit()

    print(f"\n[DONE] Emails sent: {total_emails} | WhatsApp sent: {total_wa}")
    print(f"[LOG] Saved to: {os.path.abspath(LOG_FILE)}")
