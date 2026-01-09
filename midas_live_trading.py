import os
import ccxt
import time
import json
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone, timedelta

# ------------------------------------------------------
# 🌍 Load environment variables
# ------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PAIR = "SOL/USDT"
INTERVAL = 60  # seconds between checks
MODE = "PAPER"  # set to LIVE for live trading

# ------------------------------------------------------
# ⚙️ Telegram Alerts
# ------------------------------------------------------
def send_telegram_message(message: str):
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("⚠️ Telegram not configured. Skipping message.")
            return
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")


# ------------------------------------------------------
# 📊 Google Sheets Integration
# ------------------------------------------------------
def init_google_sheet():
    """Initialize connection to Google Sheets."""
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("google_key.json", scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open("MIDAS_Trade_Log").sheet1
        print("✅ Connected to Google Sheets successfully.")
        return sheet
    except Exception as e:
        print(f"⚠️ Google Sheets connection failed: {e}")
        return None


def log_to_google_sheets(sheet, pair, price, exchange, timestamp):
    """Log trade data to Google Sheets."""
    try:
        sheet.append_row([timestamp, pair, price, exchange])
        print(f"📊 Logged to Google Sheets: {pair} ${price:.2f} on {exchange}")
    except Exception as e:
        print(f"⚠️ Failed to log to Google Sheets: {e}")


def log_daily_summary(sheet):
    """Generate and log daily trading summary."""
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        summary = [
            "📅 Daily Summary",
            timestamp,
            "Data collection complete. Bot operational ✅"
        ]
        sheet.append_row(summary)
        send_telegram_message(f"📊 MIDAS Daily Summary logged at {timestamp}.")
        print(f"✅ Daily summary logged at {timestamp}.")
    except Exception as e:
        print(f"⚠️ Failed to log daily summary: {e}")


# ------------------------------------------------------
# 💱 Exchange Setup
# ------------------------------------------------------
exchanges = {
    "bybit": ccxt.bybit(),
    "mexc": ccxt.mexc(),
}

# ------------------------------------------------------
# 🔁 Monitoring Loop
# ------------------------------------------------------
def monitor_with_failover(pairs=[PAIR], interval=INTERVAL):
    """Continuously monitor prices and log data to Google Sheets and Telegram."""
    sheet = init_google_sheet()
    last_summary_day = datetime.now(timezone.utc).day

    while True:
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            for pair in pairs:
                for ex_name, ex in exchanges.items():
                    try:
                        ticker = ex.fetch_ticker(pair)
                        price = ticker["last"]
                        print(f"[{timestamp}] {pair} on {ex_name.upper()}: ${price:.2f}")
                        if sheet:
                            log_to_google_sheets(sheet, pair, price, ex_name.upper(), timestamp)
                    except Exception as sub_e:
                        print(f"[⚠️] Failed to fetch {pair} on {ex_name.upper()}: {sub_e}")
                        continue

            send_telegram_message(
                f"💗 MIDAS {MODE.upper()} Bot alive at {timestamp}. Still monitoring {PAIR} on BYBIT & MEXC."
            )

            # Log daily summary at midnight UTC
            current_day = datetime.now(timezone.utc).day
            if current_day != last_summary_day:
                log_daily_summary(sheet)
                last_summary_day = current_day

            time.sleep(interval)

        except Exception as e:
            print(f"[❌] Major error in monitor loop: {e}")
            send_telegram_message(f"[🔥] MIDAS Error: {e}")
            time.sleep(10)


# ------------------------------------------------------
# 🚀 Entry Point
# ------------------------------------------------------
if __name__ == "__main_git add midas_live_trading.py_":
    print(f"🚀 Starting MIDAS {MODE.upper()} Trading Bot (Paper Mode on Render)...")
    send_telegram_message("🤖 MIDAS Bot is now LIVE on Render.")
    monitor_with_failover()