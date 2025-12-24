from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.clients.bybit import BybitUpstreamError, fetch_last_price
from app.schemas.common import StandardResponse
from app.schemas.market import MarketPrice

router = APIRouter(prefix="/market", tags=["Market"])


@router.get(
    "/price",
    response_model=StandardResponse[MarketPrice],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def get_current_symbol_price(
    symbol: str = Query(..., min_length=3, max_length=30, description="Trading symbol, e.g. BTCUSDT"),
    category: Literal["spot", "linear", "inverse", "option"] = Query(
        "spot",
        description="Bybit market category (spot/linear/inverse/option)",
    ),
):
    """Return current symbol price from Bybit (uses BYBIT_BASE_URL)."""
    try:
        ticker = await fetch_last_price(symbol=symbol, category=category)
    except BybitUpstreamError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        ) from e

    return StandardResponse(
        data=MarketPrice(
            symbol=ticker.symbol,
            category=ticker.category,
            price=ticker.last_price,
            upstream_time_ms=ticker.upstream_time_ms,
        )
    )

