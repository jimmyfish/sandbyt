from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MarketPrice(BaseModel):
    symbol: str
    category: str
    price: Decimal
    upstream_time_ms: Optional[int] = None

    model_config = ConfigDict(extra="forbid")

