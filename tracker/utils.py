
from typing import Any, Dict

def fmt_currency(v: float, symbol: str = '$') -> str:
    try:
        return f"{symbol}{v:,.2f}"
    except Exception:
        return str(v)

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def safe_get(d: Dict[str, Any], *path, default=None):
    cur = d
    for p in path:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur
