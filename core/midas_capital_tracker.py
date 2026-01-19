import json
import os
from datetime import datetime

# File to store current capital
CAPITAL_FILE = os.path.join(os.path.dirname(__file__), "capital_tracker.json")


def load_capital():
    """
    Loads the last known capital balance from file.
    If not found, initializes with 100 (default starting balance).
    """
    if os.path.exists(CAPITAL_FILE):
        try:
            with open(CAPITAL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "capital" in data:
                    return data["capital"]
        except json.JSONDecodeError:
            print("⚠️ Corrupted capital file detected. Resetting...")
    # Default capital if missing or broken
    save_capital(100.0)
    return 100.0


def save_capital(capital):
    """Saves the current capital value safely."""
    with open(CAPITAL_FILE, "w", encoding="utf-8") as f:
        json.dump({"capital": round(float(capital), 2)}, f, indent=4)
    print(f"💰 Capital saved: ${capital:.2f}")


def update_capital(result: str, profit_pct: float, balance=None):
    """
    Updates capital based on trade result (WIN / LOSS / BREAKEVEN).
    Automatically saves new balance to JSON.
    """
    capital = load_capital() if balance is None else balance

    if result == "WIN":
        capital *= (1 + profit_pct)
    elif result == "LOSS":
        capital *= (1 - profit_pct)
    elif result == "BREAKEVEN":
        pass  # no change

    save_capital(capital)
    print(f"💹 Updated capital after {result}: ${capital:.2f}")
    return capital


def reset_daily_capital():
    """Resets daily capital at midnight (or testing start)."""
    base = load_capital()
    print(f"🕛 Daily capital reset completed. Starting with: ${base:.2f}")
    return base


if __name__ == "__main__":
    print("🔧 Testing capital tracker...")

    capital = load_capital()
    print(f"Starting capital: ${capital:.2f}")

    update_capital("WIN", 0.02)
    update_capital("LOSS", 0.015)
    reset_daily_capital()