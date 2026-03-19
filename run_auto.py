"""
run_auto.py — Non-interactive daily runner for MoneyPrinter.
Runs the full campaign (all 29 cities) without any user prompts.
Skips businesses already contacted (emails/phones in logs/sent.csv).

Cron job (VPS, UTC): 0 7 * * * cd /root/moneyprinter && python3 run_auto.py >> /root/moneyprinter/logs/cron.log 2>&1
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Force UTF-8 output
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print(f"[AUTO] Starting full campaign — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

from outreach import run_outreach

run_outreach()

print(f"[AUTO] Done — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
