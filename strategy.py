import pandas as pd

def make_signals(df: pd.DataFrame, z_entry: float, vol_spike_mult: float, hour_window: str):
    # filtro de janela
    if hour_window == "lisbon_13_17":
        inwin = df["hour_local"].between(13, 17)
    else:
        inwin = pd.Series(True, index=df.index)

    vol_ok = df["volume"] > (vol_spike_mult * df["vol_ma"])
    long_sig  = (df["z"] >  z_entry) & vol_ok & inwin
    short_sig = (df["z"] < -z_entry) & vol_ok & inwin

    # retorna DataFrame apenas com a última barra fechada marcada (decidimos no alert.py)
    out = df[["timestamp","dt_local","close","vwap"]].copy()
    out["long"] = long_sig
    out["short"] = short_sig
    return out
