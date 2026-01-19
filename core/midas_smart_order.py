# ======================================================
# 💹 MIDAS SMART ORDER ENGINE
# Handles order simulation, trailing stop logic,
# and paper/live trade execution routing.
# ======================================================

import time
from datetime import datetime
from core.midas_logger import log_trade
from core.midas_telegram import send_telegram_message

# ======================================================
# ⚙️ ORDER EXECUTION (SIMULATED / LIVE)
# ======================================================

def execute_trade(exchange, pair, side, price, size, mode="PAPER"):
    """
    Executes a simulated or live trade.
    - exchange: ccxt exchange object (only required for live mode)
    - pair: trading pair (e.g., BTC/USDT)
    - side: 'buy' or 'sell'
    - price: entry price
    - size: trade size
    - mode: 'PAPER' or 'LIVE'
    """
    print(f"📈 Executing trade — {pair} {side.upper()} @ {price:.4f} (size: {size})")

    # Send Telegram notification
    send_telegram_message(f"🚀 Executing {side.upper()} {pair} @ {price:.4f} ({size})")

    if mode.upper() == "LIVE":
        try:
            # Live order (for future activation)
            order = exchange.create_order(pair, "market", side, size)
            print(f"✅ LIVE trade executed: {order}")
            send_telegram_message(f"✅ LIVE trade executed successfully: {pair}")
            return order
        except Exception as e:
            print(f"❌ Live trade failed: {e}")
            send_telegram_message(f"⚠️ Live trade failed for {pair}: {e}")
            return None
    else:
        # PAPER MODE: Simulated trade
        log_trade(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), pair, side, price, size)
        send_telegram_message(f"📊 Simulating {pair} {side.upper()}\nEntry: {price:.4f}")
        return {"status": "simulated", "pair": pair, "side": side, "price": price, "size": size}


# ======================================================
# 📉 STOP LOSS / TAKE PROFIT CALCULATOR
# ======================================================

def calculate_trade_levels(entry_price, take_profit_pct=0.02, stop_loss_pct=0.01):
    """
    Calculate take profit and stop loss levels for given entry.
    Returns: (take_profit, stop_loss)
    """
    take_profit = entry_price * (1 + take_profit_pct)
    stop_loss = entry_price * (1 - stop_loss_pct)
    return round(take_profit, 6), round(stop_loss, 6)


# ======================================================
# 📊 TRAILING STOP SIMULATION (FOR PAPER TESTING)
# ======================================================

def simulate_trailing_stop(pair, side, entry_price, trailing_stop_pct=0.02):
    """
    Simulates trailing stop behavior for paper trading.
    Adjusts stop level dynamically as price rises.
    """
    print("🔧 Running trailing stop test simulation...\n")

    # Initialize prices
    highest_price = entry_price
    trailing_stop = entry_price * (1 - trailing_stop_pct)

    send_telegram_message(f"🔄 Trailing stop initialized at {trailing_stop:.4f}")

    # Simulate 10 progressive steps in price
    for step in range(1, 11):
        # Increase price slightly to simulate bullish movement
        price = highest_price * (1 + 0.005 * step)

        if price > highest_price:
            highest_price = price
            trailing_stop = highest_price * (1 - trailing_stop_pct)

        # Log trade update event
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_trade(timestamp, pair, side, float(price), size=1.0)

        print(f"Step {step}: Price={price:.4f}, TrailingStop={trailing_stop:.4f}")

        send_telegram_message(
            f"📈 Trailing Stop Update — {pair}\n"
            f"Price: {price:.4f}\nStop: {trailing_stop:.4f}"
        )

        time.sleep(1)

    print("\n✅ Trailing stop simulation complete.")
    send_telegram_message("✅ Trailing stop simulation complete.")


# ======================================================
# 🧠 STRATEGIC SIGNAL HANDLER (BASIC LOGIC)
# ======================================================

def evaluate_signal(price_data):
    """
    Placeholder for your future strategy logic.
    Example: Decide whether to buy, sell, or hold.
    Returns: 'buy', 'sell', or None
    """
    # Simple random trigger for simulation
    import random
    if random.random() > 0.7:
        return "buy"
    elif random.random() < 0.3:
        return "sell"
    else:
        return None


# ======================================================
# 🧪 SELF-TEST MODE
# ======================================================

if __name__ == "__main__":
    print("🧪 Running standalone test for simulate_trailing_stop...\n")
    simulate_trailing_stop("XRP/USDT", "buy", 1.00, trailing_stop_pct=0.02)