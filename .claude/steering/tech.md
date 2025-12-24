# Technology Stack

## Architecture

Newsly API follows a **modern async Python architecture** with FastAPI as the web framework and direct PostgreSQL access via asyncpg. The application uses a connection pooling pattern for database operations and JWT-based stateless authentication.

## Backend

### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs with automatic OpenAPI documentation
  - Used in `app/main.py` to create the application instance
  - Routers defined in `app/routers/auth.py` using `APIRouter`
  - Dependency injection via `Depends()` for authentication
  - Response models use `response_model_exclude_none=True` to omit None values
- **Python 3.10+**: Required for modern async/await patterns and type hints (see `.python-version` for exact version)

### Database
- **PostgreSQL**: Relational database for persistent data storage
- **asyncpg**: **Primary and only database access method** - High-performance async PostgreSQL driver using direct SQL queries (no ORM)
  - Imported in `app/db/database.py`
  - Connection pooling configured with min_size=5, max_size=20 connections
  - Uses parameterized queries (`$1`, `$2`, etc.) for SQL injection prevention
- **No ORM Layer**: The application uses asyncpg directly for all database operations - no SQLAlchemy or other ORM

### Authentication & Security
- **PyJWT** (imported as `jwt`): JWT token creation and validation
  - Used in `app/core/security.py` for `create_access_token()` and token decoding
  - Handles token expiration and validation errors
- **passlib**: Password hashing with bcrypt (supports up to 72 character passwords)
  - Used in `app/routers/auth.py` via `CryptContext(schemes=["bcrypt"])`
  - Provides `hash()` and `verify()` methods for password operations
- **email-validator**: Email format validation
  - Used implicitly via Pydantic's `EmailStr` type in `app/schemas/user.py`

### Configuration & Settings
- **pydantic-settings**: Type-safe configuration management from environment variables
  - Used in `app/core/config.py` via `BaseSettings` class
  - Settings class defines database and JWT configuration with defaults
- **pydantic**: Core Pydantic library for data validation and serialization
  - Used throughout `app/schemas/` for request/response models
  - Provides `BaseModel`, `EmailStr`, `Field`, `ConfigDict` for schema definition
- **python-dotenv**: Load environment variables from `.env` files
  - Used in `app/core/config.py` via `load_dotenv()` call

### Server
- **uvicorn**: ASGI server for running FastAPI application
  - Not imported in code (used as command-line tool)
  - Standard extras include httptools, uvloop, watchfiles for performance

## Development Environment

### Required Tools
- Python 3.10 or higher
- PostgreSQL database server
- pip (Python package manager)

### Environment Variables

Key configuration variables (set in `.env` file):

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=newsly
DB_USER=postgres
DB_PASSWORD=postgres

# JWT Configuration
JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60

# Binance API Configuration
BINANCE_API_URL=https://api.binance.com
# For testnet, use: BINANCE_API_URL=https://testnet.binance.vision
```

### Port Configuration

- **API Server**: Port 8000 (default, configurable via uvicorn)
- **PostgreSQL**: Port 5432 (default, configurable via DB_PORT)

## Common Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Create database (PostgreSQL)
createdb newsly
```

### API Access

- **API Base URL**: http://localhost:8000
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

## Database Schema

Current tables:

- **users**: Stores user accounts
  - `id` (SERIAL PRIMARY KEY)
  - `email` (TEXT UNIQUE NOT NULL)
  - `password` (TEXT NOT NULL) - stores bcrypt hash
  - `created_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))

Tables are automatically created on application startup via `init_db()` function.

## Important Technical Notes

### Database Access Pattern

The application uses **direct SQL queries with asyncpg** rather than an ORM. This provides:
- Full control over SQL queries
- High performance with async operations
- Direct PostgreSQL feature access

**Note**: The project uses **asyncpg exclusively** for database access. The migration specs in `.claude/specs/initial-migrations/` confirm continued use of asyncpg (no ORM) for performance reasons. `CLAUDE.md` has been updated to reflect the asyncpg + FastAPI architecture.

### Connection Pool Management

Database connections are managed through a global connection pool:
- Created on first access via `get_db_pool()`
- Initialized during application startup (lifespan)
- Closed gracefully on application shutdown

### Authentication Flow

1. User registers → password hashed with bcrypt → stored in database
2. User logs in → password verified → JWT token generated and returned
3. Protected endpoints → JWT validated → user record fetched from database

### Response Envelope

All endpoints wrap responses in `StandardResponse[DataT]` generic type for consistent API structure.

## API Documentation

- **OpenAPI Specification**: `swagger.yaml` (OpenAPI 3.0.3) defines complete API schema
- **Auto-generated Docs**: FastAPI automatically generates Swagger UI (`/docs`) and ReDoc (`/redoc`)
- **Schema Sync**: Pydantic models in `app/schemas/` are automatically reflected in OpenAPI spec

## Planned Extensions

The project has migration specifications in `.claude/specs/initial-migrations/` that outline:
- Binance API integration for trading sandbox
- Extended database schema (transact, watchlists, log, strategies, trade_strategies tables)
- Order management and balance tracking
- Strategy management system

These extensions will maintain the asyncpg-based architecture (no ORM) for performance.

## Dependencies Actually Used in Codebase

Based on actual imports in the codebase, the following dependencies are actively used:

**Core Framework:**
- `fastapi` - Web framework (imported in main.py, routers/auth.py, core/security.py)
- `asyncpg` - Database driver (imported in db/database.py)
- `pydantic` - Data validation (imported in schemas/common.py, schemas/user.py)
- `pydantic-settings` - Configuration management (imported in core/config.py)
- `python-dotenv` - Environment variable loading (imported in core/config.py)

**Authentication:**
- `PyJWT` (imported as `jwt`) - JWT operations (imported in core/security.py)
- `passlib` - Password hashing (imported in routers/auth.py)
- `email-validator` - Email validation (used via Pydantic's EmailStr)

**Standard Library:**
- `contextlib.asynccontextmanager` - Application lifespan management (used in main.py)
- `datetime`, `typing` - Type hints and date handling (used throughout)
- `fastapi.responses.JSONResponse` - Error response formatting (used in main.py)

**Note**: This documentation reflects only dependencies that are actually imported and used in the application code. Other dependencies may be present in `requirements.txt` but are not currently integrated into the codebase.

