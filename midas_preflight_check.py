import os
import requests
import json

# ------------------------------------------------------
# MIDAS Preflight Check (Telegram Connection Only)
# ------------------------------------------------------

print("🚀 MIDAS Preflight Check Starting...")

# Check for required environment variables
required_env_vars = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "PAIR",
    "MODE",
]

missing_vars = [v for v in required_env_vars if not os.getenv(v)]
if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
else:
    print("✅ All required environment variables found.")

# Telegram check
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(msg: str):
    """Send test message to Telegram."""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": msg}
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("✅ Telegram message sent successfully.")
        else:
            print(f"⚠️ Telegram error: {res.text}")
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

# Send preflight confirmation
send_telegram_message("✅ MIDAS Preflight Check: Telegram connection OK.")

print("🎯 MIDAS Preflight Check Complete.")