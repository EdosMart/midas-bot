import os
import json
from datetime import datetime

CAPITAL_FILE = os.path.join("data", "capital_tracker.json")

def _init_capital():
    """Initializes the capital file if it doesn't exist."""
    return {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "starting_balance": 100.0,
        "current_balance": 100.0,
        "total_profit": 0.0,
        "total_loss": 0.0,
        "win_trades": 0,
        "loss_trades": 0,
        "total_trades": 0
    }

def load_capital():
    """Loads existing capital data or initializes a new record."""
    if not os.path.exists(CAPITAL_FILE) or os.path.getsize(CAPITAL_FILE) == 0:
        capital = _init_capital()
        save_capital(capital)
        return capital
    with open(CAPITAL_FILE, "r") as f:
        return json.load(f)

def save_capital(data):
    """Saves capital data to file."""
    os.makedirs(os.path.dirname(CAPITAL_FILE), exist_ok=True)
    with open(CAPITAL_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_capital(profit, is_win=True):
    """Updates capital based on trade outcome."""
    capital = load_capital()
    capital["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    capital["total_trades"] += 1
    capital["current_balance"] += profit

    if is_win:
        capital["total_profit"] += profit
        capital["win_trades"] += 1
    else:
        capital["total_loss"] += abs(profit)
        capital["loss_trades"] += 1

    save_capital(capital)
    print(f"💰 Capital updated — New balance: ${capital['current_balance']:.2f}")
    return capital

def reset_daily_capital():
    """Resets capital data for a new day (retains total values)."""
    capital = load_capital()
    capital["starting_balance"] = capital["current_balance"]
    capital["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    save_capital(capital)
    print("🕛 Daily capital reset completed.")
    return capital

def log_sync_event(source="MEXC", status="synced"):
    """Logs when a capital sync happens."""
    capital = load_capital()
    event = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "status": status,
        "balance": capital["current_balance"]
    }
    print(f"🔄 Balance {status} from {source} — ${capital['current_balance']:.2f}")
    return event