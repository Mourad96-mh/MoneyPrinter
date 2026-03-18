import os
import sys
import json
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Force UTF-8 output on Windows terminals
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def check_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        example_path = os.path.join(os.path.dirname(__file__), "config.example.json")
        shutil.copy(example_path, config_path)
        print("[SETUP] config.json created from example.")
        print("[SETUP] Please fill in your credentials in config.json before running again.")
        sys.exit(0)
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    email = config.get("email", {})
    if not email.get("username") or email.get("username") == "your_gmail@gmail.com":
        print("[ERROR] Please fill in your Gmail credentials in config.json")
        sys.exit(1)
    return config


def main():
    print("=" * 50)
    print("  MoneyPrinter — MouDev Edition")
    print("  Automated Client Outreach for moudevpro.com")
    print("=" * 50)
    print()

    check_config()

    print("What do you want to do?")
    print()
    print("  [1] Pilot mode — Casablanca only (test before full campaign)")
    print("  [2] Full campaign — all 29 cities")
    print("  [3] Exit")
    print()

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        from outreach import run_outreach
        print("\n[PILOT] Running Casablanca only — 73 business types")
        run_outreach(cities_override=["Casablanca"])
    elif choice == "2":
        from outreach import run_outreach
        confirm = input("This will contact thousands of businesses. Type YES to confirm: ").strip()
        if confirm == "YES":
            run_outreach()
        else:
            print("Cancelled.")
    elif choice == "3":
        print("Bye!")
        sys.exit(0)
    else:
        print("[ERROR] Invalid choice.")
        main()


if __name__ == "__main__":
    main()
