# =====================================================
# MIDAS LIVE TRADING BOT (Paper Mode with Auto-Failover)
# =====================================================

import time
import random
import ccxt
import requests

# =====================================================
# CONFIGURATION
# =====================================================
TELEGRAM_TOKEN = "854XXXXXX9:xxxGTA4iF97rxxxxxxxxxKfSZivF0n6Uxxx"  # Your Telegram Bot Token
TELEGRAM_CHAT_ID = "970989479"  # Your Telegram Chat ID

# ✅ Supported pairs
PAIRS_TO_MONITOR = ["BTC/USDT", "SOL/USDT"]

# ⏱ Update frequency (in seconds)
SLEEP_TIME = 60

# 🌍 Proxy list (fallbacks for blocked or slow regions)
PROXIES = [
    None,
    "https://1.1.1.1:8080",
    "https://8.8.8.8:8080",
    "https://51.158.154.173:3128",
    "https://198.199.86.11:3128",
    "https://64.225.8.82:9994",
]


# =====================================================
# TELEGRAM ALERT FUNCTION
# =====================================================
def send_telegram_message(text):
    """Send alert to Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
        requests.get(url, params=params, timeout=10)
        print(f"📨 Telegram alert sent: {text}")
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")


# =====================================================
# CONNECT TO EXCHANGES (with proxy + retry logic)
# =====================================================
def connect_exchange_with_proxy(exchange_name, retries=3, delay=5):
    """
    Connects to an exchange with retry and proxy fallback.
    Returns a ccxt exchange instance or None if all attempts fail.
    """
    for attempt in range(1, retries + 1):
        proxy = random.choice(PROXIES)
        try:
            print(f"🌐 [{exchange_name.upper()}] Attempt {attempt}/{retries} — Using proxy: {proxy or 'DIRECT'}")

            if exchange_name.lower() == "bybit":
                ex = ccxt.bybit({
                    "enableRateLimit": True,
                    "timeout": 10000,
                    "proxies": {"https": proxy} if proxy else {},
                    "urls": {"api": {"public": "https://api.bybit.com", "backup": "https://api.bytick.com"}}
                })
            elif exchange_name.lower() == "okx":
                ex = ccxt.okx({
                    "enableRateLimit": True,
                    "timeout": 10000,
                    "proxies": {"https": proxy} if proxy else {},
                    "urls": {"api": {"public": "https://www.okx.com", "backup": "https://okex.com"}}
                })
            elif exchange_name.lower() == "mexc":
                ex = ccxt.mexc({
                    "enableRateLimit": True,
                    "timeout": 10000,
                    "proxies": {"https": proxy} if proxy else {},
                })
            else:
                return None

            # Try to load markets
            markets = ex.load_markets()
            print(f"✅ Connected to {exchange_name.upper()} ({len(markets)} markets) via {proxy or 'DIRECT'}")
            return ex

        except Exception as e:
            print(f"⚠️ [{exchange_name.upper()}] Connection failed (proxy={proxy or 'DIRECT'}): {e}")
            time.sleep(delay * attempt)

    print(f"❌ [{exchange_name.upper()}] All connection attempts failed after {retries} tries.")
    return None


# =====================================================
# INITIALIZE EXCHANGES
# =====================================================
def initialize_exchanges():
    print("🔗 Connecting to exchanges with proxy fallback...")

    bybit = connect_exchange_with_proxy("bybit")
    okx = connect_exchange_with_proxy("okx")
    mexc = connect_exchange_with_proxy("mexc")

    if bybit:
        send_telegram_message("✅ Connected to BYBIT successfully.")
        return bybit, "BYBIT"
    elif okx:
        send_telegram_message("✅ Connected to OKX successfully.")
        return okx, "OKX"
    elif mexc:
        send_telegram_message("✅ Connected to MEXC successfully.")
        return mexc, "MEXC"
    else:
        send_telegram_message("❌ All exchanges failed to connect. Bot halted.")
        exit()

import threading, os, time

def clear_logs_periodically():
    while True:
        try:
            os.system("truncate -s 0 /var/log/render/service.log")
        except Exception as e:
            print(f"Log cleanup failed: {e}")
        time.sleep(86400)  # Run once every 24 hours

# Run cleanup in a background thread
threading.Thread(target=clear_logs_periodically, daemon=True).start()

# =====================================================
# LIVE MONITORING (auto failover)
# =====================================================
def monitor_with_failover(pairs=PAIRS_TO_MONITOR, sleep_time=SLEEP_TIME):
    """Continuously monitor prices and auto-switch exchanges on failure."""
    global exchange, active_exchange

    while True:
        try:
            print(f"\n📡 Using {active_exchange} for live data...")
            for pair in pairs:
                ticker = exchange.fetch_ticker(pair)
                price = ticker["last"]
                print(f"💹 {pair}: {price:.2f}")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"⚠️ {active_exchange} connection error: {e}")
            send_telegram_message(f"⚠️ {active_exchange} failed. Attempting automatic failover...")

            # Attempt to reinitialize exchanges
            new_exchange, new_name = initialize_exchanges()
            exchange, active_exchange = new_exchange, new_name

            send_telegram_message(f"🔄 Switched to {active_exchange} exchange for continued monitoring.")
            print(f"🔄 Switched to {active_exchange} exchange.")
            continue


# =====================================================
# ENTRY POINT
# =====================================================
if __name__ == "__main__":
    print("🚀 Starting MIDAS Live Trading Bot (Paper Mode with Auto-Failover)...")

    exchange, active_exchange = initialize_exchanges()
    send_telegram_message("🤖 MIDAS Live Bot started successfully. Monitoring live markets...")
    monitor_with_failover(PAIRS_TO_MONITOR, sleep_time=SLEEP_TIME)
