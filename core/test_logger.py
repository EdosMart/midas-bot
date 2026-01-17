from core.midas_logger import log_trade
import json, os

log_trade("XRP/USDT", "buy", 0.5471, 25, result="open")

log_path = os.path.join("data", "trade_log.json")

if os.path.exists(log_path):
    with open(log_path, "r") as f:
        content = f.read().strip()
        if not content:
            print("⚠️ trade_log.json is empty.")
        else:
            try:
                data = json.loads(content)
                print("✅ Trade successfully logged! Latest entry:")
                print(data[-1])
            except json.JSONDecodeError:
                print("⚠️ trade_log.json is malformed. Check formatting.")
else:
    print("❌ trade_log.json not found.")