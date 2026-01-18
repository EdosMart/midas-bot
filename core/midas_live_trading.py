# ============================================================
# MIDAS LIVE TRADING ENGINE 🦾
# Supports: MEXC, BYBIT, OKX (active: MEXC)
# Mode: Paper or Live (controlled via MODE)
# ============================================================

import os
import time
import ccxt
from datetime import datetime, timezone
from dotenv import load_dotenv

# Internal imports
from core.midas_logger import log_trade
from core.midas_capital_tracker import update_capital, load_capital
from core.midas_telegram import send_telegram_message
from core.midas_smart_order import execute_trade

# ============================================================
# 🌍 ENVIRONMENT SETUP
# ============================================================
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print("✅ Local .env file loaded successfully.")
else:
    print("🌐 Running in hosted environment (Render or similar).")

# ============================================================
# ⚙️ CONFIGURATION
# ============================================================
EXCHANGE_NAME = os.getenv("EXCHANGE", "mexc").lower()
PAIR = os.getenv("PAIR", "XRP/USDT")
MODE = os.getenv("MODE", "paper").lower()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SMART_COMPOUND = os.getenv("SMART_COMPOUND", "true").lower() == "true"

RISK_PER_TRADE = 0.02         # 2% risk per trade
STOP_LOSS_PERCENT = 0.01      # 1% stop loss
TAKE_PROFIT_PERCENT = 0.02    # 2% take profit
TRAILING_STOP_PERCENT = 0.02  # Optional trailing stop
INTERVAL_SECONDS = 60         # 1 minute loop
MAX_DAILY_LOSS = 0.015        # 1.5% daily cap

starting_balance = 100.0  # Default paper balance

# ============================================================
# 🔗 EXCHANGE CONNECTION
# ============================================================
def get_exchange(name):
    """Initialize exchange dynamically."""
    try:
        exchange_class = getattr(ccxt, name)
        exchange = exchange_class({
            "apiKey": os.getenv(f"{name.upper()}_API_KEY"),
            "secret": os.getenv(f"{name.upper()}_SECRET"),
            "enableRateLimit": True
        })
        print(f"✅ Connected to {name.upper()} exchange successfully.")
        return exchange
    except AttributeError:
        raise ValueError(f"❌ Unsupported exchange: {name}")

exchange = get_exchange(EXCHANGE_NAME)

# ============================================================
# 💰 SMART COMPOUNDING TOGGLE
# ============================================================
if SMART_COMPOUND:
    current_capital_data = load_capital()
    current_balance = current_capital_data.get("current_balance", starting_balance)
    trade_size = current_balance * RISK_PER_TRADE
    print(f"🧮 Smart compounding active: using ${trade_size:.2f} per trade (based on current balance ${current_balance:.2f})")
else:
    trade_size = starting_balance * RISK_PER_TRADE
    print(f"📊 Fixed trade size mode: using ${trade_size:.2f} per trade")

# ============================================================
# 📊 TELEGRAM STARTUP MESSAGE
# ============================================================
send_telegram_message(
    f"🚀 MIDAS Trading Bot started successfully on {EXCHANGE_NAME.upper()} ({MODE.upper()} MODE) — monitoring {PAIR}"
)

# ============================================================
# 🧠 TRADE SIGNAL ANALYSIS (SIMPLE LOGIC)
# ============================================================
def analyze_signal():
    """Placeholder signal generator (replace with AI/indicator logic)."""
    import random
    return random.choice(["buy", "sell", None])

# ============================================================
# 🔁 MAIN TRADING LOOP
# ============================================================
daily_loss = 0.0
trades_today = 0
daily_start_date = datetime.now().strftime("%Y-%m-%d")

while True:
    try:
        # Reset daily counters at midnight
        if datetime.now().strftime("%Y-%m-%d") != daily_start_date:
            daily_start_date = datetime.now().strftime("%Y-%m-%d")
            daily_loss = 0.0
            trades_today = 0
            print("🔄 New trading day detected. Counters reset.")

        signal = analyze_signal()

        if not signal:
            print("🤖 No valid trade signal. Waiting...")
            time.sleep(INTERVAL_SECONDS)
            continue

        ticker = exchange.fetch_ticker(PAIR)
        price = ticker["last"]

        # Daily loss protection
        if daily_loss <= -MAX_DAILY_LOSS * starting_balance:
            send_telegram_message("🛑 Daily loss limit reached. Halting trades for today.")
            print("🛑 Daily loss cap triggered. Trading paused until next day.")
            time.sleep(600)
            continue

        # Trade direction setup
        if signal == "buy":
            side = "buy"
            take_profit = price * (1 + TAKE_PROFIT_PERCENT)
            stop_loss = price * (1 - STOP_LOSS_PERCENT)
        else:
            side = "sell"
            take_profit = price * (1 - TAKE_PROFIT_PERCENT)
            stop_loss = price * (1 + STOP_LOSS_PERCENT)

        # Execute trade
        execute_trade({
            "pair": PAIR,
            "side": side,
            "price": price,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "size": trade_size,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        })

        # Update capital tracker (simulated)
        profit = trade_size * TAKE_PROFIT_PERCENT if signal == "buy" else -trade_size * STOP_LOSS_PERCENT
        update_capital(profit, is_win=profit > 0)
        daily_loss += profit
        trades_today += 1

        log_trade({
            "pair": PAIR,
            "side": side,
            "price": price,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "profit": profit,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result": "win" if profit > 0 else "loss"
        })

        send_telegram_message(
            f"📈 Trade executed: {side.upper()} {PAIR}\n💰 Profit: ${profit:.2f}\n📊 Daily P/L: ${daily_loss:.2f}"
        )

        time.sleep(INTERVAL_SECONDS)

    except Exception as e:
        print(f"⚠️ Error in trading loop: {e}")
        time.sleep(30)
