import time
import pandas as pd
from config import SYMBOL, TIMEFRAME, LOCAL_TZ, HOUR_WINDOW, Z_ENTRY, VOL_SPIKE_MULT, TP_MULT, Z_LOOKBACK, VOL_LOOKBACK, HISTORY_BARS, FEE_PER_SIDE, SLIPPAGE_PER_SIDE
from exchange import connect_with_fallback
from features import build_features
from strategy import make_signals
from utils import tf_to_ms
from alerts import notify

def fetch_tail(ex, symbol, timeframe, limit=500):
    rows = ex.fetch_ohlcv(symbol, timeframe, limit=limit)
    return pd.DataFrame(rows, columns=["timestamp","open","high","low","close","volume"])

def main():
    ex, sym, src = connect_with_fallback()
    print(f"[INFO] Connected to {src.upper()} | symbol={sym} | timeframe={TIMEFRAME}")

    df = fetch_tail(ex, sym, TIMEFRAME, limit=HISTORY_BARS)
    if df.empty:
        print("[WARN] Empty OHLCV"); return

    feat = build_features(df, Z_LOOKBACK, VOL_LOOKBACK, LOCAL_TZ)
    if feat.empty:
        print("[WARN] Not enough data for features"); return

    sigs = make_signals(feat, Z_ENTRY, VOL_SPIKE_MULT, HOUR_WINDOW)
    # última barra FECHADA: timestamp <= now - timeframe_ms
    now_ms = ex.milliseconds()
    closed_mask = sigs["timestamp"] <= (now_ms - tf_to_ms(TIMEFRAME))
    if not closed_mask.any():
        print("[INFO] No closed candle yet")
        return

    last = sigs[closed_mask].iloc[-1]
    long_sig = bool(last["long"]); short_sig = bool(last["short"])

    if not (long_sig or short_sig):
        print("[INFO] No signal @", last["dt_local"])
        return

    side = "LONG" if long_sig else "SHORT"
    px = float(last["close"])
    vw = float(last["vwap"])
    dist = abs(px - vw)
    tp = px + TP_MULT*dist if long_sig else px - TP_MULT*dist
    sl = vw

    cost_bps = (FEE_PER_SIDE + SLIPPAGE_PER_SIDE) * 10000.0
    text = (
        f"⚡ <b>SINAL {side}</b> — DOGEUSDT {TIMEFRAME}\n"
        f"• Fechamento: {last['dt_local']}\n"
        f"• Close={px:.6f}  VWAP={vw:.6f}  |  z>=±{Z_ENTRY}\n"
        f"• TP={tp:.6f}  SL={sl:.6f}  (TP_MULT={TP_MULT})\n"
        f"• Janela: {HOUR_WINDOW}  |  Custos ~{cost_bps:.1f} bps/lado\n"
        f"• Execução sugerida: <b>open da próxima barra</b>"
    )
    ok = notify(text)
    print(("[ALERT]" if ok else "[ALERT-LOCAL]"), text.replace("\n"," | "))

if __name__ == "__main__":
    main()
