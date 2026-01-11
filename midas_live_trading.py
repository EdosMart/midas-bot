# ================================================================
# MIDAS LIVE TRADING BOT – CLEAN VERSION (Bybit + Telegram)
# ================================================================

import os
import ccxt
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# ================================================================
# 🌍 Load Environment Variables (works locally + Render)
# ================================================================
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print("✅ Local .env file loaded successfully.")
else:
    print("🌐 Running in hosted environment (Render or similar).")

# ================================================================
# ⚙️ Configuration
# ================================================================
MODE = os.getenv("MODE", "paper").lower()
PAIR = os.getenv("PAIR", "SOL/USDT")
INTERVAL = int(os.getenv("INTERVAL", "60"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_SECRET = os.getenv("BYBIT_SECRET")

# ================================================================
# 💬 Telegram Helper
# ================================================================
def send_telegram_message(message: str):
    """Send message to Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials missing. Cannot send message.")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Telegram message sent successfully.")
        else:
            print(f"⚠️ Telegram send failed: {response.text}")
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

# ================================================================
# 🧩 Initialize Exchange
# ================================================================
def init_exchange():
    """Initialize Bybit connection."""
    if not BYBIT_API_KEY or not BYBIT_SECRET:
        print("⚠️ No valid Bybit API credentials found.")
        return None
    try:
        exchange = ccxt.bybit({
            "apiKey": BYBIT_API_KEY,
            "secret": BYBIT_SECRET,
            "enableRateLimit": True,
        })
        print("✅ Bybit exchange initialized successfully.")
        return exchange
    except Exception as e:
        print(f"❌ Failed to initialize Bybit: {e}")
        return None

# ================================================================
# 📈 Main Monitor Loop
# ================================================================
def monitor_market(exchange):
    """Continuously fetch and log the latest price."""
    while True:
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            ticker = exchange.fetch_ticker(PAIR)
            price = ticker.get("last")
            print(f"[{timestamp}] {PAIR} on BYBIT: ${price:.2f}")
            time.sleep(INTERVAL)
        except Exception as e:
            print(f"[⚠️] Error fetching ticker: {e}")
            time.sleep(10)

# ================================================================
# 🚀 Entry Point
# ================================================================
if __name__ == "__main__":
    print("🚀 Starting MIDAS Trading Bot...")

    # Diagnostic check
    print("🔍 Checking environment variables...")
    critical_vars = {
        "MODE": MODE,
        "PAIR": PAIR,
        "TELEGRAM_BOT_TOKEN": "✅" if TELEGRAM_TOKEN else "❌",
        "TELEGRAM_CHAT_ID": "✅" if TELEGRAM_CHAT_ID else "❌",
        "BYBIT_API_KEY": "✅" if BYBIT_API_KEY else "❌",
        "BYBIT_SECRET": "✅" if BYBIT_SECRET else "❌",
    }
    for key, val in critical_vars.items():
        print(f"   {key}: {val}")

    exchange = init_exchange()

    if not exchange:
        print("❌ Exchange not initialized. Aborting startup.")
        send_telegram_message("❌ MIDAS startup failed: Bybit not initialized.")
    else:
        send_telegram_message(f"🤖 MIDAS {MODE.upper()} bot is live, monitoring {PAIR} every {INTERVAL}s.")
        monitor_market(exchange)