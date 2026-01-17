import itertools
import json
import os
from datetime import datetime
import pandas as pd
import importlib.util
from tqdm import tqdm
import time

# =====================================================
# CONFIGURATION
# =====================================================
PAIR = "BTCUSDT"
BOT_FILE = "midas_multiframe_backtest_v2.py"
BEST_FILE = "midas_best_config.json"
PROGRESS_FILE = "optimizer_progress_finetune_safe.csv"
RESULTS_FILE = "midas_finetune_light_results.xlsx"

SAVE_INTERVAL = 20  # autosave after every N configurations


# =====================================================
# LOAD BACKTEST ENGINE
# =====================================================
def load_bot_module(filepath):
    """Dynamically load midas_multiframe_backtest_v2.py as a module."""
    spec = importlib.util.spec_from_file_location("midas_engine", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bot = load_bot_module(BOT_FILE)


# =====================================================
# LOAD BASE CONFIG
# =====================================================
if not os.path.exists(BEST_FILE):
    print(f"⚠️ No {BEST_FILE} found. Using default base config.")
    base_config = {
        "rsi_bullish": 50,
        "rsi_bearish": 46,
        "adx_min": 16,
        "ema_fast": 8,
        "ema_slow": 40,
        "take_profit": 1.6,
        "stop_mult": 1.3,
        "win_rate": 0,
        "profit": 0,
        "trades": 0,
        "score": 0
    }
else:
    with open(BEST_FILE, "r") as f:
        base_config = json.load(f)

print("✨ Loaded previous best config:")
print(json.dumps(base_config, indent=4))


# =====================================================
# CREATE PARAMETER GRID (NARROW RANGE AROUND BEST CONFIG)
# =====================================================
param_grid = {
    "rsi_bullish": [base_config["rsi_bullish"] - 2, base_config["rsi_bullish"], base_config["rsi_bullish"] + 2],
    "rsi_bearish": [base_config["rsi_bearish"] - 2, base_config["rsi_bearish"], base_config["rsi_bearish"] + 2],
    "adx_min": [base_config["adx_min"] - 2, base_config["adx_min"], base_config["adx_min"] + 2],
    "ema_fast": [base_config["ema_fast"] - 2, base_config["ema_fast"], base_config["ema_fast"] + 2],
    "ema_slow": [base_config["ema_slow"] - 10, base_config["ema_slow"], base_config["ema_slow"] + 10],
    "take_profit": [base_config["take_profit"] - 0.2, base_config["take_profit"], base_config["take_profit"] + 0.2],
    "stop_mult": [base_config["stop_mult"] - 0.2, base_config["stop_mult"], base_config["stop_mult"] + 0.2],
}

configs = []
for combo in itertools.product(*param_grid.values()):
    cfg = dict(zip(param_grid.keys(), combo))
    configs.append(cfg)

print(f"\n🧮 Total fine-tune configurations: {len(configs)}")


# =====================================================
# LOAD MARKET DATA ONCE
# =====================================================
print("\n🧠 Loading market data (5m + 15m only for speed)...")
try:
    df5 = bot.load_csv(PAIR, "5m")
    df15 = bot.load_csv(PAIR, "15m")
    preloaded_data = {"df5": df5, "df15": df15, "df30": df5.head(10), "df1h": df5.head(10)}  # lightweight placeholders
except Exception as e:
    print(f"❌ Failed to load data: {e}")
    preloaded_data = None


# =====================================================
# LOAD PROGRESS (RESUME SUPPORT)
# =====================================================
if os.path.exists(PROGRESS_FILE):
    try:
        df_progress = pd.read_csv(PROGRESS_FILE)
        tested = len(df_progress)
        print(f"🔁 Resuming from {PROGRESS_FILE} ({tested} completed configs).")
        completed_configs = df_progress.to_dict("records")
    except Exception:
        print("⚠️ Progress file corrupted. Starting fresh.")
        df_progress = pd.DataFrame()
        completed_configs = []
else:
    print("🆕 Starting fresh optimization run.")
    df_progress = pd.DataFrame()
    completed_configs = []

# Skip configs already tested
completed_set = {tuple(sorted(cfg.items())) for cfg in completed_configs}
remaining_configs = [cfg for cfg in configs if tuple(sorted(cfg.items())) not in completed_set]


# =====================================================
# MAIN FINE-TUNING LOOP
# =====================================================
print("🚀 Running safe fine-tuning loop...")

results = []
counter = 0
start_time = time.time()

for cfg in tqdm(remaining_configs, desc="⚙️ Safe Fine-Tuning", ncols=80):
    try:
        result = bot.run_backtest_with_params(cfg, preloaded_data)
        result.update(cfg)
        results.append(result)
    except Exception as e:
        print(f"⚠️ Error in config {cfg}: {e}")
        continue

    counter += 1

    # Autosave progress every N runs
    if counter % SAVE_INTERVAL == 0:
        df_progress = pd.concat([df_progress, pd.DataFrame(results)], ignore_index=True)
        df_progress.to_csv(PROGRESS_FILE, index=False)
        results = []
        print(f"💾 Progress autosaved ({counter}/{len(configs)})")

# Final save after loop
if results:
    df_progress = pd.concat([df_progress, pd.DataFrame(results)], ignore_index=True)
df_progress.to_csv(PROGRESS_FILE, index=False)

# =====================================================
# ANALYZE & SAVE RESULTS
# =====================================================
if "score" in df_progress.columns and not df_progress["score"].isna().all():
    best = df_progress.sort_values("score", ascending=False).iloc[0].to_dict()

    print("\n🏆 Best Fine-Tuned Parameters Found:")
    for k, v in best.items():
        print(f"   {k}: {v}")

    # Update best config file
    with open(BEST_FILE, "w") as f:
        json.dump(best, f, indent=4)

else:
    print("⚠️ No valid 'score' column found — skipping sort.")

# Save to Excel
try:
    df_progress.to_excel(RESULTS_FILE, index=False)
    print(f"📁 Results saved to: {RESULTS_FILE}")
except PermissionError:
    alt_name = f"midas_finetune_light_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df_progress.to_excel(alt_name, index=False)
    print(f"⚠️ Excel open — saved to {alt_name} instead.")

print("\n🏁 Fine-tuning completed safely and saved successfully.")

