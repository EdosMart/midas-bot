import json
import os
from datetime import datetime

# Path to the trade log file
TRADE_LOG_FILE = os.path.join(os.path.dirname(__file__), "trade_log.json")


def log_trade(timestamp, pair, side, price, size, result="open"):
    """
    Logs each trade into trade_log.json without overwriting old data.
    Automatically repairs corrupted or non-list JSON files.
    """

    new_entry = {
        "timestamp": timestamp,
        "pair": pair,
        "side": side,
        "price": round(float(price), 6),
        "size": round(float(size), 3),
        "result": result
    }

    # ✅ Load existing trade data safely
    data = []
    if os.path.exists(TRADE_LOG_FILE):
        try:
            with open(TRADE_LOG_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
                if isinstance(existing, list):
                    data = existing
                else:
                    # Convert a single dict into a list
                    data = [existing]
        except json.JSONDecodeError:
            print("⚠️ Warning: trade_log.json was corrupted. Rebuilding...")
            data = []

    # ✅ Append the new trade
    data.append(new_entry)

    # ✅ Write back cleanly
    with open(TRADE_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"📝 Trade logged: {new_entry}")
    return new_entry


def log_message(message):
    """Utility function for basic console + file logging (optional)."""
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(log_entry)


def reset_trade_log():
    """Clears the trade log — useful for starting a new test session."""
    with open(TRADE_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)
    print("🧹 Trade log reset successfully.")


# Run directly for quick test
if __name__ == "__main__":
    print("🔧 Testing trade logging system...")

    # Simulate two test trades
    log_trade(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "XRP/USDT", "buy", 0.5471, 25)
    log_trade(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "BTC/USDT", "sell", 92500.55, 0.15, "closed")

    print("✅ Logging test complete. Check trade_log.json.")