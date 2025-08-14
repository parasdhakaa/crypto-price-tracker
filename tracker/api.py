
import requests
from typing import List, Dict, Any

BASE = "https://api.coingecko.com/api/v3"

def top_market_coins(vs: str = "usd", per_page: int = 100) -> List[Dict[str, Any]]:
    url = f"{BASE}/coins/markets"
    params = {
        "vs_currency": vs,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": "true",
        "price_change_percentage": "1h,24h,7d"
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def simple_price(ids: List[str], vs: str = "usd") -> Dict[str, Any]:
    url = f"{BASE}/simple/price"
    params = {"ids": ",".join(ids), "vs_currencies": vs}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()
