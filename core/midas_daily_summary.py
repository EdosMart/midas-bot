# ============================================================
# 📅 MIDAS DAILY SUMMARY MODULE
# Automatically sends a daily trade report to Telegram
# ============================================================

import os
import json
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(msg):
    """Send message to Telegram bot."""
    try:
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except Exception as e:
        print(f"[⚠️] Telegram send error: {e}")


def generate_summary():
    """Reads trade_log.json and calculates key metrics."""
    log_path = os.path.join(os.path.dirname(__file__), "trade_log.json")
    if not os.path.exists(log_path):
        send_telegram_message("📭 No trades have been logged yet.")
        return

    try:
        with open(log_path, "r") as file:
            trades = json.load(file)

        total = len(trades)
        wins = sum(1 for t in trades if t.get("result") == "take_profit")
        losses = sum(1 for t in trades if t.get("result") == "stopped")
        win_rate = (wins / total * 100) if total > 0 else 0

        summary = (
            f"📅 Daily MIDAS Summary — {datetime.now().strftime('%Y-%m-%d')}\n"
            f"📊 Total Trades: {total}\n"
            f"✅ Wins: {wins}\n"
            f"❌ Losses: {losses}\n"
            f"🏆 Win Rate: {win_rate:.2f}%\n"
        )

        send_telegram_message(summary)
        print("✅ Daily summary sent successfully.")
    except Exception as e:
        print(f"[⚠️] Failed to generate summary: {e}")


def run_daily_summary():
    """Runs once every 24 hours at a specific hour."""
    target_hour = 7  # 7 AM local time
    while True:
        now = datetime.now(timezone.utc)
        if now.hour == target_hour and now.minute == 0:
            generate_summary()
            time.sleep(60)  # Avoid multiple sends in the same minute
        time.sleep(30)


if __name__ == "_main_":
    run_daily_summary()