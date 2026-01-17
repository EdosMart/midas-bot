# ============================================================
# 🚀 MIDAS PREFLIGHT CHECK
# Telegram Connection + Environment Verification
# ============================================================

import os
import requests
from dotenv import load_dotenv

# ------------------------------------------------------------
# 🌍 Load Environment Variables (works for local + Render)
# ------------------------------------------------------------
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print("✅ Local .env file loaded successfully.")
else:
    print("🌐 Running in hosted environment (Render or similar).")
print("🔍 TELEGRAM_BOT_TOKEN =", os.getenv("TELEGRAM_BOT_TOKEN"))
print("🔍 TELEGRAM_CHAT_ID =", os.getenv("TELEGRAM_CHAT_ID"))
# ------------------------------------------------------------
# 🧩 Start Health Check
# ------------------------------------------------------------
print("\n🚀 MIDAS Preflight Check Starting...\n")

# Required environment variables
required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "PAIR", "MODE"]
missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    print(f"❌ Missing environment variables: {', '.join(missing)}")
else:
    print("✅ All required environment variables found.\n")

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
