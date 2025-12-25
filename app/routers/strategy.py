"""Strategy management router.

This module provides endpoints for managing trading strategies.
All endpoints require authentication via JWT token.

Endpoints:
    GET /strategy - List all strategies (including soft-deleted by default)
    POST /strategy - Create a new strategy
    PUT /strategy/{strategy_id} - Update a strategy
    DELETE /strategy/{strategy_id} - Soft delete a strategy
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user
from app.db.database import (
    create_strategy,
    get_all_strategies,
    get_strategy_by_id,
    soft_delete_strategy,
    update_strategy,
)
from app.schemas.common import StandardResponse
from app.schemas.strategy import (
    StrategyCreate,
    StrategyListResponse,
    StrategyResponse,
    StrategyUpdate,
)

router = APIRouter(prefix="/strategy", tags=["Strategy"])


def _serialize_strategy(record) -> StrategyResponse:
    """Convert an asyncpg.Record to a StrategyResponse."""
    return StrategyResponse.model_validate(
        {
            "id": record["id"],
            "name": record["name"],
            "slug": record["slug"],
            "deleted_at": record["deleted_at"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
        }
    )


@router.get(
    "/",
    response_model=StandardResponse[StrategyListResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def list_strategies(
    include_deleted: bool = Query(
        default=True,
        description="Include soft-deleted strategies in results (default: True)"
    ),
    current_user=Depends(get_current_user),
):
    """List all strategies.
    
    This endpoint returns all strategies, optionally including soft-deleted ones.
    Results are ordered by created_at DESC.
    
    Args:
        include_deleted: If True, include soft-deleted strategies (default: True)
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with StrategyListResponse containing:
        - strategies: List of strategy entries
    """
    strategy_records = await get_all_strategies(include_deleted=include_deleted)
    
    # Serialize strategy records
    strategies = [_serialize_strategy(record) for record in strategy_records]
    
    return StandardResponse(
        data=StrategyListResponse(strategies=strategies)
    )


@router.post(
    "/",
    response_model=StandardResponse[StrategyResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_strategy_entry(
    payload: StrategyCreate,
    current_user=Depends(get_current_user),
):
    """Create a new strategy.
    
    This endpoint creates a new strategy with name and optional slug.
    If slug is not provided, it will be auto-generated from the name.
    
    Args:
        payload: StrategyCreate schema with name and optional slug
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with StrategyResponse containing the created strategy
        
    Raises:
        HTTPException 422: If validation fails (handled by Pydantic)
        HTTPException 500: If database error occurs
    """
    try:
        record = await create_strategy(
            name=payload.name,
            slug=payload.slug
        )
    except Exception as e:
        # Handle database errors (e.g., constraint violations)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create strategy: {str(e)}",
        )
    
    return StandardResponse(data=_serialize_strategy(record))


@router.put(
    "/{strategy_id}",
    response_model=StandardResponse[StrategyResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def update_strategy_entry(
    strategy_id: int,
    payload: StrategyUpdate,
    current_user=Depends(get_current_user),
):
    """Update a strategy.
    
    This endpoint updates a strategy's name and/or slug.
    If name is provided and slug is not, slug will be auto-generated from name.
    
    Args:
        strategy_id: Strategy ID to update
        payload: StrategyUpdate schema with optional name and slug
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with StrategyResponse containing the updated strategy
        
    Raises:
        HTTPException 404: If strategy not found
        HTTPException 422: If validation fails (handled by Pydantic)
        HTTPException 500: If database error occurs
    """
    try:
        record = await update_strategy(
            strategy_id=strategy_id,
            name=payload.name,
            slug=payload.slug
        )
    except ValueError as e:
        # Strategy not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        # Handle other database errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update strategy: {str(e)}",
        )
    
    return StandardResponse(data=_serialize_strategy(record))


@router.delete(
    "/{strategy_id}",
    response_model=StandardResponse[dict],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def delete_strategy_entry(
    strategy_id: int,
    current_user=Depends(get_current_user),
):
    """Soft delete a strategy.
    
    This endpoint soft deletes a strategy by setting the deleted_at timestamp.
    The record is not removed from the database.
    
    Args:
        strategy_id: Strategy ID to soft delete
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with success message
        
    Raises:
        HTTPException 404: If strategy not found
        HTTPException 500: If database error occurs
    """
    try:
        record = await soft_delete_strategy(strategy_id)
    except ValueError as e:
        # Strategy not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        # Handle other database errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete strategy: {str(e)}",
        )
    
    return StandardResponse(
        data={},
        message=f"Strategy '{record['name']}' soft deleted successfully",
    )

