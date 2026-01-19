import os
import json
from datetime import datetime

# Define all data file paths
BASE_DIR = os.path.dirname(__file__)

DATA_FILES = {
    "trade_log": os.path.join(BASE_DIR, "trade_log.json"),
    "capital_tracker": os.path.join(BASE_DIR, "capital_tracker.json"),
    "daily_summary": os.path.join(BASE_DIR, "daily_summary.json")
}


def ensure_json_list(file_path):
    """
    Ensures the file contains a valid JSON list.
    If missing or corrupted, resets to [].
    """
    if not os.path.exists(file_path):
        print(f"⚠️ File missing — creating new: {os.path.basename(file_path)}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert dict → list
        if isinstance(data, dict):
            print(f"🩹 Repairing: {os.path.basename(file_path)} (dict → list)")
            data = [data]

        # If empty or invalid, reinit
        if not isinstance(data, list):
            raise ValueError("Invalid JSON format")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    except (json.JSONDecodeError, ValueError):
        print(f"⚠️ Corrupted file repaired: {os.path.basename(file_path)}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)


def ensure_capital_tracker(file_path):
    """
    Ensures the capital tracker file is valid and has a numeric capital entry.
    """
    default_capital = {"capital": 100.0}
    if not os.path.exists(file_path):
        print("⚠️ Missing capital tracker — creating new with $100 balance.")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_capital, f, indent=4)
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict) or "capital" not in data:
            raise ValueError("Invalid format for capital tracker")

        # Repair non-numeric values
        data["capital"] = round(float(data.get("capital", 100.0)), 2)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    except (json.JSONDecodeError, ValueError):
        print("⚠️ Corrupted capital tracker repaired.")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_capital, f, indent=4)


def run_data_safety_check():
    """
    Scans and repairs all critical MIDAS data files.
    """
    print("🔍 Running MIDAS Data Safety Check...\n")

    ensure_json_list(DATA_FILES["trade_log"])
    ensure_capital_tracker(DATA_FILES["capital_tracker"])
    ensure_json_list(DATA_FILES["daily_summary"])

    print("\n✅ Data integrity check complete.")
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("---------------------------------------------------")


if __name__ == "__main__":
    run_data_safety_check()