def tf_to_ms(tf: str) -> int:
    # "30m", "1h", "15m", "1d"
    num = int(''.join(ch for ch in tf if ch.isdigit()))
    unit = ''.join(ch for ch in tf if ch.isalpha()).lower()
    mult = {"m": 60_000, "h": 3_600_000, "d": 86_400_000}[unit]
    return num * mult
