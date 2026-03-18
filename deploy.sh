#!/bin/bash
# deploy.sh — Run this ONCE on a fresh Ubuntu 22.04/24.04 VPS
# Usage: bash deploy.sh
# Then edit config.json with your Gmail credentials

set -e

echo "============================================"
echo "  MoneyPrinter — VPS Setup"
echo "============================================"

# 1. System update + Chrome
echo "[1/5] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip git wget gnupg unzip curl xvfb

echo "[2/5] Installing Google Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y -qq ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# 2. Python dependencies
echo "[3/5] Installing Python packages..."
pip3 install -q --break-system-packages yagmail requests selenium webdriver-manager premailer

# 3. Project setup
echo "[4/5] Setting up project..."
INSTALL_DIR="/root/MoneyPrinter"

if [ -d "$INSTALL_DIR" ]; then
  echo "  Directory exists — pulling latest changes..."
  cd "$INSTALL_DIR" && git pull
else
  echo "  Cloning repo..."
  git clone https://github.com/Mourad96-mh/MoneyPrinter.git "$INSTALL_DIR"
fi

# 4. Config check
if [ ! -f "$INSTALL_DIR/config.json" ]; then
  cp "$INSTALL_DIR/config.example.json" "$INSTALL_DIR/config.json"
  echo ""
  echo "  [!] config.json created — FILL IN YOUR CREDENTIALS:"
  echo "      nano $INSTALL_DIR/config.json"
fi

# 5. Cron job — runs full campaign every day at 3:00 AM
echo "[5/5] Setting up daily cron job..."
CRON_JOB="0 3 * * * /usr/bin/python3 $INSTALL_DIR/run.py --full >> $INSTALL_DIR/logs/cron.log 2>&1"
(crontab -l 2>/dev/null | grep -v "MoneyPrinter\|run.py"; echo "$CRON_JOB") | crontab -

echo ""
echo "============================================"
echo "  Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Edit config.json:      nano $INSTALL_DIR/config.json"
echo "  2. Setup WhatsApp (once): python3 $INSTALL_DIR/setup_whatsapp.py"
echo "  3. Test it:               python3 $INSTALL_DIR/run.py --pilot"
echo "  4. It will auto-run every night at 3:00 AM"
echo ""
echo "  View logs:  tail -f $INSTALL_DIR/logs/cron.log"
echo "  Edit cron:  crontab -e"
echo "============================================"
