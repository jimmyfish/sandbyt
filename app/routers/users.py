from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.common import StandardResponse
from app.schemas.user import UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


def _serialize_user(record) -> UserResponse:
    """Convert an asyncpg.Record to a UserResponse"""
    # Let UserResponse handle Decimal->string formatting for `balance`.
    return UserResponse.model_validate(
        {
            "id": record["id"],
            "email": record["email"],
            "name": record["name"],
            "balance": record["balance"],
            "created_at": record["created_at"],
        }
    )


@router.get(
    "/me",
    response_model=StandardResponse[UserResponse],
    response_model_exclude_none=True,
)
async def get_me(current_record=Depends(get_current_user)) -> StandardResponse[UserResponse]:
    """Return the authenticated user's profile details"""
    return StandardResponse(data=_serialize_user(current_record))

