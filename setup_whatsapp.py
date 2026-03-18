"""
setup_whatsapp.py — Run ONCE on the VPS to log in to WhatsApp Web.
The session is saved in ~/.config/chrome-whatsapp so the bot never
needs to scan the QR code again (until WhatsApp logs you out).

Usage:
    python3 setup_whatsapp.py
"""
import os
import sys
import time
import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

_WHATSAPP_PROFILE = os.path.expanduser("~/.config/chrome-whatsapp")
_QR_SCREENSHOT = "/tmp/whatsapp_qr.png"


def main():
    print("=" * 52)
    print("  WhatsApp Web — One-Time Login Setup")
    print("=" * 52)

    # Start Xvfb virtual display
    print("\n[1/3] Starting virtual display (Xvfb)...")
    xvfb = subprocess.Popen(
        ["Xvfb", ":99", "-screen", "0", "1280x800x24", "-ac"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    os.environ["DISPLAY"] = ":99"
    time.sleep(1)

    print("[2/3] Opening WhatsApp Web with persistent profile...")
    options = Options()
    options.add_argument(f"--user-data-dir={_WHATSAPP_PROFILE}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.get("https://web.whatsapp.com")
    time.sleep(5)

    # Already logged in?
    if driver.find_elements(By.CSS_SELECTOR, "div[data-testid='chat-list'], div[aria-label='Chat list'], #side"):
        print("\n[OK] Already logged in — nothing to do!")
        driver.quit()
        xvfb.terminate()
        return

    # Take QR screenshot
    print("[3/3] Saving QR code screenshot...")
    driver.save_screenshot(_QR_SCREENSHOT)
    print()
    print("  ┌─────────────────────────────────────────────┐")
    print(f"  │  QR saved to: {_QR_SCREENSHOT:<29} │")
    print("  │                                             │")
    print("  │  Download it on your PC with:              │")
    print(f"  │  scp root@YOUR_VPS_IP:{_QR_SCREENSHOT}  . │")
    print("  │                                             │")
    print("  │  Then open whatsapp_qr.png and scan it     │")
    print("  │  with WhatsApp on your phone.              │")
    print("  └─────────────────────────────────────────────┘")
    print()
    print("  Waiting for scan... (Ctrl+C to cancel)\n")

    # Refresh screenshot every 15s and poll for login
    for i in range(120):
        time.sleep(2)
        try:
            if driver.find_elements(By.CSS_SELECTOR, "div[data-testid='chat-list'], div[aria-label='Chat list'], #side"):
                print("\n[OK] Logged in! Session saved to ~/.config/chrome-whatsapp")
                print("     The bot will now send WhatsApp messages automatically.")
                driver.quit()
                xvfb.terminate()
                return
        except Exception:
            pass
        # Refresh screenshot every ~30s so the QR stays scannable
        if i > 0 and i % 15 == 0:
            try:
                driver.save_screenshot(_QR_SCREENSHOT)
                print(f"  QR refreshed ({i * 2}s elapsed) — download again if it expired")
            except Exception:
                pass

    print("\n[ERROR] Timed out waiting for scan (4 minutes).")
    print("        Run setup_whatsapp.py again to retry.")
    driver.quit()
    xvfb.terminate()


if __name__ == "__main__":
    main()
