import os
import sys
import requests
from dotenv import load_dotenv

# === Ensure Python finds the project root ===
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# === Load .env file (both locally and on Render) ===
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print("✅ Local .env file loaded successfully.")
else:
    print("🌐 Running in hosted environment (Render or similar).")

# === Verify environment variables ===
REQUIRED_VARS = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "PAIR",
    "MODE",
]

missing = [v for v in REQUIRED_VARS if not os.getenv(v)]

if missing:
    print(f"❌ Missing environment variables: {', '.join(missing)}")
else:
    print("✅ All required environment variables found.")

# ------------------------------------------------------------
# 💬 Test Telegram Bot
# ------------------------------------------------------------
try:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID.")

    message = "✅ MIDAS Preflight Check: Telegram connection OK."
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    res = requests.post(url, data={"chat_id": chat_id, "text": message})

    if res.status_code == 200:
        print("✅ Telegram message sent successfully.")
    else:
        print(f"⚠️ Telegram error: {res.text}")

except Exception as e:
    print(f"⚠️ Telegram error: {e}")

# ------------------------------------------------------------
# 🎯 Final Status
# ------------------------------------------------------------
print("\n🎯 MIDAS Preflight Check Complete.\n")
