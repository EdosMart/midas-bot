import json
import os
from datetime import datetime
from core.midas_capital_tracker import load_capital
import requests

def send_telegram_message(msg):
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": msg})

def generate_daily_summary():
    capital = load_capital()
    summary = (
        f"📊 *Daily Trading Summary — {datetime.utcnow().strftime('%Y-%m-%d')}*\n"
        f"💰 Current Balance: ${capital['current_balance']:.2f}\n"
        f"📈 Total Profit: ${capital['total_profit']:.2f}\n"
        f"📉 Total Loss: ${capital['total_loss']:.2f}\n"
        f"🧾 Total Trades: {capital['total_trades']}\n"
        f"✅ Wins: {capital['win_trades']} | ❌ Losses: {capital['loss_trades']}\n"
    )
    send_telegram_message(summary)
    print(summary)

if __name__ == "__main__":
    generate_daily_summary()