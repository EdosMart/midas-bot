# ============================================================
# 📬 MIDAS Telegram Messaging Utility
# ============================================================
import os
import requests
from dotenv import load_dotenv

# Load environment variables (works locally and on Render)
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    """
    Sends a text message to the configured Telegram chat.
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram not configured properly.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}

    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print(f"📨 Telegram alert sent: {message}")
        else:
            print(f"⚠️ Telegram error: {res.text}")
    except Exception as e:
        print(f"❌ Telegram connection failed: {e}")