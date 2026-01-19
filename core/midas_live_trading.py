import os
import time
import json
import ccxt
from datetime import datetime, timedelta, timezone

from core.midas_logger import log_trade
from core.midas_capital_tracker import update_capital, load_capital, reset_daily_capital
from core.midas_smart_order import execute_trade
from core.midas_telegram import send_telegram_message
from core.validate_data_files import validate_and_fix_json_files


# ============================================================
# 🧩 PRE-START VALIDATION
# ============================================================
validate_and_fix_json_files(silent=True)
print("✅ Data validation complete. Proceeding with trading engine startup.\n")


# ============================================================
# ⚙️ CONFIGURATION
# ============================================================
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "mexc")
PAIR_LIST = ["XRP/USDT", "BTC/USDT", "SOL/USDT"]
MODE = os.getenv("MODE", "PAPER").upper()
DAILY_MAX_LOSS = float(os.getenv("DAILY_MAX_LOSS", 0.015))  # 1.5% daily max loss
RISK_PER_TRADE = 0.015  # 1.5% of capital per trade
STOP_LOSS_PCT = 0.01  # 1% stop loss
TAKE_PROFIT_PCT = 0.02  # 2% take profit per trade
TRAILING_STOP_PCT = 0.02  # optional trailing stop
CAPITAL = 100.0
DAILY_RESET_HOUR = 0  # reset at 00:00 UTC+1
TIMEZONE_OFFSET = timedelta(hours=1)  # UTC+1 for Nigeria


# ============================================================
# 🌐 EXCHANGE INITIALIZATION
# ============================================================
def get_exchange(name="mexc"):
    """Initialize CCXT exchange with safe defaults."""
    name = name.lower()
    try:
        exchange_class = getattr(ccxt, name)
        exchange = exchange_class({
            "enableRateLimit": True,
            "options": {"defaultType": "spot"}
        })
        return exchange
    except AttributeError:
        raise ValueError(f"❌ Unsupported exchange: {name}")


exchange = get_exchange(EXCHANGE_NAME)
send_telegram_message(f"🚀 MIDAS Trading Bot started in {MODE} mode — Monitoring {', '.join(PAIR_LIST)}")


# ============================================================
# 📊 HELPER FUNCTIONS
# ============================================================
def fetch_price(pair):
    """Fetch latest ticker price."""
    try:
        ticker = exchange.fetch_ticker(pair)
        return ticker["last"]
    except Exception as e:
        print(f"⚠️ Failed to fetch price for {pair}: {e}")
        return None


def analyze_signal(price, last_price):
    """Placeholder signal logic — to be replaced with your real strategy."""
    if last_price is None:
        return None
    if price > last_price * 1.001:
        return {"side": "buy"}
    elif price < last_price * 0.999:
        return {"side": "sell"}
    return None


def within_trading_hours():
    """Always true for now — can add custom hours if needed."""
    return True


def is_reset_time():
    """Check if it's 00:00 UTC+1."""
    current_utc = datetime.utcnow()
    local_time = current_utc + TIMEZONE_OFFSET
    return local_time.hour == DAILY_RESET_HOUR and local_time.minute < 5


def send_daily_summary():
    """Summarize and report daily performance."""
    capital = load_capital()
    summary_msg = (
        f"📅 *Daily Summary ({datetime.utcnow().strftime('%Y-%m-%d')})*\n"
        f"💰 Balance: ${capital['current_balance']:.2f}\n"
        f"🏆 Total Trades: {capital['total_trades']}\n"
        f"✅ Wins: {capital['win_trades']} | ❌ Losses: {capital['loss_trades']}\n"
        f"📈 Profit: ${capital['total_profit']:.2f}\n"
        f"📉 Loss: ${capital['total_loss']:.2f}"
    )
    send_telegram_message(summary_msg)


# ============================================================
# 🔁 MAIN TRADING LOOP
# ============================================================
capital = load_capital()
print(f"💰 Starting capital: ${capital['current_balance']:.2f}")

last_prices = {pair: None for pair in PAIR_LIST}
daily_loss = 0.0

while True:
    try:
        if is_reset_time():
            reset_daily_capital()
            send_daily_summary()
            send_telegram_message("🔄 Daily reset complete. Starting new trading cycle.")
            daily_loss = 0.0
            time.sleep(300)
            continue

        if not within_trading_hours():
            time.sleep(60)
            continue

        for pair in PAIR_LIST:
            price = fetch_price(pair)
            if price is None:
                continue

            signal = analyze_signal(price, last_prices[pair])
            last_prices[pair] = price
            if not signal:
                print(f"⏸️ {pair}: No signal triggered.")
                continue

            side = signal["side"].upper()
            trade_size = capital["current_balance"] * RISK_PER_TRADE / price
            print(f"📊 {pair} price: {price}")
            print(f"💰 Trade size: {trade_size:.3f}")

            try:
                trade_result = execute_trade(
                    pair=pair,
                    side=side,
                    price=price,
                    size=trade_size,
                    mode=MODE,
                    take_profit_pct=TAKE_PROFIT_PCT,
                    stop_loss_pct=STOP_LOSS_PCT,
                    trailing_stop_pct=TRAILING_STOP_PCT
                )

                if trade_result["result"] == "win":
                    update_capital(trade_result["profit"], is_win=True)
                    send_telegram_message(f"🏆 {pair} WIN +{TAKE_PROFIT_PCT*100:.2f}% ✅")
                elif trade_result["result"] == "loss":
                    update_capital(trade_result["profit"], is_win=False)
                    daily_loss += abs(trade_result["profit"])
                    send_telegram_message(f"⚠️ {pair} LOSS -{STOP_LOSS_PCT*100:.2f}% ❌")
                else:
                    send_telegram_message(f"⚖️ {pair} Breakeven: {TAKE_PROFIT_PCT*100:.2f}%")

                print(f"✅ {pair}: Trade result — {trade_result['result'].upper()} ({trade_result['profit']:.2f}%)")

            except Exception as e:
                send_telegram_message(f"⚠️ Trade execution error: {e}")
                print(f"⚠️ Trade execution error: {e}")

            # 🚫 Stop trading if daily max loss reached
            if daily_loss / capital["current_balance"] >= DAILY_MAX_LOSS:
                send_telegram_message("🛑 Daily max loss reached. Trading halted until reset.")
                print("🛑 Daily max loss reached. Pausing trading.")
                time.sleep(3600)
                break

        print("✅ Cycle completed.\n")
        time.sleep(60)

    except Exception as e:
        print(f"⚠️ Loop error: {e}")
        send_telegram_message(f"⚠️ Loop error: {e}")
        time.sleep(60)
