import os
import requests

def send_telegram(message: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("[ERROR] TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"[INFO] Telegram OK: {message}")
        else:
            print(f"[ERROR] Telegram status {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[ERROR] Falha ao enviar para Telegram: {e}")
