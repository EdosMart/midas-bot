# ============================================================
# 📘 MIDAS TRADE LOGGER MODULE
# Logs trades into a local JSON file for performance tracking
# ============================================================

import json
import os
from datetime import datetime


# ============================================================
# 🧩 TRADE LOGGING FUNCTION
# ============================================================
def log_trade(pair, side, price, size, result="open"):
    """
    Logs trade details to 'trade_log.json'.
    Automatically creates the file if it doesn't exist.
    """
    try:
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "pair": pair,
            "side": side,
            "price": round(price, 6),
            "size": round(size, 6),
            "result": result
        }

        # Determine log file path
        log_path = os.path.join(os.path.dirname(__file__), "trade_log.json")

        # Load previous logs if available
        if os.path.exists(log_path):
            with open(log_path, "r") as file:
                try:
                    trades = json.load(file)
                    if not isinstance(trades, list):
                        trades = []
                except json.JSONDecodeError:
                    trades = []
        else:
            trades = []

        # Append new trade
        trades.append(log_entry)

        # Save back to file
        with open(log_path, "w") as file:
            json.dump(trades, file, indent=4)

        print(f"📝 Trade logged: {log_entry}")
        return True

    except Exception as e:
        print(f"[⚠️] Failed to log trade: {e}")
        return False


# ============================================================
# 🧮 SIMPLE TRADE STATS
# ============================================================
def get_trade_summary():
    """
    Reads 'trade_log.json' and returns a summary of results.
    """
    log_path = os.path.join(os.path.dirname(__file__), "trade_log.json")

    if not os.path.exists(log_path):
        print("⚠️ No trades logged yet.")
        return None

    try:
        with open(log_path, "r") as file:
            trades = json.load(file)

        total = len(trades)
        wins = sum(1 for t in trades if t.get("result") == "take_profit")
        losses = sum(1 for t in trades if t.get("result") == "stopped")

        win_rate = (wins / total * 100) if total > 0 else 0

        print(f"📊 Total Trades: {total}, Wins: {wins}, Losses: {losses}, Win Rate: {win_rate:.2f}%")
        return {"total": total, "wins": wins, "losses": losses, "win_rate": win_rate}

    except Exception as e:
        print(f"[⚠️] Could not summarize trades: {e}")
        return None