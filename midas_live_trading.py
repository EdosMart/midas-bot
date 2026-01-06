import ccxt
import time
from datetime import datetime, timezone
import requests
import os

# ==========================
# CONFIGURATION
# ==========================

PAIRS_TO_MONITOR = ["SOL/USDT"]
INTERVAL = 60  # seconds
EXCHANGES = ["bybit", "mexc"]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "854XXXXXX9:xxxGTA4iF97rxxxxxxxxxKfSZivF0n6Uxxx")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "970989479")

MODE = os.getenv("MODE", "paper")  # "live" or "paper"

# ==========================
# TELEGRAM UTILITY
# ==========================

def send_telegram_message(msg: str):
    """Send message to Telegram chat"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"[⚠️ Telegram Error] {e}")


# ==========================
# EXCHANGE CONNECTION
# ==========================

def connect_exchange(name):
    """Initialize connection to exchange"""
    try:
        if name == "bybit":
            ex = ccxt.bybit()
        elif name == "mexc":
            ex = ccxt.mexc()
        else:
            raise ValueError(f"Unknown exchange: {name}")

        markets = ex.load_markets()
        print(f"✅ Connected to {name.upper()} ({len(markets)} markets)")
        return ex
    except Exception as e:
        print(f"⚠️ Failed to connect to {name.upper()}: {e}")
        return None


# ==========================
# MONITORING LOOP
# ==========================

def monitor_with_failover(pairs=PAIRS_TO_MONITOR, interval=INTERVAL):
    """Continuously monitor prices and auto-switch exchanges on failure"""
    active_exchange = None
    exchange = None

    # Try connecting to the first available exchange
    for name in EXCHANGES:
        exchange = connect_exchange(name)
        if exchange:
            active_exchange = name
            break

    if not exchange:
        print("❌ Could not connect to any exchange. Exiting.")
        send_telegram_message("❌ MIDAS BOT: No exchange connections available.")
        return

    send_telegram_message(f"🚀 MIDAS {MODE.upper()} Bot started on {active_exchange.upper()} — Monitoring {', '.join(pairs)}")

    while True:
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            for pair in pairs:
                try:
                    ticker = exchange.fetch_ticker(pair)
                    price = ticker["last"]
                    print(f"[{timestamp}] {pair}: ${price:.2f}")
                except Exception as sub_e:
                    print(f"[⚠️] Failed to fetch {pair} from {active_exchange}: {sub_e}")

            time.sleep(interval)

        except Exception as e:
            print(f"[❌] Major error in loop: {e}")
            send_telegram_message(f"[⚠️] MIDAS BOT ERROR: {e}")

            # Attempt failover
            for name in EXCHANGES:
                if name != active_exchange:
                    exchange = connect_exchange(name)
                    if exchange:
                        print(f"[🔁] Switched from {active_exchange.upper()} to {name.upper()}")
                        active_exchange = name
                        send_telegram_message(f"🔁 Switched from {active_exchange.upper()} to {name.upper()}")
                        break

            time.sleep(10)


# ==========================
# ENTRY POINT
# ==========================

if _name_ == "_main_":
    print(f"🚀 Starting MIDAS {MODE.upper()} Trading Bot...")
    monitor_with_failover()