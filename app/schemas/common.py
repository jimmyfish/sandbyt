from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class StandardResponse(BaseModel, Generic[DataT]):
    """Generic envelope for API responses."""

    status: str = "success"
    message: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    data: Optional[DataT] = None

    model_config = ConfigDict(extra="forbid")
