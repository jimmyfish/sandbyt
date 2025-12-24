from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import httpx

from app.core.config import settings


class BybitUpstreamError(RuntimeError):
    """Raised when the Bybit upstream response is invalid or indicates failure."""


@dataclass(frozen=True)
class BybitTickerPrice:
    symbol: str
    category: str
    last_price: Decimal
    upstream_time_ms: Optional[int] = None


def _parse_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError) as e:
        raise BybitUpstreamError(f"Invalid decimal value from Bybit: {value!r}") from e


def _parse_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


async def fetch_last_price(*, symbol: str, category: str = "spot") -> BybitTickerPrice:
    """
    Fetch current ticker last price from Bybit v5 market tickers endpoint.

    Uses sandbox/mainnet base URL depending on settings.BYBIT_SANDBOX.
    """
    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        raise BybitUpstreamError("Symbol is empty")

    url = f"{settings.BYBIT_BASE_URL}/v5/market/tickers"
    params = {"category": category, "symbol": normalized_symbol}
    headers = {
        "Accept": "application/json",
        "User-Agent": "newsly/1.0",
    }

    timeout = httpx.Timeout(settings.BYBIT_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url, params=params, headers=headers)

    if resp.status_code != 200:
        detail = resp.text.strip().replace("\n", " ")[:240]
        msg = f"Bybit returned HTTP {resp.status_code}"
        if detail:
            msg = f"{msg}: {detail}"
        raise BybitUpstreamError(msg)

    try:
        payload = resp.json()
    except ValueError as e:
        raise BybitUpstreamError("Bybit returned invalid JSON") from e

    if payload.get("retCode") != 0:
        raise BybitUpstreamError(payload.get("retMsg") or "Bybit returned non-zero retCode")

    result = payload.get("result") or {}
    items = result.get("list") or []
    if not items:
        raise BybitUpstreamError("No ticker data returned for symbol/category")

    ticker = items[0] or {}
    last_price = _parse_decimal(ticker.get("lastPrice"))
    upstream_time_ms = _parse_int(result.get("time"))

    return BybitTickerPrice(
        symbol=normalized_symbol,
        category=category,
        last_price=last_price,
        upstream_time_ms=upstream_time_ms,
    )

