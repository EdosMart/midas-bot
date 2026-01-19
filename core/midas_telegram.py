# ======================================================
# 📬 MIDAS Telegram Messaging Module
# Provides robust message delivery with retries and
# connection handling to avoid dropped alerts.
# ======================================================

import os
import time
import requests

# ======================================================
# 🔧 CONFIGURATION
# ======================================================

TELEGRAM_BOT_TOKEN = os.getenv("8152460819:AAF_se8ZXk6w2cjwleTrUVPoX3FaCCSesXI")
TELEGRAM_CHAT_ID = os.getenv("970989479")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# ======================================================
# ✉️ SEND TELEGRAM MESSAGE (With Auto-Retry)
# ======================================================

def send_telegram_message(message: str, retry_attempts: int = 3, timeout: int = 20):
    """
    Sends a Telegram message with retry logic and timeout handling.
    Safe to call from anywhere in the MIDAS engine.
    """

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials missing or not loaded from environment.")
        return False

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"  # allow emojis & simple formatting
    }

    for attempt in range(1, retry_attempts + 1):
        try:
            response = requests.post(BASE_URL, data=data, timeout=timeout)

            # ✅ Success
            if response.status_code == 200:
                print(f"📨 Telegram alert sent (Attempt {attempt}/{retry_attempts}): {message[:70]}")
                return True

            # ⚠️ Rate-limited or API error
            elif response.status_code == 429:
                retry_after = response.json().get("parameters", {}).get("retry_after", 5)
                print(f"⚠️ Rate limited by Telegram. Retrying in {retry_after}s...")
                time.sleep(retry_after)

            else:
                print(f"⚠️ Telegram API error ({response.status_code}): {response.text}")

        except requests.exceptions.Timeout:
            print(f"⏳ Telegram send timeout (attempt {attempt}/{retry_attempts}) — retrying...")
            time.sleep(3)

        except requests.exceptions.RequestException as e:
            print(f"❌ Telegram send failed (attempt {attempt}/{retry_attempts}): {e}")
            time.sleep(3)

    print("🚫 All Telegram send attempts failed after retries.")
    return False


# ======================================================
# 🧪 TEST FUNCTION (Run manually)
# ======================================================

if __name__ == "__main__":
    print("🔧 Testing Telegram connection...")
    success = send_telegram_message("✅ MIDAS Telegram connection test successful!")
    if success:
        print("✅ Telegram communication verified.")
    else:
        print("❌ Telegram communication test failed.")