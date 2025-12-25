from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class WatchlistCreate(BaseModel):
    """Schema for creating a watchlist entry."""
    symbol: str = Field(
        min_length=1,
        max_length=10,
        description="Trading symbol (e.g., BTCUSDT)"
    )


class WatchlistResponse(BaseModel):
    """Schema for watchlist entry response."""
    id: int
    symbol: str
    created_at: datetime

    model_config = ConfigDict(extra="forbid")


class WatchlistListResponse(BaseModel):
    """Schema for watchlist list response with unique symbols."""
    watchlists: List[WatchlistResponse] = Field(
        default_factory=list,
        description="List of watchlist entries"
    )
    unique_symbols: List[str] = Field(
        default_factory=list,
        description="List of unique symbols from all watchlists"
    )

    model_config = ConfigDict(extra="forbid")

