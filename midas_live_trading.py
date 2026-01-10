import os
import ccxt
import time
import json
import requests
import gspread
from datetime import datetime, timezone, timedelta
from google.oauth2.service_account import Credentials

# ------------------------------------------------------
# ⚙️ Load Configuration
# ------------------------------------------------------

MODE = os.getenv("MODE", "Paper")
PAIR = os.getenv("PAIR", "SOL/USDT")
INTERVAL = int(os.getenv("INTERVAL", 60))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "MIDAS_Trade_Log")

# ------------------------------------------------------
# 🔑 Google Sheets Credentials (from Render)
# ------------------------------------------------------

creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not creds_json:
    raise ValueError("❌ Missing GOOGLE_APPLICATION_CREDENTIALS_JSON in environment")

creds_dict = json.loads(creds_json)
creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)
sheet = gc.open(GOOGLE_SHEET_NAME).sheet1

# ------------------------------------------------------
# 📤 Telegram Notifier
# ------------------------------------------------------

def send_telegram_message(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials not found, skipping message.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")

# ------------------------------------------------------
# 🧾 Google Sheets Logger
# ------------------------------------------------------

def log_to_sheet(timestamp, pair, price, note):
    try:
        sheet.append_row([timestamp, pair, price, note])
        print(f"✅ Logged to sheet: {timestamp}, {pair}, {price}, {note}")
    except Exception as e:
        print(f"⚠️ Google Sheets logging failed: {e}")

# ------------------------------------------------------
# 📊 Daily Summary
# ------------------------------------------------------

def send_daily_summary():
    try:
        data = sheet.get_all_records()
        if not data:
            send_telegram_message("📊 No trades logged yet.")
            return

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_trades = [row for row in data if today in str(row.get("Timestamp", ""))]

        if not today_trades:
            send_telegram_message("📊 No trades logged today.")
            return

        summary = f"📈 MIDAS Daily Summary ({today})\n"
        summary += f"Total Logs: {len(today_trades)}\n"

        prices = [float(row["Price"]) for row in today_trades if row.get("Price")]
        if prices:
            summary += f"Min: {min(prices)} | Max: {max(prices)}\n"

        notes = set(row.get("Note", "") for row in today_trades if row.get("Note"))
        if notes:
            summary += f"Notes: {', '.join(notes)}"

        send_telegram_message(summary)

    except Exception as e:
        print(f"⚠️ Daily summary error: {e}")

# ------------------------------------------------------
# 💹 Live Trading Monitor (Bybit & MEXC)
# ------------------------------------------------------

def monitor_prices():
    print(f"🚀 Starting MIDAS {MODE.upper()} Bot — monitoring {PAIR}...\n")
    send_telegram_message(f"🤖 MIDAS {MODE.upper()} Bot is now LIVE — tracking {PAIR}")

    bybit = ccxt.bybit()
    mexc = ccxt.mexc()

    while True:
        try:
            bybit_price = bybit.fetch_ticker(PAIR)["last"]
            mexc_price = mexc.fetch_ticker(PAIR)["last"]
            diff = abs(bybit_price - mexc_price)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] BYBIT: {bybit_price} | MEXC: {mexc_price} | Δ {diff:.2f}")

            # Log to Google Sheets
            log_to_sheet(timestamp, PAIR, bybit_price, f"Spread Δ {diff:.2f}")

            # Heartbeat to Telegram (every 60 minutes)
            if datetime.now().minute % 60 == 0:
                send_telegram_message(f"💖 MIDAS Bot alive. {PAIR} Δ {diff:.2f}")

            # Send daily summary at 23:55 UTC
            now = datetime.now(timezone.utc)
            if now.hour == 23 and now.minute == 55:
                send_daily_summary()

            time.sleep(INTERVAL)

        except Exception as e:
            print(f"⚠️ Monitor loop error: {e}")
            time.sleep(30)

# ------------------------------------------------------
# 🚀 Entry Point
# ------------------------------------------------------

if __name__ == "__main__":
    monitor_prices()