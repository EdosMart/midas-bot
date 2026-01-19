import os
import requests
import time
from dotenv import load_dotenv

# ======================================================
# 🧩 LOAD ENVIRONMENT VARIABLES
# ======================================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    print("✅ Environment loaded successfully.")
else:
    print("⚠️ No .env file found in project root.")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ENABLE_TELEGRAM_UPDATES = os.getenv("ENABLE_TELEGRAM_UPDATES", "True").lower() == "true"

# ======================================================
# 🌐 BUILD TELEGRAM API ENDPOINT
# ======================================================
if TELEGRAM_BOT_TOKEN:
    TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
else:
    TELEGRAM_API_URL = None
    print("❌ TELEGRAM_BOT_TOKEN not set in .env")

# ======================================================
# ✉️ SEND TELEGRAM MESSAGE (With Retry Logic)
# ======================================================
def send_telegram_message(message: str, retry_attempts: int = 3, timeout: int = 10):
    """
    Sends a message to the configured Telegram chat.
    Retries on network failure up to retry_attempts times.
    """
    if not TELEGRAM_API_URL or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials missing or not loaded from environment.")
        return False

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    for attempt in range(1, retry_attempts + 1):
        try:
            response = requests.post(TELEGRAM_API_URL, data=payload, timeout=timeout)
            if response.status_code == 200:
                print(f"📨 Telegram alert sent: {message[:50]}{'...' if len(message) > 50 else ''}")
                return True
            else:
                print(f"⚠️ Telegram API error ({response.status_code}): {response.text}")
        except requests.exceptions.Timeout:
            print(f"⚠️ Telegram timeout (attempt {attempt}/{retry_attempts}) — retrying...")
        except Exception as e:
            print(f"❌ Telegram send failed (attempt {attempt}/{retry_attempts}): {e}")

        time.sleep(2)  # short pause before retry

    print("❌ Telegram communication failed after all retries.")
    return False

# ======================================================
# 🧪 TEST TELEGRAM CONNECTION (Optional Manual Run)
# ======================================================
if __name__ == "__main__":
    print("🔧 Testing Telegram connection...")

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        success = send_telegram_message("✅ MIDAS Telegram connection test successful!")
        if success:
            print("🎉 Telegram test message sent successfully.")
        else:
            print("⚠️ Telegram message failed. Please check your chat ID or bot token.")
    else:
        print("⚠️ Telegram credentials missing or invalid in .env.")