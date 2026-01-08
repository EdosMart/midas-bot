# ======================================================
# 🚀 MIDAS LIVE TRADING BOT (Render Version)
# Author: EdosMart & ChatGPT (GPT-5)
# Mode: Paper / Live via ENV
# ======================================================

import os
import ccxt
import time
import json
import gspread
import requests
from datetime import datetime, timedelta, timezone
from oauth2client.service_account import ServiceAccountCredentials

# ======================================================
# ⚙️ CONFIGURATION
# ======================================================

PAIR = "SOL/USDT"
INTERVAL = 60  # seconds
START_BALANCE = 1000.0
SHEET_NAME = "MIDAS_Trade_Log"

# Load environment variables
MODE = os.getenv("MODE", "paper").lower()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")
MEXC_API_KEY = os.getenv("MEXC_API_KEY", "")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET", "")

# ======================================================
# 🔗 INITIALIZE EXCHANGES
# ======================================================
exchanges = {
    "bybit": ccxt.bybit({"enableRateLimit": True, "apiKey": BYBIT_API_KEY, "secret": BYBIT_API_SECRET}),
    "mexc": ccxt.mexc({"enableRateLimit": True, "apiKey": MEXC_API_KEY, "secret": MEXC_API_SECRET})
}

# ======================================================
# 🧠 STRATEGY PARAMETERS (from best config)
# ======================================================
with open("midas_best_config.json", "r") as f:
    CONFIG = json.load(f)

RSI_BULLISH = CONFIG.get("rsi_bullish", 52)
RSI_BEARISH = CONFIG.get("rsi_bearish", 46)
ADX_MIN = CONFIG.get("adx_min", 14)
EMA_FAST = CONFIG.get("ema_fast", 8)
EMA_SLOW = CONFIG.get("ema_slow", 30)
TAKE_PROFIT = CONFIG.get("take_profit", 1.8)
STOP_MULT = CONFIG.get("stop_mult", 1.1)

# ======================================================
# 💬 TELEGRAM ALERT
# ======================================================
def send_telegram_message(text):
    try:
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
            requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"[⚠️] Telegram error: {e}")

# ======================================================
# 📈 GOOGLE SHEETS LOGGING
# ======================================================
def init_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("midasbot_service.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        print(f"[⚠️] Google Sheets init failed: {e}")
        return None

def log_to_sheets(sheet, data):
    try:
        if sheet:
            sheet.append_row(data)
    except Exception as e:
        print(f"[⚠️] Google Sheets log failed: {e}")

# ======================================================
# 💾 LOCAL CSV LOGGING
# ======================================================
def log_to_csv(data):
    try:
        with open("trade_log.csv", "a") as f:
            f.write(",".join(map(str, data)) + "\n")
    except Exception as e:
        print(f"[⚠️] CSV log failed: {e}")

# ======================================================
# ⚖️ TRADE SIMULATION STATE (PAPER)
# ======================================================
balance = START_BALANCE
position = None
entry_price = 0.0
last_summary = datetime.now(timezone.utc)

# ======================================================
# 🔁 MONITORING + STRATEGY LOOP
# ======================================================
def monitor_with_failover():
    global balance, position, entry_price, last_summary
    sheet = init_google_sheets()

    while True:
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            for ex_name, ex in exchanges.items():
                try:
                    ticker = ex.fetch_ticker(PAIR)
                    price = ticker["last"]
                    print(f"[{timestamp}] {PAIR} @ ${price:.2f} on {ex_name.upper()}")

                    # Simulated strategy (paper mode)
                    if MODE == "paper":
                        if not position and price < entry_price * 0.98:
                            position = "BUY"
                            entry_price = price
                            send_telegram_message(f"🟢 BUY @ ${price:.2f} on {ex_name.upper()}")
                            log_to_sheets(sheet, [timestamp, PAIR, "BUY", price, balance])
                            log_to_csv([timestamp, PAIR, "BUY", price, balance])

                        elif position == "BUY" and price > entry_price * (1 + TAKE_PROFIT / 100):
                            profit = (price - entry_price)
                            balance += profit
                            position = None
                            send_telegram_message(f"🔴 SELL @ ${price:.2f} (Profit: ${profit:.2f}) on {ex_name.upper()}")
                            log_to_sheets(sheet, [timestamp, PAIR, "SELL", price, balance])
                            log_to_csv([timestamp, PAIR, "SELL", price, balance])

                    # Daily summary
                    now = datetime.now(timezone.utc)
                    if now - last_summary >= timedelta(hours=24):
                        summary = f"📊 DAILY SUMMARY\nMode: {MODE.upper()}\nBalance: ${balance:.2f}\nTime: {timestamp}"
                        send_telegram_message(summary)
                        last_summary = now

                except Exception as sub_e:
                    print(f"[⚠️] Failed on {ex_name}: {sub_e}")
                    continue

            time.sleep(INTERVAL)

        except Exception as e:
            print(f"[❌] Loop Error: {e}")
            send_telegram_message(f"[🔥] MIDAS Error: {e}")
            time.sleep(10)

# ======================================================
# 🚀 ENTRY POINT
# ======================================================
if __name__ == "__main__":
    print(f"🚀 Starting MIDAS {MODE.upper()} Trading Bot on Render...")
    send_telegram_message(f"🤖 MIDAS {MODE.upper()} Bot is now LIVE on Render.")
    monitor_with_failover()