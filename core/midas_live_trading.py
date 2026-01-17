import os
import ccxt
import time
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from core.midas_capital_tracker import update_capital, load_capital, reset_daily_capital, log_sync_event

# --------------------------------------------------
# 🧩 Load Environment Variables
# --------------------------------------------------
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MODE = os.getenv("MODE", "paper").lower()
PAIR = os.getenv("PAIR", "XRP/USDT")

MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_SECRET = os.getenv("MEXC_SECRET")

# --------------------------------------------------
# 📢 Telegram Messaging
# --------------------------------------------------
def send_telegram_message(msg):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
        except Exception as e:
            print(f"⚠️ Telegram send error: {e}")

# --------------------------------------------------
# ⚙️ MEXC Exchange Setup
# --------------------------------------------------
def get_exchange(name):
    """Initializes exchange safely — converts name to lowercase for ccxt."""
    try:
        name = name.lower()  # ✅ ensure lowercase
        exchange_class = getattr(ccxt, name)
        return exchange_class({
            "apiKey": os.getenv(f"{name.upper()}_API_KEY"),
            "secret": os.getenv(f"{name.upper()}_SECRET"),
            "enableRateLimit": True
        })
    except AttributeError:
        raise ValueError(f"❌ Unsupported exchange: {name} (must match ccxt lowercase name)")


# --------------------------------------------------
# 📊 Balance Sync (Live Mode)
# --------------------------------------------------
def sync_balance(exchange):
    if MODE != "live":
        return
    try:
        balance_info = exchange.fetch_balance()
        mexc_balance = balance_info["total"].get("USDT", 0)
        capital = load_capital()
        local_balance = capital["current_balance"]
        diff = abs(mexc_balance - local_balance) / local_balance * 100

        if diff > 1:
            capital["current_balance"] = mexc_balance
            update_capital(0, is_win=True)
            log_sync_event("MEXC", "synced")
            send_telegram_message("🔄 Balance synced successfully with MEXC.")
    except Exception as e:
        print(f"⚠️ Balance sync failed: {e}")

# --------------------------------------------------
# 📈 Trade Signal Simulation
# --------------------------------------------------
def simulate_signal():
    """Mock signal generator for testing."""
    import random
    direction = random.choice(["buy", "sell", None])
    return direction

# --------------------------------------------------
# 🔁 Main Loop
# --------------------------------------------------
print(f"🚀 MIDAS Trading Bot started in {MODE.upper()} mode — Monitoring {PAIR}")
exchange = init_exchange()
capital = load_capital()
send_telegram_message(f"🤖 MIDAS Bot active — {MODE.upper()} mode running.")

daily_loss_limit = 0.015 * capital["starting_balance"]

while True:
    try:
        if datetime.utcnow().hour == 0:
            reset_daily_capital()

        signal = simulate_signal()
        if not signal:
            time.sleep(60)
            continue

        balance = capital["current_balance"]
        risk_per_trade = balance * 0.02
        stop_loss = balance * 0.01
        potential_loss = -stop_loss
        potential_profit = risk_per_trade * 2

        if signal == "buy":
            update_capital(potential_profit, is_win=True)
            send_telegram_message("🟢 Simulated BUY — +2% profit target hit.")
        elif signal == "sell":
            update_capital(potential_loss, is_win=False)
            send_telegram_message("🔴 Simulated SELL — -1% stop-loss triggered.")

        capital = load_capital()
        if capital["total_loss"] >= daily_loss_limit:
            send_telegram_message("⛔ Daily loss cap reached (1.5%). Trading paused until next reset.")
            break

        time.sleep(120)

    except Exception as e:
        print(f"⚠️ Trading loop error: {e}")
        time.sleep(60)
