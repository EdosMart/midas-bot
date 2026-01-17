# ============================================================
# 📊 MIDAS PERFORMANCE DASHBOARD
# ============================================================
# Description:
# Reads daily_summary.json + capital_tracker.json
# Generates an equity curve + performance stats
# Sends chart + report to Telegram
# ============================================================

import os
import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv

# ============================================================
# 🌍 LOAD ENVIRONMENT
# ============================================================
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print("✅ Local .env file loaded successfully.")
else:
    print("🌐 Running in hosted environment (Render or similar).")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ============================================================
# 📂 FILES
# ============================================================
CAPITAL_FILE = "capital_tracker.json"
SUMMARY_FILE = "daily_summary.json"

# ============================================================
# 📤 TELEGRAM SEND FUNCTIONS
# ============================================================
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def send_telegram_image(image_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as img:
        files = {"photo": img}
        data = {"chat_id": CHAT_ID, "caption": caption}
        requests.post(url, files=files, data=data)

# ============================================================
# 📊 LOAD AND PROCESS DATA
# ============================================================
if not os.path.exists(SUMMARY_FILE):
    print("❌ No trade summary data found.")
    send_telegram_message("❌ No trade summary data found for MIDAS Dashboard.")
    exit()

with open(SUMMARY_FILE, "r") as f:
    summary = json.load(f)

# Create DataFrame
data = []
for date, stats in summary.items():
    data.append({
        "date": date,
        "wins": stats.get("wins", 0),
        "losses": stats.get("losses", 0),
        "profit": stats.get("profit", 0.0),
    })

df = pd.DataFrame(data)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

# Compute cumulative equity
initial_balance = 100
df["equity"] = initial_balance + df["profit"].cumsum()

# ============================================================
# 📈 CALCULATE METRICS
# ============================================================
total_profit = df["profit"].sum()
win_rate = (df["wins"].sum() / (df["wins"].sum() + df["losses"].sum())) * 100 if (df["wins"].sum() + df["losses"].sum()) > 0 else 0
last_equity = df["equity"].iloc[-1]

report_text = (
    f"📊 *MIDAS Performance Dashboard*\n"
    f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
    f"💰 Current Equity: ${last_equity:.2f}\n"
    f"📈 Total Profit: ${total_profit:.2f}\n"
    f"🏆 Win Rate: {win_rate:.1f}%\n"
    f"📆 Trading Days: {len(df)}\n"
)

# ============================================================
# 📉 GENERATE PLOT
# ============================================================
plt.figure(figsize=(8, 5))
plt.plot(df["date"], df["equity"], marker="o", label="Equity Curve")
plt.bar(df["date"], df["profit"], alpha=0.4, label="Daily Profit ($)")
plt.title("MIDAS Daily Equity & Profit Overview")
plt.xlabel("Date")
plt.ylabel("Value ($)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save image
chart_path = "midas_performance_chart.png"
plt.savefig(chart_path)
plt.close()

# ============================================================
# 📬 SEND REPORT TO TELEGRAM
# ============================================================
send_telegram_message(report_text)
send_telegram_image(chart_path, caption="📊 MIDAS Equity & Profit Overview")

print("✅ Performance dashboard report sent successfully.")