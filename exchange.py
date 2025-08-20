import ccxt
from config import EXCHANGE_PREFERRED, PROXY_BASE, PROXY_BASE_ALT

def make_exchange(name: str, proxy_base: str | None):
    cfg = {"enableRateLimit": True, "options": {"defaultType": "swap"}}
    if proxy_base:
        pb = proxy_base.rstrip("/")
        cfg["urls"] = {"api": {"public": pb, "private": pb}}
    if name == "bybit":
        cfg["options"].update({"defaultSubType": "linear"})
        ex = ccxt.bybit(cfg)
    elif name == "okx":
        ex = ccxt.okx(cfg)
    else:
        raise ValueError("exchange inválida")
    ex.load_markets()
    return ex

def resolve_symbol(ex, hints=("DOGE/USDT:USDT","DOGE/USDT")):
    for h in hints:
        if h in ex.markets:
            return h
    for m, info in ex.markets.items():
        if info.get("type")=="swap" and info.get("linear") and info.get("base")=="DOGE" and info.get("quote")=="USDT":
            return m
    raise ValueError("DOGE perp não encontrado")

def connect_with_fallback():
    # preferido (sem proxy)
    try:
        ex = make_exchange(EXCHANGE_PREFERRED, None)
        sym = resolve_symbol(ex)
        return ex, sym, EXCHANGE_PREFERRED
    except Exception:
        pass
    # bybit via proxies
    for pb in (PROXY_BASE, PROXY_BASE_ALT):
        if not pb:
            continue
        try:
            ex = make_exchange("bybit", pb)
            sym = resolve_symbol(ex)
            return ex, sym, "bybit"
        except Exception:
            pass
    # okx final
    ex = make_exchange("okx", None)
    sym = resolve_symbol(ex)
    return ex, sym, "okx"
