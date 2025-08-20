import os

# Exchange / Proxy
EXCHANGE_PREFERRED = os.getenv("EXCHANGE_PREFERRED", "bybit")  # "bybit" ou "okx"
# Seu Worker (e a variante 'workers.dev' para fallback leve)
PROXY_BASE = os.getenv("PROXY_BASE", "https://dogeusdt.danielmatos-contatos.workes.dev")
PROXY_BASE_ALT = os.getenv("PROXY_BASE_ALT", "https://dogeusdt.danielmatos-contatos.workers.dev")

# Símbolo / timeframe
SYMBOL = os.getenv("SYMBOL", "DOGE/USDT:USDT")
TIMEFRAME = os.getenv("TIMEFRAME", "30m")
LOCAL_TZ = os.getenv("LOCAL_TZ", "Europe/Lisbon")
HOUR_WINDOW = os.getenv("HOUR_WINDOW", "all")  # "all" ou "lisbon_13_17"

# Parâmetros agressivos padrão (vindos do seu backtest 30m)
Z_ENTRY = float(os.getenv("Z_ENTRY", "1.0"))
VOL_SPIKE_MULT = float(os.getenv("VOL_SPIKE_MULT", "1.5"))
TP_MULT = float(os.getenv("TP_MULT", "2.0"))
Z_LOOKBACK = int(os.getenv("Z_LOOKBACK", "80"))
VOL_LOOKBACK = int(os.getenv("VOL_LOOKBACK", "40"))

# Custos (informativo no alerta)
FEE_PER_SIDE = float(os.getenv("FEE_PER_SIDE", "0.0005"))       # 0.05%
SLIPPAGE_PER_SIDE = float(os.getenv("SLIPPAGE_PER_SIDE", "0.0002"))  # 0.02%

# Polling local (não usado no Actions, mas útil se rodar contínuo)
POLL_SEC = int(os.getenv("POLL_SEC", "15"))
HISTORY_BARS = int(os.getenv("HISTORY_BARS", "500"))  # barras para zscore/vol_ma (>= max lookback)
