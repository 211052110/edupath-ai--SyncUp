"""
Live data fetcher for:
1. World Bank GDP per capita (free, no key) — used as salary multiplier
2. Exchange rates via open.exchangerate-api.com (free, no key)

Results are cached in-memory for 24h to avoid hammering APIs.
Fallback to hardcoded values if API is unavailable.
"""

import time
import httpx
from typing import Optional

CACHE_TTL = 60 * 60 * 24  # 24 hours

# { key: (value, timestamp) }
_cache: dict[str, tuple] = {}

# World Bank country codes
WB_COUNTRY_CODES = {
    "USA": "US", "Germany": "DE", "UK": "GB", "Canada": "CA",
    "Australia": "AU", "Netherlands": "NL", "Singapore": "SG",
    "Ireland": "IE", "New Zealand": "NZ", "Sweden": "SE",
}

# Fallback GDP per capita (USD, 2024 estimates)
GDP_FALLBACK = {
    "USA": 82000, "Germany": 54000, "UK": 49000, "Canada": 57000,
    "Australia": 65000, "Netherlands": 61000, "Singapore": 88000,
    "Ireland": 103000, "New Zealand": 48000, "Sweden": 58000,
}

# Fallback exchange rates to USD
FX_FALLBACK = {
    "USD": 1.0, "EUR": 1.08, "GBP": 1.27, "CAD": 0.74,
    "AUD": 0.65, "SGD": 0.74, "INR": 0.012,
}


def _cached(key: str):
    entry = _cache.get(key)
    if entry and (time.time() - entry[1]) < CACHE_TTL:
        return entry[0]
    return None


def _store(key: str, value):
    _cache[key] = (value, time.time())
    return value


def get_gdp_per_capita(country: str) -> Optional[float]:
    """Fetch World Bank GDP per capita for a country (USD, latest year)."""
    cache_key = f"gdp_{country}"
    cached = _cached(cache_key)
    if cached:
        return cached

    code = WB_COUNTRY_CODES.get(country)
    if not code:
        return GDP_FALLBACK.get(country)

    try:
        url = f"https://api.worldbank.org/v2/country/{code}/indicator/NY.GDP.PCAP.CD?format=json&mrv=1"
        with httpx.Client(timeout=5.0) as client:
            r = client.get(url)
            r.raise_for_status()
            data = r.json()
            value = data[1][0].get("value") if data and len(data) > 1 and data[1] else None
            if value:
                return _store(cache_key, float(value))
    except Exception:
        pass

    return GDP_FALLBACK.get(country, 50000)


def get_exchange_rate(from_currency: str = "USD", to_currency: str = "INR") -> float:
    """Fetch live exchange rate."""
    cache_key = f"fx_{from_currency}_{to_currency}"
    cached = _cached(cache_key)
    if cached:
        return cached

    try:
        url = f"https://api.exchangerate-api.com/v6/latest/{from_currency}"
        with httpx.Client(timeout=5.0) as client:
            r = client.get(url)
            r.raise_for_status()
            data = r.json()
            rate = data.get("rates", {}).get(to_currency)
            if rate:
                return _store(cache_key, float(rate))
    except Exception:
        pass

    # Fallback: cross-rate via USD
    usd_to_target = FX_FALLBACK.get(to_currency, 1.0)
    usd_from_base = FX_FALLBACK.get(from_currency, 1.0)
    return usd_to_target / usd_from_base


def get_salary_multiplier(country: str) -> float:
    """
    Returns a multiplier (0.8–1.2) based on how the country's
    live GDP deviates from our benchmark assumption.
    Keeps ROI dynamic without needing paid salary APIs.
    """
    gdp = get_gdp_per_capita(country)
    fallback_gdp = GDP_FALLBACK.get(country, 55000)

    if not gdp:
        return 1.0

    ratio = gdp / fallback_gdp
    # Clamp to ±20% adjustment
    return max(0.80, min(1.20, ratio))
