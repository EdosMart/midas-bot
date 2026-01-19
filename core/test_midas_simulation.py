# ======================================================
# 🧪 MIDAS SYSTEM SIMULATION (PAPER MODE)
# Simulates multi-pair trading, position sizing,
# and trailing stop logic for system validation.
# ======================================================

import os
import time
import random
from datetime import datetime
from dotenv import load_dotenv

from core.midas_capital_tracker import load_capital, save_capital
from core.midas_logger import log_trade
from core.midas_telegram import send_telegram_message
from core.midas_smart_order import execute_trade, calculate_trade_levels, simulate_trailing_stop, evaluate_signal

# ======================================================
# ⚙️ ENVIRONMENT SETUP
# ======================================================

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)
print("✅ Local .env file loaded successfully.\n")

MODE = os.getenv("MODE", "PAPER").upper()
RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", 0.015))  # 1.5% of capital
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", 0.02))  # 2% TP
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", 0.01))  # 1% SL

PAIRS = ["XRP/USDT", "SOL/USDT", "BTC/USDT"]

# ======================================================
# 💰 CAPITAL SETUP
# ======================================================

capital_data = load_capital()

# Handle float or dict returns gracefully
if isinstance(capital_data, dict):
    current_balance = capital_data.get("current_balance", 100.0)
else:
    current_balance = float(capital_data)

print(f"🕛 Daily capital reset completed. Starting with: ${current_balance:.2f}")
send_telegram_message(f"🕛 Daily capital reset completed.\n💰 Starting Balance: ${current_balance:.2f}")

# ======================================================
# 🔁 TRADING CYCLE SIMULATION
# ======================================================

send_telegram_message("🧪 MIDAS Simulation Starting...")

for cycle in range(1, 4):  # Simulate 3 cycles
    print(f"\n🔁 Cycle {cycle} - {datetime.now().strftime('%H:%M:%S')}")

    for pair in PAIRS:
        price = round(random.uniform(0.9, 1.1), 4) if "XRP" in pair else \
                round(random.uniform(120, 140), 2) if "SOL" in pair else \
                round(random.uniform(90000, 95000), 2)
        print(f"📊 {pair} price: {price}")

        signal = evaluate_signal(price)

        if not signal:
            print(f"⏸️ {pair}: No signal triggered.")
            continue

        # ✅ Calculate trade position (1.5% risk)
        trade_value = current_balance * RISK_PER_TRADE
        size = round(trade_value / price, 3)
        side = signal

        print(f"💰 Trade size: {size}")
        log_trade(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), pair, side, price, size)
        send_telegram_message(f"🧾 Trade logged: {pair} {side.upper()} @ {price:.4f}")

        # 📈 Execute trade (paper mode)
        execute_trade(None, pair, side, price, size, mode=MODE)

        # 📊 Calculate levels
        take_profit, stop_loss = calculate_trade_levels(price, TAKE_PROFIT_PCT, STOP_LOSS_PCT)
        send_telegram_message(
            f"📊 Simulating {pair} {side.upper()}\n"
            f"Entry: {price:.4f}\n"
            f"TP: {take_profit:.4f}\n"
            f"SL: {stop_loss:.4f}"
        )

        # Simulate trailing stop
        simulate_trailing_stop(pair, side, price, trailing_stop_pct=STOP_LOSS_PCT)

        # 📈 Mock trade outcome
        trade_result = random.choice(["WIN", "LOSS", "BREAKEVEN"])
        if trade_result == "WIN":
            pnl = current_balance * TAKE_PROFIT_PCT
        elif trade_result == "LOSS":
            pnl = -current_balance * STOP_LOSS_PCT
        else:
            pnl = 0

        current_balance += pnl
        save_capital(current_balance)

        # 📣 Report result
        emoji = "🏆" if trade_result == "WIN" else "⚠️" if trade_result == "LOSS" else "⚖️"
        print(f"{emoji} {pair} Result: {trade_result} ({pnl:+.2f})")
        send_telegram_message(f"{emoji} {pair}: {trade_result} ({pnl:+.2f})")

    print("✅ Cycle completed.\n")
    time.sleep(3)

# ======================================================
# 🧾 DAILY SUMMARY
# ======================================================

summary = f"""
📅 Simulation Summary
---------------------
Final Balance: ${current_balance:.2f}
Total Pairs: {len(PAIRS)}
Mode: {MODE}
🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

print(summary)
send_telegram_message(summary)
print("✅ MIDAS Simulation Complete.")
