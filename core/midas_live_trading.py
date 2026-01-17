# ============================================================
# ⚡ MIDAS LIVE TRADING BOT (v6.0 — Auto-Compounding + Daily Summary)
# ============================================================

import os
import time
import json
import ccxt
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Internal modules
from midas_logger import log_trade
from midas_telegram import send_telegram_message

# ============================================================
# 🌍 LOAD ENVIRONMENT VARIABLES
# ============================================================
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print("✅ Local .env file loaded successfully.")
else:
    print("🌐 Running in hosted environment (Render or similar).")

EXCHANGE_NAME = os.getenv("EXCHANGE", "bybit")
PAIRS = os.getenv("PAIRS", "XRP/USDT,SOL/USDT,ETH/USDT,BTC/USDT").split(",")
MODE = os.getenv("MODE", "paper").lower()
BASE_CAPITAL = float(os.getenv("CAPITAL", 100))
RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", 0.02))
TIMEFRAME = os.getenv("TIMEFRAME", "15m")
DAILY_REPORT_HOUR = int(os.getenv("REPORT_HOUR", 21))  # Default: 21:00 (9 PM)

CAPITAL_FILE = "capital_tracker.json"
SUMMARY_FILE = "daily_summary.json"

# Indicator constants
RSI_PERIOD = 14
EMA_FAST = 9
EMA_SLOW = 21
VOL_WINDOW = 20

# ============================================================
# 💾 CAPITAL + SUMMARY MANAGEMENT
# ============================================================
def load_capital():
    if os.path.exists(CAPITAL_FILE):
        with open(CAPITAL_FILE, "r") as f:
            data = json.load(f)
            return data.get("capital", BASE_CAPITAL)
    return BASE_CAPITAL

def save_capital(new_balance):
    with open(CAPITAL_FILE, "w") as f:
        json.dump({"capital": new_balance}, f, indent=4)

def update_capital(current_capital, result, profit_factor=0.02):
    if result == "win":
        new_capital = current_capital * (1 + profit_factor)
    elif result == "loss":
        new_capital = current_capital * (1 - RISK_PER_TRADE)
    else:
        new_capital = current_capital
    save_capital(round(new_capital, 2))
    return round(new_capital, 2)

def record_trade_summary(result, profit_amount):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    summary = {}

    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "r") as f:
            summary = json.load(f)

    if today not in summary:
        summary[today] = {"wins": 0, "losses": 0, "profit": 0.0}

    if result == "win":
        summary[today]["wins"] += 1
        summary[today]["profit"] += profit_amount
    elif result == "loss":
        summary[today]["losses"] += 1
        summary[today]["profit"] -= profit_amount

    with open(SUMMARY_FILE, "w") as f:
        json.dump(summary, f, indent=4)

def generate_daily_report():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not os.path.exists(SUMMARY_FILE):
        return None

    with open(SUMMARY_FILE, "r") as f:
        summary = json.load(f)

    data = summary.get(today)
    if not data:
        return None

    report = (
        f"📅 MIDAS Daily Summary ({today})\n"
        f"✅ Wins: {data['wins']}\n"
        f"❌ Losses: {data['losses']}\n"
        f"💰 Net Profit: ${data['profit']:.2f}\n"
        f"📊 Current Balance: ${load_capital():.2f}"
    )
    return report

# ============================================================
# 🔌 EXCHANGE CONNECTION
# ============================================================
def get_exchange(name):
    try:
        exchange_class = getattr(ccxt, name)
        return exchange_class({"enableRateLimit": True})
    except AttributeError:
        raise ValueError(f"❌ Unsupported exchange: {name}")

exchange = get_exchange(EXCHANGE_NAME)
print(f"✅ Connected to {EXCHANGE_NAME.upper()} — {MODE.upper()} mode")

# ============================================================
# 📈 INDICATOR FUNCTIONS
# ============================================================
def fetch_ohlcv(symbol, timeframe="15m", limit=100):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        return df
    except Exception as e:
        print(f"⚠️ Failed to fetch data for {symbol}: {e}")
        return None

def calculate_indicators(df):
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(RSI_PERIOD).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(RSI_PERIOD).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))
    df["ema_fast"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["vol_ma"] = df["volume"].rolling(VOL_WINDOW).mean()
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    if (
        latest["ema_fast"] > latest["ema_slow"]
        and prev["rsi"] < 50
        and latest["rsi"] > 50
        and latest["volume"] > latest["vol_ma"] * 1.2
    ):
        return {"trend": "bullish", "price": latest["close"]}

    elif (
        latest["ema_fast"] < latest["ema_slow"]
        and prev["rsi"] > 50
        and latest["rsi"] < 50
        and latest["volume"] > latest["vol_ma"] * 1.2
    ):
        return {"trend": "bearish", "price": latest["close"]}

    return None

# ============================================================
# 🚀 STARTUP MESSAGE
# ============================================================
send_telegram_message(f"🚀 MIDAS v6.0 started | {EXCHANGE_NAME.upper()} | Mode: {MODE.upper()}\nPairs: {', '.join(PAIRS)}")

# ============================================================
# 🔁 MAIN LOOP WITH DAILY REPORTS
# ============================================================
last_report_day = None

while True:
    try:
        current_capital = load_capital()

        for pair in PAIRS:
            df = fetch_ohlcv(pair, timeframe=TIMEFRAME, limit=100)
            if df is None:
                continue

            df = calculate_indicators(df)
            signal = generate_signal(df)
            if not signal:
                continue

            entry_price = signal["price"]
            trend = signal["trend"].upper()
            position_open = True
            result = None
            profit_amount = 0

            # Risk parameters
            if trend == "BULLISH":
                take_profit = entry_price * 1.02
                stop_loss = entry_price * 0.98
            else:
                take_profit = entry_price * 0.98
                stop_loss = entry_price * 1.02

            send_telegram_message(f"📊 New {trend} setup on {pair}\nEntry: {entry_price:.4f}\nTP: {take_profit:.4f}\nSL: {stop_loss:.4f}")
            log_trade(pair, trend, entry_price, "Trade opened")

            while position_open:
                ticker = exchange.fetch_ticker(pair)
                current_price = ticker["last"]

                if (trend == "BULLISH" and current_price >= take_profit) or (trend == "BEARISH" and current_price <= take_profit):
                    result = "win"
                    profit_amount = current_capital * RISK_PER_TRADE
                    send_telegram_message(f"🏆 TP HIT | {pair} | ${current_price:.4f}")
                    position_open = False

                elif (trend == "BULLISH" and current_price <= stop_loss) or (trend == "BEARISH" and current_price >= stop_loss):
                    result = "loss"
                    profit_amount = current_capital * RISK_PER_TRADE
                    send_telegram_message(f"❌ STOP LOSS | {pair} | ${current_price:.4f}")
                    position_open = False

                time.sleep(15)

            if result:
                new_balance = update_capital(current_capital, result)
                record_trade_summary(result, profit_amount)
                send_telegram_message(f"💹 {result.upper()} | New Balance: ${new_balance:.2f}")

        # === Daily Summary Reporting ===
        current_time = datetime.now(timezone.utc)
        if current_time.hour == DAILY_REPORT_HOUR and current_time.strftime("%Y-%m-%d") != last_report_day:
            report = generate_daily_report()
            if report:
                send_telegram_message(report)
                last_report_day = current_time.strftime("%Y-%m-%d")

        time.sleep(60)

    except Exception as e:
        print(f"⚠️ Error: {e}")
        send_telegram_message(f"⚠️ MIDAS ERROR: {e}")
        time.sleep(60)