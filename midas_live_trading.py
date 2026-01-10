import os
import ccxt
import time
import json
import requests
from datetime import datetime, timezone

# ------------------------------------------------------
# 🩺 MIDAS Startup Health Check
# ------------------------------------------------------

print("🔍 Running MIDAS startup health check...")

required_env_vars = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "MODE",
    "PAIR"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
else:
    print("✅ All required environment variables found.")

print("🚀 Continuing to initialize MIDAS bot...\n")

# ------------------------------------------------------
# ⚙️ Load Environment Variables
# ------------------------------------------------------

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PAIR = os.getenv("PAIR", "SOL/USDT")
MODE = os.getenv("MODE", "Paper")
INTERVAL = int(os.getenv("INTERVAL", "60"))

# ------------------------------------------------------
# 🔔 Telegram Notification
# ------------------------------------------------------
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")

# ------------------------------------------------------
# 📈 Exchange Setup
# ------------------------------------------------------
exchange = ccxt.bybit({"enableRateLimit": True})
print(f"🪙 Monitoring {PAIR} on Bybit in {MODE} mode")

send_telegram_message(f"🤖 MIDAS Bot started in {MODE} mode — tracking {PAIR}")

# ------------------------------------------------------
# 🔁 Live Monitoring Loop
# ------------------------------------------------------
while True:
    try:
        ticker = exchange.fetch_ticker(PAIR)
        last_price = ticker["last"]
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {PAIR}: {last_price}")
        time.sleep(INTERVAL)
    except Exception as e:
        print(f"⚠️ Error fetching price: {e}")
        time.sleep(10)