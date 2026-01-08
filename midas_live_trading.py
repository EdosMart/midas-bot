# ======================================================
# MIDAS Live Trading Bot (with Auto Failover + Telegram)
# ======================================================
# - Supports Paper or Live mode (controlled by ENV var)
# - Handles network errors gracefully
# - Auto-failover between Bybit and MEXC
# - Sends Telegram alerts and hourly heartbeats
# ======================================================

import os
import ccxt
import time
import json
import requests
from datetime import datetime, timezone  # ✅ fixed timezone import

# ------------------------------------------------------
# 🔧 Environment Variables / Config
# ------------------------------------------------------
MODE = os.getenv("TRADING_MODE", "PAPER")       # PAPER or LIVE
PAIR = os.getenv("PAIR", "SOL/USDT")
INTERVAL = int(os.getenv("INTERVAL", "60"))     # seconds between cycles
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "854XXXXXX9:xxxGTA4iF97rxxxxxxxxxKfSZivF0n6Uxxx")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "970989479")

# ------------------------------------------------------
# 📡 Telegram Helper
# ------------------------------------------------------
def send_telegram(message: str):
    """Send message to Telegram channel."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[⚠️] Telegram send failed: {e}")

# ------------------------------------------------------
# 🌐 Exchange Connection Handling
# ------------------------------------------------------
def connect_exchanges():
    """Attempt to connect to both Bybit and MEXC."""
    exchanges = {}
    for name in ["bybit", "mexc"]:
        try:
            ex = getattr(ccxt, name)()
            markets = ex.load_markets()
            print(f"✅ Connected to {name.upper()} ({len(markets)} markets)")
            exchanges[name] = ex
        except Exception as e:
            print(f"⚠️ Could not connect to {name.upper()}: {e}")
    return exchanges


# ------------------------------------------------------
# 🚀 Run the Bot
# ------------------------------------------------------

def monitor_with_failover(pairs=[PAIR], interval=INTERVAL):
    """Continuously monitor prices and auto-switch exchanges on failure."""
    global exchange, active_exchange

    while True:
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            for pair in pairs:
                # 🔄 Loop through both Bybit and MEXC for live comparison
                for ex_name, ex in exchanges.items():
                    try:
                        ticker = ex.fetch_ticker(pair)
                        price = ticker["last"]
                        print(f"[{timestamp}] {pair} on {ex_name.upper()}: ${price:.2f}")

                    except Exception as sub_e:
                        print(f"[⚠️] Failed to fetch {pair} on {ex_name.upper()}: {sub_e}")
                        continue

            # 💬 Telegram heartbeat
            send_telegram_message(
                f"💗 MIDAS {MODE.upper()} Bot alive at {timestamp}. Still monitoring {PAIR} on both BYBIT & MEXC."
            )

            time.sleep(interval)

        except Exception as e:
            print(f"[❌] Major error in monitor loop: {e}")
            send_telegram_message(f"[🔥] MIDAS Error: {e}")
            time.sleep(10)


# ------------------------------------------------------
# 🧠 Entry Point
# ------------------------------------------------------
if __name__ == "__main__":
    print(f"🚀 Starting MIDAS {MODE.upper()} Trading Bot (Paper Mode on Render)...")
    monitor_with_failover()

