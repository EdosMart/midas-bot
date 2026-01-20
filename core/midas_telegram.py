import os
import time
import requests
from dotenv import load_dotenv

# ======================================================
# 🌍 LOAD ENVIRONMENT VARIABLES
# ======================================================
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ENABLE_UPDATES = os.getenv("ENABLE_TELEGRAM_UPDATES", "False").lower() == "true"

# ======================================================
# 🧩 BUILD TELEGRAM API ENDPOINT
# ======================================================
if BOT_TOKEN:
    TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
else:
    TELEGRAM_API_URL = None


# ======================================================
# 📨 SEND TELEGRAM MESSAGE (With Auto-Retry)
# ======================================================
def send_telegram_message(message: str, retry_attempts: int = 3, timeout: int = 10):
    """Sends a Telegram message with retries and error handling."""
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram credentials missing or not loaded from environment.")
        return False

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    for attempt in range(retry_attempts):
        try:
            response = requests.post(TELEGRAM_API_URL, data=payload, timeout=timeout)
            if response.status_code == 200:
                print("✅ Telegram message sent successfully.")
                return True
            else:
                print(f"⚠️ Telegram send failed: {response.text}")
        except requests.RequestException as e:
            print(f"⚠️ Network error on attempt {attempt + 1}: {e}")
        time.sleep(2)

    print("❌ Telegram communication test failed after multiple attempts.")
    return False


# ======================================================
# 🧪 TEST CONNECTION (Manual Run)
# ======================================================
if __name__ == "__main__":
    print("🔧 Testing Telegram connection...")
    if send_telegram_message("✅ MIDAS Telegram connection test successful!"):
        print("✅ Test completed successfully.")
    else:
        print("❌ Telegram communication test failed.")