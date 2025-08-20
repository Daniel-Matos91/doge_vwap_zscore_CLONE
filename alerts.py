import os, requests

TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG_CHAT  = os.getenv("TELEGRAM_CHAT_ID", "")

def notify(text: str):
    ok = False
    if TG_TOKEN and TG_CHAT:
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TG_CHAT, "text": text, "parse_mode": "HTML"}, timeout=15)
            ok = True
        except Exception:
            pass
    if DS_HOOK:
        try:
            requests.post(DS_HOOK, json={"content": text}, timeout=15)
            ok = True
        except Exception:
            pass
    return ok
