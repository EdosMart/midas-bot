from core.midas_capital_tracker import load_capital, update_capital

print("💰 Loading capital data...")
capital = load_capital()
print(f"Starting balance: ${capital['current_balance']:.2f}")

# ✅ Simulate a winning trade (+2%)
profit_win = capital['current_balance'] * 0.02
capital = update_capital(profit_win, is_win=True)

# ✅ Simulate a losing trade (-1%)
loss_trade = -capital['current_balance'] * 0.01
capital = update_capital(loss_trade, is_win=False)

print("\n📊 Final Capital Summary:")
print(f"Current Balance: ${capital['current_balance']:.2f}")
print(f"Total Trades: {capital['total_trades']}")
print(f"Wins: {capital['win_trades']} | Losses: {capital['loss_trades']}")
print(f"Total Profit: ${capital['total_profit']:.2f}")
print(f"Total Loss: ${capital['total_loss']:.2f}")