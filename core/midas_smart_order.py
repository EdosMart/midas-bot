import time
from datetime import datetime
from core.midas_logger import log_trade
from core.midas_capital_tracker import update_capital

# ============================================================
# ⚙️ SMART ORDER MODULE – MEXC PAPER TRADING ENGINE
# ============================================================

def execute_trade(exchange, pair, signal, balance, risk_per_trade=0.02,
                  take_profit_pct=0.02, stop_loss_pct=0.01, trailing_stop_pct=0.02,
                  paper_mode=True):
    """
    Executes a simulated or live trade based on signal.
    Returns a trade summary dictionary.
    """

    try:
        # --- Define direction ---
        side = signal.get("trend", "neutral")
        price = signal.get("price", 0)

        if side not in ["bullish", "bearish"]:
            print("⚠️ No clear signal, skipping trade.")
            return None

        # --- Calculate position size ---
        position_size = balance * risk_per_trade / stop_loss_pct
        trade_value = balance * risk_per_trade
        print(f"📊 Position size: ${trade_value:.2f} ({risk_per_trade*100:.1f}% risk)")

        # --- Simulated price movement ---
        if paper_mode:
            entry_price = price or exchange.fetch_ticker(pair)["last"]
            take_profit = entry_price * (1 + take_profit_pct if side == "bullish" else 1 - take_profit_pct)
            stop_loss = entry_price * (1 - stop_loss_pct if side == "bullish" else 1 + stop_loss_pct)

            print(f"🎯 Entry: {entry_price:.4f} | TP: {take_profit:.4f} | SL: {stop_loss:.4f}")

            # --- Simulate outcome ---
            outcome = "win" if signal.get("rsi", 50) > 45 else "loss"
            profit_pct = take_profit_pct if outcome == "win" else -stop_loss_pct
            profit = balance * profit_pct

            # --- Log the trade ---
            trade_data = {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "pair": pair,
                "side": side,
                "entry": entry_price,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "outcome": outcome,
                "profit": profit,
                "balance_before": balance,
                "balance_after": balance + profit
            }

            log_trade(trade_data)
            update_capital(profit, is_win=(outcome == "win"))
            print(f"✅ {outcome.upper()} | New balance: ${balance + profit:.2f}")

            return trade_data

        # --- Live trading (if paper_mode=False) ---
        else:
            entry_price = exchange.fetch_ticker(pair)["last"]
            order_side = "buy" if side == "bullish" else "sell"
            order = exchange.create_market_order(pair, order_side, position_size)

            log_trade({
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "pair": pair,
                "side": order_side,
                "price": entry_price,
                "size": position_size,
                "result": "executed"
            })
            print(f"✅ Live order executed: {order_side} {pair} @ {entry_price}")

            return order

    except Exception as e:
        print(f"⚠️ Trade execution error: {e}")
        return None


# ============================================================
# 🧮 HELPER FUNCTION – TRAILING STOP SIMULATION
# ============================================================

def simulate_trailing_stop(entry_price, side, trailing_stop_pct=0.02, steps=10):
    """
    Simulates a trailing stop for demonstration or backtesting.
    """
    direction = 1 if side == "bullish" else -1
    highest_price = entry_price
    trailing_stop = entry_price * (1 - trailing_stop_pct * direction)

    for i in range(steps):
        current_price = entry_price * (1 + direction * 0.005 * i)
        if direction == 1 and current_price > highest_price:
            highest_price = current_price
            trailing_stop = highest_price * (1 - trailing_stop_pct)
        elif direction == -1 and current_price < highest_price:
            highest_price = current_price
            trailing_stop = highest_price * (1 + trailing_stop_pct)

        print(f"Step {i+1}: Price={current_price:.4f}, TrailingStop={trailing_stop:.4f}")
        time.sleep(0.1)

    print("🔚 Trailing stop simulation complete.")