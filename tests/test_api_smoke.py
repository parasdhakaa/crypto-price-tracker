
from tracker.api import BASE

def test_base_url():
    assert BASE.startswith("https://api.coingecko.com")
