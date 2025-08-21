import os
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from telegram_utils import send_telegram

# ===== Config =====
SYMBOL       = os.getenv("SYMBOL", "DOGE/USDT:USDT")
INTERVAL     = os.getenv("INTERVAL", "30m")
LIMIT        = int(os.getenv("LIMIT", "500"))
EXCHANGE     = os.getenv("EXCHANGE", "okx")
Z_ENTRY      = float(os.getenv("Z_ENTRY", "1.0"))
TP_MULT      = float(os.getenv("TP_MULT", "2.0"))

# ===== Exchange =====
if EXCHANGE == "okx":
    exchange = ccxt.okx()
else:
    exchange = ccxt.binance()

print(f"[INFO] Connected to {exchange.id.upper()} | symbol={SYMBOL} | timeframe={INTERVAL}")

# ===== Funções =====
def fetch_ohlcv(symbol, interval, limit):
    data = exchange.fetch_ohlcv(symbol, interval, limit=limit)
    df = pd.DataFrame(data, columns=["ts","o","h","l","c","v"])
    df["dt"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    return df

def compute_vwap_z(df, lookback=120):
    df["tp"] = (df["h"] + df["l"] + df["c"]) / 3
    df["vwap"] = (df["tp"] * df["v"]).cumsum() / df["v"].cumsum()
    df["zscore"] = (df["c"] - df["c"].rolling(lookback).mean()) / df["c"].rolling(lookback).std()
    return df

# ===== Estratégia =====
df = fetch_ohlcv(SYMBOL, INTERVAL, LIMIT)
df = compute_vwap_z(df)

last = df.iloc[-1]
price = last["c"]
zscore = last["zscore"]

signal = None
entry, tp, sl = None, None, None

if zscore >= Z_ENTRY:
    signal = "LONG"
    entry = price
    tp = entry * (1 + (TP_MULT * (zscore / 100)))
    sl = entry * (1 - (1.0 * (zscore / 100)))

elif zscore <= -Z_ENTRY:
    signal = "SHORT"
    entry = price
    tp = entry * (1 - (TP_MULT * (abs(zscore) / 100)))
    sl = entry * (1 + (1.0 * (abs(zscore) / 100)))

else:
    signal = "HOLD"

# ===== Telegram =====
if signal == "HOLD":
    # Envia "HOLD" só se você quiser ver — senão pode comentar essa parte
    msg = (
        f"⏸ *HOLD Detected*\n"
        f"Par: `{SYMBOL}`\n"
        f"Preço atual: `{price:.5f}`\n"
        f"Z-Score: `{zscore:.2f}`\n"
        f"Hora: {last['dt'].strftime('%Y-%m-%d %H:%M UTC')}"
    )
    print("[INFO] Sinal = HOLD")
    send_telegram(msg)

elif signal in ["LONG", "SHORT"]:
    msg = (
        f"📊 *Sinal Detectado*\n"
        f"Par: `{SYMBOL}`\n"
        f"Direção: *{signal}*\n"
        f"Entrada: `{entry:.5f}`\n"
        f"TP: `{tp:.5f}`\n"
        f"SL: `{sl:.5f}`\n"
        f"Z-Score: `{zscore:.2f}`\n"
        f"Hora: {last['dt'].strftime('%Y-%m-%d %H:%M UTC')}"
    )
    print("[INFO] Sinal gerado, enviando para Telegram...")
    send_telegram(msg)
else:
    print("[INFO] Nenhum sinal calculado.")

