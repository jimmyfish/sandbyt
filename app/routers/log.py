"""Log management router.

This module provides endpoints for managing trading log entries.
All endpoints require authentication via JWT token.

Endpoints:
    GET /log - List log entries with optional filtering and pagination
    POST /log - Create a log entry
"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.constants import SUCCESS_LOG_CREATED
from app.core.security import get_current_user
from app.db.database import create_log, get_logs, get_unique_log_symbols
from app.schemas.common import StandardResponse
from app.schemas.log import LogCreate, LogListResponse, LogResponse

router = APIRouter(prefix="/log", tags=["Log"])


def _serialize_log(record) -> LogResponse:
    """Convert an asyncpg.Record to a LogResponse.
    
    The data field is stored as JSON text in the database, so we need to parse it.
    """
    return LogResponse.model_validate(
        {
            "id": record["id"],
            "symbol": record["symbol"],
            "data": record["data"],  # Will be parsed by LogResponse field_validator
            "action": record["action"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
        }
    )


@router.post(
    "/",
    response_model=StandardResponse[LogResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_log_entry(
    payload: LogCreate,
    current_user=Depends(get_current_user),
):
    """Create a new log entry.
    
    This endpoint creates a new log entry with symbol, data (as JSON), and action.
    The data field is stored as JSON text in the database.
    
    Args:
        payload: LogCreate schema with symbol, data (dict), and action
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with LogResponse containing the created log entry
        
    Raises:
        HTTPException 422: If validation fails (handled by Pydantic)
        HTTPException 500: If database error occurs
    """
    symbol = payload.symbol.upper()
    
    try:
        record = await create_log(
            symbol=symbol,
            data=payload.data,
            action=payload.action
        )
    except Exception as e:
        # Handle database errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create log entry: {str(e)}",
        )
    
    return StandardResponse(
        data=_serialize_log(record),
        message=SUCCESS_LOG_CREATED
    )


@router.get(
    "/",
    response_model=StandardResponse[LogListResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def list_logs(
    symbol: str | None = Query(
        default=None,
        description="Filter logs by symbol (LIKE search, e.g., 'BTC' matches 'BTCUSDT')"
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records per page (1-1000)"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip for pagination"
    ),
    current_user=Depends(get_current_user),
):
    """List log entries with optional filtering and pagination.
    
    This endpoint returns log entries ordered by created_at DESC.
    Supports filtering by symbol (LIKE search) and pagination.
    
    Args:
        symbol: Optional symbol filter (LIKE search, e.g., "BTC" matches "BTCUSDT")
        limit: Maximum number of records per page (default: 100, max: 1000)
        offset: Number of records to skip for pagination (default: 0)
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with LogListResponse containing:
        - logs: List of log entries
        - unique_symbols: List of unique symbols from all logs
        - total_count: Total number of matching records (for pagination)
        - limit: Maximum number of records per page
        - offset: Number of records skipped
    """
    # Fetch logs with filters and pagination
    log_records, total_count = await get_logs(
        symbol=symbol,
        limit=limit,
        offset=offset
    )
    
    # Serialize log records (data field will be parsed by LogResponse)
    logs = [_serialize_log(record) for record in log_records]
    
    # Get unique symbols from all logs (not just filtered results)
    unique_symbols = await get_unique_log_symbols()
    
    return StandardResponse(
        data=LogListResponse(
            logs=logs,
            unique_symbols=unique_symbols,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )
    )

