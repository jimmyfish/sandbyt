# Technology Stack

## Architecture

goblin API follows a **modern async Python architecture** with FastAPI as the web framework and direct PostgreSQL access via asyncpg. The application uses a connection pooling pattern for database operations and JWT-based stateless authentication.

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
  - Settings class defines database, JWT, Binance, and Bybit configuration with defaults
- **pydantic**: Core Pydantic library for data validation and serialization
  - Used throughout `app/schemas/` for request/response models
  - Provides `BaseModel`, `EmailStr`, `Field`, `ConfigDict` for schema definition
- **python-dotenv**: Load environment variables from `.env` files
  - Used in `app/core/config.py` via `load_dotenv()` call

### External API Integration
- **httpx**: Async HTTP client for external API calls
  - Used in `app/clients/bybit.py` for Bybit API integration
  - Supports async/await patterns for non-blocking API requests
- **Bybit API**: Market data integration for real-time price queries
  - Supports testnet (`api-testnet.bybit.com`) and mainnet (`api.bybit.com`)
  - Market categories: spot, linear, inverse, option
  - Configured via `BYBIT_BASE_URL` and `BYBIT_TIMEOUT_SECONDS` environment variables

### Data Processing (Optional)
- **pandas**: Data analysis library for DataFrame operations
  - Used in `app/db/database.py` via `records_to_dataframe()` and `query_to_dataframe()` helpers
  - Converts asyncpg.Record objects to pandas DataFrames for analysis
  - Optional dependency - functions raise ImportError if pandas not installed

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
DB_NAME=goblin
DB_USER=postgres
DB_PASSWORD=postgres

# JWT Configuration
JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60

# Binance API Configuration
BINANCE_API_URL=https://api.binance.com
# For testnet, use: BINANCE_API_URL=https://testnet.binance.vision

# Bybit API Configuration
BYBIT_BASE_URL=https://api-testnet.bybit.com
# For mainnet, use: BYBIT_BASE_URL=https://api.bybit.com
BYBIT_TIMEOUT_SECONDS=10.0
```

### Port Configuration

- **API Server**: Port 8000 (default, configurable via uvicorn)
- **PostgreSQL**: Port 5432 (default, configurable via DB_PORT)

## Common Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create database (PostgreSQL)
createdb goblin

# Run database migrations (Flyway)
./scripts/run_migrations.sh
# Or directly:
flyway migrate -configFiles=flyway.conf

# Run development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Run migrations
./scripts/run_migrations.sh

# Check migration status
flyway info -configFiles=flyway.conf

# Validate migrations
flyway validate -configFiles=flyway.conf
```

### API Access

- **API Base URL**: http://localhost:8000
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

## Database Schema

Current tables (managed via Flyway migrations in `db/migration/`):

- **users**: Stores user accounts with balance tracking
  - `id` (SERIAL PRIMARY KEY)
  - `email` (TEXT UNIQUE NOT NULL)
  - `password` (TEXT NOT NULL) - stores bcrypt hash
  - `name` (TEXT NOT NULL)
  - `balance` (DECIMAL(30,20) NOT NULL DEFAULT 0) - user trading balance
  - `created_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))
  - `updated_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))

- **transact**: Stores trading orders/transactions
  - `id` (SERIAL PRIMARY KEY)
  - `symbol` (TEXT NOT NULL) - trading symbol (e.g., "BTCUSDT")
  - `buy_price` (DECIMAL(30,20) NOT NULL)
  - `sell_price` (DECIMAL(30,20)) - NULL until order closed
  - `status` (INTEGER NOT NULL DEFAULT 1) - 1=active, 2=closed
  - `quantity` (DECIMAL(30,20) NOT NULL)
  - `user_id` (INTEGER NOT NULL REFERENCES users(id))
  - `created_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))
  - `updated_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))

- **watchlists**: Stores watchlist entries
  - `id` (SERIAL PRIMARY KEY)
  - `symbol` (TEXT NOT NULL)
  - `created_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))

- **log**: Stores trading logs and analysis data
  - `id` (SERIAL PRIMARY KEY)
  - `symbol` (TEXT NOT NULL)
  - `data` (TEXT NOT NULL) - JSON string storage
  - `action` (TEXT NOT NULL) - action description
  - `created_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))
  - `updated_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))

- **strategies**: Stores trading strategies
  - `id` (SERIAL PRIMARY KEY)
  - `name` (TEXT NOT NULL)
  - `slug` (TEXT NOT NULL) - URL-friendly identifier
  - `deleted_at` (TIMESTAMPTZ) - soft deletion timestamp
  - `created_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))
  - `updated_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))

- **trade_strategies**: Maps symbols to strategies with time intervals
  - `id` (SERIAL PRIMARY KEY)
  - `symbol` (TEXT NOT NULL) - max 15 chars
  - `strategy_id` (INTEGER NOT NULL REFERENCES strategies(id))
  - `timestamp` (TEXT NOT NULL DEFAULT '5m') - time interval
  - `deleted_at` (TIMESTAMPTZ) - soft deletion timestamp
  - `created_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))
  - `updated_at` (TIMESTAMPTZ DEFAULT timezone('utc', now()))

**Note**: Database schema is managed via Flyway migrations in `db/migration/`. The `init_db()` function in `app/db/database.py` only creates the users table as a fallback for backward compatibility. All schema changes should go through Flyway migrations.

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

## Migration History

The project has completed migration from PHP Laravel-based Binance Sandbox to Python FastAPI. Migration specifications in `.claude/specs/initial-migrations/` document the completed work:

- ✅ Bybit API integration for market data (replacing Binance)
- ✅ Extended database schema (transact, watchlists, log, strategies, trade_strategies tables)
- ✅ Order management and balance tracking with atomic transactions
- ✅ Strategy management system with soft deletion
- ✅ Watchlist management
- ✅ Trading log system with JSON data storage
- ✅ Trade strategy mapping (symbols to strategies with time intervals)

All features maintain the asyncpg-based architecture (no ORM) for performance.

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

**Additional Dependencies Used:**
- `httpx` - Async HTTP client for Bybit API integration (imported in `app/clients/bybit.py`)
- `pandas` - Optional dependency for DataFrame conversion helpers (imported conditionally in `app/db/database.py`)
- `decimal` - Standard library for precise decimal arithmetic (used for financial calculations)

**Note**: This documentation reflects dependencies that are actively imported and used in the application code. Other dependencies may be present in `requirements.txt` for future use or as transitive dependencies.

