import os
import ccxt
import time
import json
import requests
import gspread
from datetime import datetime, timezone
from google.oauth2.service_account import Credentials

# ------------------------------------------------------
# ⚙️ ENVIRONMENT CONFIG
# ------------------------------------------------------

MODE = os.getenv("MODE", "Paper")
PAIR = os.getenv("PAIR", "SOL/USDT")
INTERVAL = int(os.getenv("INTERVAL", 60))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "MIDAS_Trade_Log")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# ------------------------------------------------------
# 💬 TELEGRAM UTILITY
# ------------------------------------------------------

def send_telegram_message(message: str):
    """Send messages to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials missing. Skipping message.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"⚠️ Telegram send error: {e}")

# ------------------------------------------------------
# 🔑 GOOGLE SHEETS CONNECTOR (auto-retry)
# ------------------------------------------------------

def connect_google_sheets(max_retries=3):
    """Retry Google Sheets connection before failing."""
    for attempt in range(1, max_retries + 1):
        try:
            if not GOOGLE_CREDS_JSON:
                raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON in environment.")

            creds_dict = json.loads(GOOGLE_CREDS_JSON)
            creds = Credentials.from_service_account_info(
                creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"]
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

# ------------------------------------------------------
# 🧾 SHEET LOGGER
# ------------------------------------------------------

def log_to_sheet(sheet, timestamp, pair, price, note):
    """Safely append data to Google Sheets."""
    try:
        sheet.append_row([timestamp, pair, price, note])
        print(f"✅ Logged to sheet: {timestamp}, {pair}, {price}, {note}")
    except Exception as e:
        print(f"⚠️ Google Sheets logging failed: {e}")

# ------------------------------------------------------
# 📊 DAILY SUMMARY
# ------------------------------------------------------

def send_daily_summary(sheet):
    """Summarize daily performance."""
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
# 🔁 FAIL-SAFE RECONNECT SYSTEM
# ------------------------------------------------------

def reconnect_exchange(exchange_name, max_retries=3):
    """Reconnect exchange with retries."""
    for attempt in range(1, max_retries + 1):
        try:
            ex = getattr(ccxt, exchange_name)()
            print(f"✅ Connected to {exchange_name.upper()}")
            return ex
        except Exception as e:
            print(f"⚠️ {exchange_name.upper()} reconnect failed (Attempt {attempt}/{max_retries}): {e}")
            time.sleep(3)
    raise RuntimeError(f"❌ Failed to reconnect {exchange_name.upper()} after {max_retries} attempts")

# ------------------------------------------------------
# 💹 MAIN MONITOR LOOP
# ------------------------------------------------------

def monitor_forever():
    """Main trading loop with full recovery."""
    sheet = None
    while sheet is None:
        try:
            sheet = connect_google_sheets()
        except Exception as e:
            print(f"⚠️ Sheets unavailable — retrying in 10s: {e}")
            time.sleep(10)

    bybit = reconnect_exchange("bybit")
    mexc = reconnect_exchange("mexc")

    send_telegram_message(f"🤖 MIDAS {MODE.upper()} Bot is now LIVE — monitoring {PAIR}")

    while True:
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            # Get prices from both exchanges
            bybit_price = bybit.fetch_ticker(PAIR)["last"]
            mexc_price = mexc.fetch_ticker(PAIR)["last"]
            diff = abs(bybit_price - mexc_price)

            print(f"[{timestamp}] BYBIT: {bybit_price} | MEXC: {mexc_price} | Δ {diff:.2f}")

            # Log trade
            log_to_sheet(sheet, timestamp, PAIR, bybit_price, f"Spread Δ {diff:.2f}")

            # Heartbeat every 60 minutes
            if datetime.now().minute % 60 == 0:
                send_telegram_message(f"💖 MIDAS Bot heartbeat — {PAIR} Δ {diff:.2f}")

            # Daily summary at 23:55 UTC
            now = datetime.now(timezone.utc)
            if now.hour == 23 and now.minute == 55:
                send_daily_summary(sheet)

            time.sleep(INTERVAL)

        except Exception as e:
            print(f"🔥 Fatal error in monitor loop: {e}")
            send_telegram_message(f"🔥 MIDAS error — restarting main loop: {e}")
            time.sleep(15)
            monitor_forever()  # self-healing restart

# ------------------------------------------------------
# 🚀 ENTRY POINT
# ------------------------------------------------------

if __name__ == "__main__":
    print("🚀 Starting MIDAS Bot — resilient mode enabled.")
    monitor_forever()