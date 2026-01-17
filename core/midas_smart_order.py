# ============================================================
# 🧠 MIDAS SMART ORDER MODULE
# Handles order execution, stop loss, and take profit logic
# ============================================================

import os
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import ccxt
from midas_logger import log_trade


# ============================================================
# ⚙️ LOAD ENVIRONMENT VARIABLES
# ============================================================
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

MODE = os.getenv("MODE", "paper").lower()
EXCHANGE_NAME = os.getenv("EXCHANGE", "bybit").lower()
PAIR = os.getenv("PAIR", "XRP/USDT")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

STOP_LOSS_PCT = 0.02
TAKE_PROFIT_PCT = 0.036
TRAILING_STOP_PCT = 0.015


# ============================================================
# 🔗 INITIALIZE EXCHANGE
# ============================================================
def get_exchange():
    """Initialize CCXT exchange connection."""
    exchange_class = getattr(ccxt, EXCHANGE_NAME)
    exchange = exchange_class({
        "apiKey": os.getenv("API_KEY"),
        "secret": os.getenv("API_SECRET"),
        "enableRateLimit": True,
    })
    return exchange


exchange = get_exchange()


# ============================================================
# 💬 TELEGRAM UPDATES
# ============================================================
def send_telegram_message(msg):
    """Send message to Telegram bot."""
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[⚠️] Telegram send error: {e}")


# ============================================================
# 🚀 EXECUTE TRADE
# ============================================================
def execute_trade(direction, pair, size, price):
    """Execute a trade order — live or paper."""
    try:
        if MODE == "paper":
            print(f"[📘 PAPER TRADE] {direction.upper()} {size:.3f} {pair} @ {price:.4f}")
            send_telegram_message(f"[📘 PAPER TRADE] {direction.upper()} {size:.3f} {pair} @ {price:.4f}")
            return {"status": "simulated", "price": price, "size": size}

        # LIVE trade
        order_type = "market"
        side = "buy" if direction == "buy" else "sell"
        order = exchange.create_order(pair, order_type, side, size)
        print(f"✅ LIVE ORDER placed: {order}")
        send_telegram_message(f"✅ LIVE ORDER placed: {direction.upper()} {pair} {size}")
        return order

    except Exception as e:
        print(f"[❌] Trade execution failed: {e}")
        send_telegram_message(f"[❌] Trade execution failed: {e}")
        return None


# ============================================================
# 🧩 EVALUATE TRADE EXIT CONDITIONS
# ============================================================
def evaluate_trade_exit(direction, entry_price, current_price):
    """Check stop loss, take profit, or trailing conditions."""
    try:
        if direction == "buy":
            stop_loss = entry_price * (1 - STOP_LOSS_PCT)
            take_profit = entry_price * (1 + TAKE_PROFIT_PCT)

            if current_price <= stop_loss:
                return "stopped"
            elif current_price >= take_profit:
                return "take_profit"

        elif direction == "sell":
            stop_loss = entry_price * (1 + STOP_LOSS_PCT)
            take_profit = entry_price * (1 - TAKE_PROFIT_PCT)

            if cu…