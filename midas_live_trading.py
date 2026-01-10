import os
import ccxt
import time
import json
import requests
import gspread
from datetime import datetime, timezone, timedelta
from google.oauth2.service_account import Credentials

# ------------------------------------------------------
# ⚙️ Configuration
# ------------------------------------------------------

MODE = os.getenv("MODE", "Paper")
PAIR = os.getenv("PAIR", "SOL/USDT")
INTERVAL = int(os.getenv("INTERVAL", 60))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "MIDAS_Trade_Log")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# ------------------------------------------------------
# 🧠 Utility Functions
# ------------------------------------------------------

def send_telegram_message(message: str):
    """Send messages to Telegram bot"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials missing. Skipping message.")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"⚠️ Telegram send error: {e}")

# ------------------------------------------------------
# 🔑 Google Sheets Setup (with auto-retry)
# ------------------------------------------------------

def connect_google_sheets(max_retries=3):
    """Try to connect to Google Sheets up to 3 times before failing."""
    for attempt in range(1, max_retries + 1):
        try:
            if not GOOGLE_CREDS_JSON:
                raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON in environment.")

            creds_dict = json.loads(GOOGLE_CREDS_JSON)
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            gc = gspread.authorize(creds)
            sheet = gc.open(GOOGLE_SHEET_NAME).sheet1

            print(f"✅ Connected to Google Sheet: {GOOGLE_SHEET_NAME}")
            return sheet

        except Exception as e:
            print(f"⚠️ Google Sheets connection failed (Attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(5)
            else:
                raise RuntimeError(f"❌ Could not connect to Google Sheets after {max_retries} tries.")

sheet = connect_google_sheets()

# ------------------------------------------------------
# 🧾 Google Sheets Logger
# ------------------------------------------------------

def log_to_sheet(timestamp, pair, price, note):
    try:
        sheet.append_row([timestamp, pair, price, note])
        print(f"✅ Logged to sheet: {timestamp}, {pair}, {price}, {note}")
    except Exception as e:
        print(f"⚠️ Logging to Google Sheets failed: {e}")

# ------------------------------------------------------
# 📊 Daily Summary
# ------------------------------------------------------

def send_daily_summary():
    try:
        data = sheet.get_all_records()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_trades = [row for row in data if today in str(row.get("Timestamp", ""))]

        if not today_trades:
            send_telegram_message("📊 No trades logged today.")
            return

        prices = [float(row["Price"]) for row in today_trades if row.get("Price")]
        min_p, max_p = min(prices), max(prices)

        summary = (
            f"📈 MIDAS Daily Summary ({today})\n"
            f"Logs: {len(today_trades)} | Min: {min_p} | Max: {max_p}\n"
        )

        send_telegram_message(summary)

    except Exception as e:
        print(f"⚠️ Daily summary error: {e}")

# ------------------------------------------------------
# 💹 Live Monitoring (Bybit + MEXC)
# ------------------------------------------------------

def monitor_prices():
    print(f"🚀 Starting MIDAS {MODE.upper()} Bot — monitoring {PAIR}...\n")
    send_telegram_message(f"🤖 MIDAS {MODE.upper()} Bot is now LIVE — tracking {PAIR}")

    bybit = ccxt.bybit()
    mexc = ccxt.mexc