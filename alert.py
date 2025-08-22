# alert.py
import os
import ccxt
import pandas as pd
from telegram_utils import send_telegram

# ===== Config =====
SYMBOL        = os.getenv("SYMBOL", "DOGE/USDT:USDT")
INTERVAL      = os.getenv("INTERVAL", "30m")
LIMIT         = int(os.getenv("LIMIT", "500"))
EXCHANGE      = os.getenv("EXCHANGE", "okx")  # "okx" ou "bybit"
LOCAL_TZ      = os.getenv("LOCAL_TZ", "Europe/Lisbon")

# Parâmetros da estratégia (alinhados com os backtests)
Z_ENTRY       = float(os.getenv("Z_ENTRY", "1.0"))
TP_MULT       = float(os.getenv("TP_MULT", "2.0"))
Z_LOOKBACK    = int(os.getenv("Z_LOOKBACK", "80"))

def connect_exchange(name: str):
    name = name.lower()
    if name == "okx":
        ex = ccxt.okx({"enableRateLimit": True, "options": {"defaultType": "swap"}})
    elif name == "bybit":
        ex = ccxt.bybit({"enableRateLimit": True, "options": {"defaultType": "swap", "defaultSubType": "linear"}})
    else:
        ex = ccxt.okx({"enableRateLimit": True, "options": {"defaultType": "swap"}})
    ex.load_markets()
    return ex

def fetch_ohlcv(ex, symbol, interval, limit):
    rows = ex.fetch_ohlcv(symbol, interval, limit=limit)
    df = pd.DataFrame(rows, columns=["ts","o","h","l","c","v"])
    df["dt_utc"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df["dt_local"] = df["dt_utc"].dt.tz_convert(LOCAL_TZ)
    return df

def compute_vwap_and_z(df: pd.DataFrame, z_lb: int) -> pd.DataFrame:
    d = df.copy()
    # VWAP acumulado simples
    d["tp"] = (d["h"] + d["l"] + d["c"]) / 3.0
    d["pv"] = d["tp"] * d["v"]
    d["vwap"] = (d["pv"].cumsum() / d["v"].cumsum())
    # Z-score do close
    d["z"] = (d["c"] - d["c"].rolling(z_lb).mean()) / d["c"].rolling(z_lb).std()
    d = d.dropna()
    return d

def main():
    ex = connect_exchange(EXCHANGE)
    print(f"[INFO] Connected to {ex.id.upper()} | symbol={SYMBOL} | timeframe={INTERVAL}")

    df = fetch_ohlcv(ex, SYMBOL, INTERVAL, LIMIT)
    if df.empty or len(df) < max(50, Z_LOOKBACK+5):
        print("[WARN] Dados insuficientes.")
        return

    feat = compute_vwap_and_z(df, Z_LOOKBACK)
    last = feat.iloc[-1]
    price = float(last["c"])
    vwap  = float(last["vwap"])
    z     = float(last["z"])
    tloc  = last["dt_local"].strftime("%Y-%m-%d %H:%M %Z")

    # ===== Estratégia / decisão =====
    signal = None
    entry = tp = sl = None

    # distância de risco baseada no desvio até o VWAP
    dist = abs(price - vwap)
    if dist <= 0:
        dist = max(price * 0.001, 1e-6)  # fallback mínimo

    if z <= -Z_ENTRY:
        # LONG: z-score muito negativo
        signal = "LONG"
        entry = price
        sl = entry - dist               # SL sempre ABAIXO da entrada
        tp = entry + TP_MULT * dist     # TP múltiplo do risco
    elif z >= Z_ENTRY:
        # SHORT: z-score muito positivo
        signal = "SHORT"
        entry = price
        sl = entry + dist               # SL sempre ACIMA da entrada
        tp = entry - TP_MULT * dist     # TP múltiplo do risco
    else:
        signal = "HOLD"

    # ===== Envio =====
    if signal == "HOLD":
        msg = (
            f"⚪ <b>HOLD</b> — {SYMBOL} {INTERVAL}\n"
            f"• Preço: <code>{price:.6f}</code>\n"
            f"• VWAP:  <code>{vwap:.6f}</code>\n"
            f"• Z:     <code>{z:.2f}</code> (−{Z_ENTRY} … +{Z_ENTRY})\n"
            f"• Horário: {tloc}"
        )
        send_telegram(msg)
        print("[INFO] Sinal = HOLD")
        return

    # Se for LONG/SHORT, calcula % de TP/SL
    tp_pct = (tp - entry) / entry * 100.0
    sl_pct = (sl - entry) / entry * 100.0
    side_emoji = "🟢" if signal == "LONG" else "🔴"

    msg = (
        f"{side_emoji} <b>SINAL {signal}</b> — {SYMBOL} {INTERVAL}\n"
        f"• Entrada: <code>{entry:.6f}</code>\n"
        f"• TP:      <code>{tp:.6f}</code>  ({tp_pct:+.2f}%)  [TP_MULT={TP_MULT}]\n"
        f"• SL:      <code>{sl:.6f}</code>  ({sl_pct:+.2f}%)\n"
        f"• VWAP:    <code>{vwap:.6f}</code>\n"
        f"• Z:       <code>{z:.2f}</code>  (limiar={Z_ENTRY})\n"
        f"• Horário: {tloc}"
    )
    ok = send_telegram(msg)
    print("[INFO]", "Alert OK" if ok else "Alert falhou")

if __name__ == "__main__":
    main()
    
