from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from app.db.database import create_user, get_user_by_email, user_exists
from app.schemas.user import UserCreate, UserLogin, UserResponse, LoginResponse
from app.schemas.common import StandardResponse
from app.core.security import create_access_token, get_current_user


router = APIRouter(prefix="/auth", tags=["Auth"])
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _serialize_user(record) -> UserResponse:
    """Convert an asyncpg.Record to a UserResponse"""
    return UserResponse.model_validate(
        {
            "id": record["id"],
            "email": record["email"],
            "name": record.get("name", ""),  # Default to empty string if not present (backward compatibility)
            "balance": record.get("balance", Decimal("0")),  # Default to 0 if not present (backward compatibility)
            "created_at": record["created_at"],
        }
    )


@router.post(
    "/register",
    response_model=StandardResponse[UserResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(payload: UserCreate):
    """Create a new user account with hashed password"""
    if await user_exists(payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    password_hash = password_context.hash(payload.password)
    record = await create_user(payload.email, password_hash, payload.name)

    return StandardResponse(data=_serialize_user(record))


@router.post(
    "/login",
    response_model=StandardResponse[LoginResponse],
    response_model_exclude_none=True,
)
async def login_user(payload: UserLogin):
    """Authenticate a user with email and password"""
    record = await get_user_by_email(payload.email)

    if not record or not password_context.verify(payload.password, record["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token({"sub": record["email"]})
    return StandardResponse(
        data=LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=_serialize_user(record),
        )
    )


@router.get(
    "/profile",
    response_model=StandardResponse[UserResponse],
    response_model_exclude_none=True,
)
async def get_profile(current_record=Depends(get_current_user)):
    """Return the authenticated user's profile details"""
    return StandardResponse(data=_serialize_user(current_record))
