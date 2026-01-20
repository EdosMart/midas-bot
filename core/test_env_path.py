import os
from dotenv import load_dotenv

# Force .env load from parent directory
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
print(f"🔍 Checking for .env at: {env_path}")

if os.path.exists(env_path):
    print("✅ .env file FOUND!")
else:
    print("❌ .env file NOT found!")

# Load .env
load_dotenv(env_path)

# Print environment variables to confirm they loaded
print("\n🧾 Loaded Variables:")
print("TELEGRAM_BOT_TOKEN:", os.getenv("TELEGRAM_BOT_TOKEN"))
print("TELEGRAM_CHAT_ID:", os.getenv("TELEGRAM_CHAT_ID"))
print("ENABLE_TELEGRAM_UPDATES:", os.getenv("ENABLE_TELEGRAM_UPDATES"))
