import requests

BOT_TOKEN = "8152460819:AAF_se8ZXk6w2cjwleTrUVPoX3FaCCSesXI"
CHAT_ID = "970989479"
MESSAGE = "✅ Telegram connectivity confirmed (Midas Engine)."

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": MESSAGE}
res = requests.post(url, json=payload)
print(res.text)