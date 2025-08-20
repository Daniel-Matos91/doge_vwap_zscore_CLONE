import pandas as pd
import numpy as np

def build_features(df: pd.DataFrame, z_lb: int, vol_lb: int, local_tz: str):
    """
    df: colunas ['timestamp','open','high','low','close','volume']
    retorna df com dt_local, vwap intraday, z-score(close-vwap), vol_ma, hour_local
    """
    d = df.copy()
    d["dt_utc"] = pd.to_datetime(d["timestamp"], unit="ms", utc=True)
    d["dt_local"] = d["dt_utc"].dt.tz_convert(local_tz)
    d["date_local"] = d["dt_local"].dt.date
    d["hour_local"] = d["dt_local"].dt.hour

    d["pv"] = d["close"] * d["volume"]
    v_cum = d.groupby("date_local")["volume"].cumsum()
    pv_cum = d.groupby("date_local")["pv"].cumsum()
    d["vwap"] = np.where(v_cum>0, pv_cum/v_cum, d["close"])

    dev = d["close"] - d["vwap"]
    std = dev.rolling(z_lb, min_periods=max(5, z_lb//2)).std()
    d["z"] = dev / std
    d["vol_ma"] = d["volume"].rolling(vol_lb, min_periods=max(5, vol_lb//2)).mean()

    return d.dropna()
