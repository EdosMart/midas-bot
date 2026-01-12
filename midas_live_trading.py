# ============================================================
# 🤖 MIDAS LIVE TRADING BOT (Bybit + Telegram)
# Clean Production Version (2026)
# ============================================================

import os
import time
import ccxt
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# ------------------------------------------------------------
# 🌍 Load Environment Variables (works locally + on Render)
# ------------------------------------------------------------
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print("✅ Local .env file loaded successfully.")
else:
    print("🌐 Running in hosted environment (Render or similar).")

# ------------------------------------------------------------
# 🔧 Load Configuration from Environment
# ------------------------------------------------------------
MODE = os.getenv("MODE", "paper").lower()
PAIR = os.getenv("PAIR", "BTC/USDT")
INTERVAL = int(os.getenv("INTERVAL", "60"))  # seconds between checks

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_SECRET = os.getenv("BYBIT_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ------------------------------------------------------------
# 💬 Telegram Messaging Utility
# ------------------------------------------------------------
def send_telegram_message(msg: str):
    """Send a Telegram message using bot token + chat ID."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials not found.")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("✅ Telegram message sent successfully.")
        else:
            print(f"⚠️ Telegram error: {res.text}")
    except Exception as e:
        print(f"⚠️ Telegram send error: {e}")

# ------------------------------------------------------------
# 🌐 Initialize Exchange (Bybit)
# ------------------------------------------------------------
def initialize_exchange():
    """Initialize connection to Bybit."""
    try:
        if not BYBIT_API_KEY or not BYBIT_SECRET:
            print("⚠️ No valid Bybit API credentials found.")
            return None

        exchange = ccxt.bybit({
            "apiKey": BYBIT_API_KEY,
            "secret": BYBIT_SECRET,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"}  # ensures spot trading
        })

        exchange.load_markets()
        print("✅ Bybit exchange initialized successfully.")
        return exchange
    except Exception as e:
        print(f"❌ Exchange initialization failed: {e}")
        send_telegram_message(f"❌ Exchange initialization failed: {e}")
        return None

# ------------------------------------------------------------
# 📈 Simulated Trade Logic (Paper Mode)
# ------------------------------------------------------------
def run_trading_loop(exchange):
    """Simulated simple strategy loop."""
    print(f"🤖 MIDAS Bot started in {MODE.upper()} mode — tracking {PAIR}")
    send_telegram_message(f"🤖 MIDAS Bot started in {MODE.upper()} mode — tracking {PAIR}")

    while True:
        try:
            ticker = exchange.fetch_ticker(PAIR)
            price = ticker["last"]
            print(f"💹 {PAIR} | Price: {price:.4f} | {datetime.now(timezone.utc)}")

            # Example: Simple threshold simulation
            if price > 200:
                send_telegram_message(f"🟢 {PAIR} price above threshold! ({price:.2f})")
            elif price < 100:
                send_telegram_message(f"🔴 {PAIR} price below threshold! ({price:.2f})")

        except Exception as e:
            print(f"⚠️ Error fetching market data: {e}")
            send_telegram_message(f"⚠️ Market data error: {e}")

        time.sleep(INTERVAL)

# ------------------------------------------------------------
# 🚀 Entry Point
# ------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting MIDAS Trading Bot...")
    exchange = initialize_exchange()

    if exchange:
        send_telegram_message("✅ MIDAS bot successfully launched and connected.")
        run_trading_loop(exchange)
    else:
        print("❌ Exchange not initialized. Aborting startup.")
        send_telegram_message("❌ Exchange not initialized. Aborting startup.")