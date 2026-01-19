import json
import os
from datetime import datetime
from core.midas_telegram import send_telegram_message

# File to store daily summaries
SUMMARY_FILE = os.path.join(os.path.dirname(__file__), "daily_summary.json")


def log_daily_summary(trades_today, profit_loss, capital, win_rate, date=None):
    """
    Logs a compact daily summary for reporting.
    Appends to the JSON file safely.
    """
    date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_entry = {
        "date": date,
        "trades_today": int(trades_today),
        "profit_loss_pct": round(profit_loss, 3),
        "capital": round(float(capital), 2),
        "win_rate_pct": round(win_rate, 2)
    }

    # ✅ Load existing data safely
    data = []
    if os.path.exists(SUMMARY_FILE):
        try:
            with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
                if isinstance(existing, list):
                    data = existing
                else:
                    data = [existing]
        except json.JSONDecodeError:
            print("⚠️ Warning: summary file corrupted. Rebuilding...")
            data = []

    # ✅ Append and save back
    data.append(new_entry)

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"📅 Daily summary logged: {new_entry}")

    # ✅ Optional Telegram summary push
    message = (
        f"📊 *Daily Summary ({date})*\n"
        f"• Trades: {trades_today}\n"
        f"• P/L: {profit_loss:.2f}%\n"
        f"• Capital: ${capital:.2f}\n"
        f"• Win Rate: {win_rate:.1f}%"
    )
    send_telegram_message(message)

    return new_entry


if __name__ == "__main__":
    print("🔧 Testing daily summary logger...")

    log_daily_summary(
        trades_today=12,
        profit_loss=3.45,
        capital=113.20,
        win_rate=66.7
    )