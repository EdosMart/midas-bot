import json, os
from datetime import datetime

def log_trade(pair, side, price, size, result="open"):
    """
    Logs trade details to 'data/trade_log.json'.
    Automatically creates the file if it doesn’t exist.
    """
    log_entry = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "pair": pair,
        "side": side,
        "price": round(price, 6),
        "size": round(size, 6),
        "result": result
    }

    log_path = os.path.join("data", "trade_log.json")

    try:
        # ✅ Load existing trades (if file exists)
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                content = f.read().strip()
                trades = json.loads(content) if content else []
        else:
            trades = []

        # ✅ Append new trade and overwrite file
        trades.append(log_entry)
        with open(log_path, "w") as f:
            json.dump(trades, f, indent=4)

        print(f"📝 Trade logged: {log_entry}")

    except Exception as e:
        print(f"⚠️ Error logging trade: {e}")