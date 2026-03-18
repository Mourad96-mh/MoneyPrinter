"""
run.py — non-interactive runner for cron / VPS
Usage:
  python run.py --pilot        # Casablanca only (test)
  python run.py --full         # All 29 cities
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(description="MoneyPrinter — MouDev Outreach Bot")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pilot", action="store_true", help="Casablanca only (test run)")
    group.add_argument("--full", action="store_true", help="Full campaign — all cities")
    args = parser.parse_args()

    from outreach import run_outreach

    if args.pilot:
        print("[PILOT] Running Casablanca only", flush=True)
        run_outreach(cities_override=["Casablanca"])
    elif args.full:
        print("[FULL] Running all cities", flush=True)
        run_outreach()


if __name__ == "__main__":
    main()
