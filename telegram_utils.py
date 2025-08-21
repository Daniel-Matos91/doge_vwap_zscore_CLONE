# telegram_utils.py
import os
import requests

def send_telegram(message: str) -> bool:
    """
    Envia 'message' ao Telegram.
    Aceita secrets com os nomes:
      - TELEGRAM_BOT_TOKEN  (preferido)  ou  TELEGRAM_TOKEN
      - TELEGRAM_CHAT_ID    (preferido)  ou  CHAT_ID
    Retorna True/False conforme sucesso no envio.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

    if not token or not chat_id:
        print("[WARN] Telegram não configurado: defina TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID (ou TELEGRAM_TOKEN/CHAT_ID).")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            print("[INFO] Telegram enviado.")
            return True
        else:
            print(f"[TG-ERR] {r.status_code} {r.text[:200]}")
            return False
    except Exception as e:
        print("[TG-EXC]", e)
        return False
