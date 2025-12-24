from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.db.database import get_db_pool, close_db_pool, init_db
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.schemas.common import StandardResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events"""
    await get_db_pool()
    await init_db()
    yield
    await close_db_pool()


app = FastAPI(
    title="Newsly API",
    description="A FastAPI application with PostgreSQL connection",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/", response_model=StandardResponse[dict], response_model_exclude_none=True)
async def root():
    """Root endpoint"""
    return StandardResponse(message="Welcome to Newsly API")


@app.get("/health", response_model=StandardResponse[dict], response_model_exclude_none=True)
async def health_check():
    """Health check endpoint to verify API and database connectivity"""
    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                return StandardResponse(
                    data={
                        "status": "healthy",
                        "database": "connected",
                        "message": "API and database are operational",
                    }
                )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content=StandardResponse(
                status="error",
                message="API or database dependency is unavailable",
                data={"error": str(e)},
            ).model_dump(exclude_none=True),
        )
