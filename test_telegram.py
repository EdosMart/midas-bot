import requests

BOT_TOKEN = "8545188339:AAEGTA4iF97r6PzP5KPtLKfSZivF0n6U3Q8"
CHAT_ID = "970989479"
MESSAGE = "✅ Telegram connectivity confirmed (Midas Engine)."

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": MESSAGE}
res = requests.post(url, json=payload)
print(res.text)