# ------------------------------------------------------
# 🧠 MIDAS LIVE TRADING BOT (PAPER MODE)
# ------------------------------------------------------

import os
import ccxt
import time
import json
import requests
from datetime import datetime, timezone  # ✅ fixed timezone import


# ------------------------------------------------------
# ⚙️ CONFIGURATION
# ------------------------------------------------------
MODE = "PAPER"
PAIR = "SOL/USDT"
INTERVAL = 60  # seconds

# Telegram credentials
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")


# ------------------------------------------------------
# 💬 Telegram Alerts
# ------------------------------------------------------
def send_telegram_message(message):
    """Send Telegram message for bot updates and errors."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[⚠️] Telegram send failed: {e}")


# ------------------------------------------------------
# 🌐 Exchange Setup
# ------------------------------------------------------
try:
    exchanges = {
        "bybit": ccxt.bybit(),
        "mexc": ccxt.mexc(),
    }
except Exception as e:
    print(f"[❌] Error initializing exchanges: {e}")
    send_telegram_message(f"[❌] Error initializing exchanges: {e}")
    raise


# ------------------------------------------------------
# 📊 Monitoring Loop with Failover
# ------------------------------------------------------
def monitor_with_failover(pairs=[PAIR], interval=INTERVAL):
    """Continuously monitor prices and auto-switch exchanges on failure."""

    while True:
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            for pair in pairs:
                for ex_name, ex in exchanges.items():
                    try:
                        ticker = ex.fetch_ticker(pair)
                        price = ticker["last"]
                        print(f"[{timestamp}] {pair} on {ex_name.upper()}: ${price:.2f}")
                    except Exception as sub_e:
                        print(f"[⚠️] Failed to fetch {pair} on {ex_name.upper()}: {sub_e}")
                        continue

            # 💗 Heartbeat notification
            send_telegram_message(
                f"💗 MIDAS {MODE.upper()} Bot alive at {timestamp}. Still monitoring {PAIR} on both BYBIT & MEXC."
            )
            time.sleep(interval)

        except Exception as e:
            print(f"[❌] Major error in monitor loop: {e}")
            send_telegram_message(f"[🔥] MIDAS Error: {e}")
            time.sleep(10)


# ------------------------------------------------------
# 🚀 Entry Point
# ------------------------------------------------------
if __name__ == "__main__":
    print(f"🚀 Starting MIDAS {MODE.upper()} Trading Bot (Paper Mode on Render)...")
    monitor_with_failover()

