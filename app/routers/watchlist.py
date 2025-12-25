"""Watchlist management router.

This module provides endpoints for managing watchlist entries.
All endpoints require authentication via JWT token.

Endpoints:
    GET /watchlist - List all watchlist entries
    POST /watchlist - Create a watchlist entry
    DELETE /watchlist/{symbol} - Delete a watchlist entry by symbol
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.db.database import create_watchlist, delete_watchlist, get_watchlists
from app.schemas.common import StandardResponse
from app.schemas.watchlist import WatchlistCreate, WatchlistListResponse, WatchlistResponse

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


def _serialize_watchlist(record) -> WatchlistResponse:
    """Convert an asyncpg.Record to a WatchlistResponse."""
    return WatchlistResponse.model_validate(
        {
            "id": record["id"],
            "symbol": record["symbol"],
            "created_at": record["created_at"],
        }
    )


@router.get(
    "/",
    response_model=StandardResponse[WatchlistListResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def list_watchlists(
    current_user=Depends(get_current_user),
):
    """List all watchlist entries.
    
    This endpoint returns all watchlist entries with their unique symbols.
    
    Args:
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with WatchlistListResponse containing:
        - watchlists: List of watchlist entries
        - unique_symbols: List of unique symbols from all watchlists
    """
    watchlist_records = await get_watchlists()
    
    # Serialize watchlist records
    watchlists = [_serialize_watchlist(record) for record in watchlist_records]
    
    # Extract unique symbols
    unique_symbols = sorted(list(set(record["symbol"] for record in watchlist_records)))
    
    return StandardResponse(
        data=WatchlistListResponse(
            watchlists=watchlists,
            unique_symbols=unique_symbols,
        )
    )


@router.post(
    "/",
    response_model=StandardResponse[WatchlistResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_watchlist_entry(
    payload: WatchlistCreate,
    current_user=Depends(get_current_user),
):
    """Create a new watchlist entry.
    
    This endpoint creates a new watchlist entry for the specified symbol.
    The symbol is validated to be max 10 characters (enforced by Pydantic).
    
    Args:
        payload: WatchlistCreate schema with symbol
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with WatchlistResponse containing the created watchlist entry
        
    Raises:
        HTTPException 422: If symbol validation fails (handled by Pydantic)
        HTTPException 500: If database error occurs
    """
    symbol = payload.symbol.upper()
    
    try:
        record = await create_watchlist(symbol)
    except Exception as e:
        # Handle database errors (e.g., constraint violations)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create watchlist entry: {str(e)}",
        )
    
    return StandardResponse(data=_serialize_watchlist(record))


@router.delete(
    "/{symbol}",
    response_model=StandardResponse[dict],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def delete_watchlist_entry(
    symbol: str,
    current_user=Depends(get_current_user),
):
    """Delete a watchlist entry by symbol.
    
    This endpoint deletes a watchlist entry for the specified symbol.
    
    Args:
        symbol: Trading symbol to remove from watchlist (max 10 chars, validated by path parameter)
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with success message
        
    Raises:
        HTTPException 400: If symbol exceeds max length
        HTTPException 404: If symbol not found in watchlist
        HTTPException 500: If database error occurs
    """
    # Validate symbol length (max 10 characters)
    if len(symbol) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symbol must be 10 characters or less",
        )
    
    symbol = symbol.upper()
    
    # Delete watchlist entry
    deleted = await delete_watchlist(symbol)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Watchlist entry for symbol '{symbol}' not found",
        )
    
    return StandardResponse(
        data={},
        message=f"Watchlist entry for symbol '{symbol}' deleted successfully",
    )

