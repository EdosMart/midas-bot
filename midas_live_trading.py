# ===========================
# 🚀 MIDAS LIVE TRADING BOT
# Cloud-Optimized for Render
# ===========================
# Features:
# - Paper/Live mode switch via ENV
# - Telegram alerts + keep-alive
# - Proxy failover (Bybit & MEXC)
# - Auto daily log cleanup
# ===========================

import os
import time
import ccxt
import requests
import threading
import traceback
from datetime import datetime

# =======================================================
# 🔧 Load Environment Variables
# =======================================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MODE = os.getenv("MODE", "PAPER")  # PAPER or LIVE
PAIR = os.getenv("TRADING_PAIR", "SOL/USDT")
INTERVAL = int(os.getenv("INTERVAL", 60))


# =======================================================
# 🧹 Automatic Log Cleanup (runs every 24 hours)
# =======================================================
def clear_logs_periodically():
    while True:
        try:
            log_path = "/var/log/render/service.log"
            if os.path.exists(log_path):
                os.system(f"truncate -s 0 {log_path}")
                print("[🧹] Logs cleared successfully.")
            else:
                print("[ℹ️] Log path not found — skipping cleanup.")
        except Exception as e:
            print(f"[⚠️] Log cleanup failed: {e}")
        time.sleep(86400)


# =======================================================
# 💬 Telegram Messaging
# =======================================================
def telegram_message(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[⚠️] Telegram credentials missing — skipping alert.")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(url, data=payload)
    except Exception as e:
        print(f"[⚠️] Telegram Error: {e}")


# =======================================================
# 🌐 Exchange Connection with Proxy Failover
# =======================================================
proxies = [
    "https://51.158.154.173:3128",
    "https://64.225.8.82:9994",
    "https://198.199.86.11:3128",
    None
]


def connect_exchange(exchange_name):
    ExchangeClass = getattr(ccxt, exchange_name)
    for attempt, proxy in enumerate(proxies, 1):
        try:
            print(f"[🌐] Connecting to {exchange_name.upper()} (Attempt {attempt})...")
            exchange = ExchangeClass({
                "enableRateLimit": True,
                "proxies": {"https": proxy} if proxy else None,
            })
            markets = exchange.load_markets()
            print(f"[✅] Connected to {exchange_name.upper()} ({len(markets)} markets)")
            return exchange
        except Exception as e:
            print(f"[⚠️] {exchange_name.upper()} connection failed (proxy={proxy}): {e}")
            time.sleep(3)
    print(f"[❌] All connection attempts failed for {exchange_name.upper()}")
    telegram_message(f"❌ {exchange_name.upper()} failed to connect after retries.")
    return None


# =======================================================
# 💹 Load Exchanges
# =======================================================
bybit = connect_exchange("bybit")
mexc = connect_exchange("mexc")

# =======================================================
# 💰 Mock Trading Variables (Paper Mode)
# =======================================================
balance = 10000
position = None
entry_price = 0


# =======================================================
# ⏱️ Main Trading Logic
# =======================================================
def trade_loop():
    global balance, position, entry_price


while True:
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # 🧠 Fetch ticker data
        ticker = exchange.fetch_ticker(PAIR)
        if not ticker:
            print(f"[⚠️] Failed to fetch price data for {PAIR}")
            time.sleep(INTERVAL)
            continue

        price = ticker["last"]
        print(f"[{timestamp}] {PAIR} price: {price}")

        # 🧠 Perform trading logic here
        print(f"[{timestamp}] Checking market data...")

        # Wait for next cycle
        time.sleep(INTERVAL)

    except Exception as e:
        print(f"[⚠️] Error in loop: {e}")
        time.sleep(10)

        if not ticker:
            print(f"[⚠️] Failed to fetch price data for {PAIR}")
            time.sleep(INTERVAL)
            continue

        price = ticker["last"]
        print(f"[{timestamp}] {PAIR} price: {price}")

        # --- Simple mock trading logic ---
        if position is None and price % 2 < 1:
            position = "SELL"
            entry_price = price
            telegram_message(f"🔴 SELL Signal at {price}\nTime: {timestamp}")

        elif position == "SELL" and price > entry_price * 1.002:
            pnl = entry_price - price
            balance += pnl
            telegram_message(f"💰 Closing SELL\nExit: {price}\nPnL: {pnl:.2f}\nBalance: {balance:.2f}")
            position = None

        # --- Keep-alive ping every few loops ---
        if int(time.time()) % (3600 * 3) < INTERVAL:
            telegram_message(f"⏰ Keep-alive: Bot running ({MODE})\nPair: {PAIR}\nBalance: {balance:.2f}")

    except Exception as e:
        error_msg = f"[⚠️] Error in loop: {e}\n{traceback.format_exc()}"
        print(error_msg)
        telegram_message(error_msg)

    time.sleep(INTERVAL)

# =======================================================
# 🚀 Start the Bot
# =======================================================
telegram_message(f"🚀 Midas Live Bot Started\nMode: {MODE}\nMonitoring: {PAIR} every {INTERVAL}s")
trade_loop()
