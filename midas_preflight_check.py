import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

# ------------------------------------------------------
# 🧩 MIDAS Preflight Check — Environment, Telegram & Sheets
# ------------------------------------------------------

print("🚀 MIDAS Preflight Check Starting...\n")

# 1️⃣ Required Environment Variables
required_vars = [
    "MODE",
    "PAIR",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "GOOGLE_APPLICATION_CREDENTIALS_JSON",
    "GOOGLE_SHEET_NAME"
]

missing = [v for v in required_vars if not os.getenv(v)]
if missing:
    print(f"❌ Missing environment variables: {', '.join(missing)}")
else:
    print("✅ All required environment variables found.")

# 2️⃣ Telegram Test
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

if token and chat_id:
    try:
        msg = "✅ MIDAS Preflight Check: Telegram connection OK."
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        res = requests.post(url, json={"chat_id": chat_id, "text": msg}, timeout=10)
        if res.status_code == 200:
            print("✅ Telegram message sent successfully.")
        else:
            print(f"⚠️ Telegram response not OK: {res.status_code}")
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
else:
    print("⚠️ Telegram environment missing, skipping Telegram test.")

# 3️⃣ Google Sheets Test
google_creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
sheet_name = os.getenv("GOOGLE_SHEET_NAME", "MIDAS_Trade_Log")

if google_creds_json:
    try:
        creds_dict = json.loads(google_creds_json)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(creds)
        sheet = gc.open(sheet_name).sheet1
        print(f"✅ Connected to Google Sheet: {sheet_name}")
        print("✅ Google Sheets access verified.")

        # Optional: test write (uncomment to test)
        # sheet.append_row(["✅", "MIDAS Preflight", "Success"])

    except Exception as e:
        print(f"❌ Google Sheets test failed: {e}")
else:
    print("⚠️ Missing GOOGLE_APPLICATION_CREDENTIALS_JSON, skipping Sheets test.")

print("\n🎯 MIDAS Preflight Check Complete.\n")