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
# 💹 Monitoring Loop (with Failover)
# ------------------------------------------------------
def monitor_with_failover(pair=PAIR, interval=INTERVAL):
    """Continuously monitor prices and auto-switch exchanges on failure."""
    exchanges = connect_exchanges()

    if not exchanges:
        print("❌ No exchanges available. Halting bot.")
        send_telegram("❌ MIDAS Bot failed to connect to any exchange. Shutting down.")
        return

    active_exchange_name = next(iter(exchanges))
    exchange = exchanges[active_exchange_name]
    ticker = None  # ✅ ensures variable is defined

    send_telegram(f"🚀 MIDAS {MODE} Bot started — monitoring {pair} on {active_exchange_name.upper()}.")

    last_heartbeat = time.time()

    while True:
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            try:
                ticker = exchange.fetch_ticker(pair)
            except Exception as fetch_err:
                print(f"[⚠️] Fetch error on {active_exchange_name.upper()}: {fetch_err}")
                ticker = None

            if not ticker:
                print(f"[⚠️] No data for {pair} on {active_exchange_name.upper()}. Switching exchange...")
                # Auto-failover
                other = "mexc" if active_exchange_name == "bybit" else "bybit"
                if other in exchanges:
                    active_exchange_name = other
                    exchange = exchanges[other]
                    send_telegram(f"[🔁] Switched to {other.upper()} due to data issues.")
                    continue
                else:
                    send_telegram("❌ Both exchanges unreachable. Retrying in 60s...")
                    time.sleep(60)
                    continue

            price = ticker["last"]
            print(f"[{timestamp}] {pair} price: ${price:.2f}")

            # 🧠 Simulated Trade Logic (extend later)
            print(f"[{timestamp}] Checking {pair} on {active_exchange_name.upper()}...")

            # 🕒 Hourly heartbeat
            if time.time() - last_heartbeat >= 3600:
                send_telegram(f"💓 MIDAS {MODE} Bot alive at {timestamp}. Still monitoring {pair}.")
                last_heartbeat = time.time()

            time.sleep(interval)

        except Exception as e:
            print(f"[❌] Major error in loop: {e}")
            send_telegram(f"⚠️ MIDAS Bot encountered error: {e}")
            time.sleep(10)

# ------------------------------------------------------
# 🚀 Run the Bot
# ------------------------------------------------------
if __name__ == "__main__":
    print(f"🚀 Starting MIDAS {MODE} Trading Bot (Paper Mode on Render)...")
    monitor_with_failover()

