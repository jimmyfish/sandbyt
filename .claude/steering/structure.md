# Project Structure

## Root Directory Organization

```
hola/
├── app/                    # Main application package
├── .claude/                # Claude AI configuration and specs
│   ├── specs/             # Project specifications
│   │   └── initial-migrations/  # Migration requirements and design docs
│   └── steering/          # Steering documents (this directory)
├── db/                    # Database migration files
│   └── migration/         # Flyway migration SQL files
│       └── V*.sql         # Versioned migration files (V1__, V2__, etc.)
├── scripts/               # Utility scripts
│   └── run_migrations.sh  # Flyway migration runner script
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest configuration and fixtures
│   ├── integration/      # Integration tests
│   └── unit/              # Unit tests
├── __pycache__/           # Python bytecode cache
├── CLAUDE.md              # Context retrieval protocol rules (asyncpg/FastAPI)
├── README.md              # Project documentation
├── RULES.md               # Development rules and guidelines
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
├── flyway.conf            # Flyway database migration configuration
├── swagger.yaml           # OpenAPI 3.0.3 specification for API documentation
├── openapi.yaml           # Alternative OpenAPI specification
└── .python-version        # Python version specification (for pyenv/version managers)
```

## Subdirectory Structures

### `app/` - Main Application Package

The core application code organized by concern:

```
app/
├── __init__.py            # Package marker
├── main.py                # FastAPI app instance, lifespan, root routes
├── core/                  # Core application configuration
│   ├── __init__.py
│   ├── config.py         # Settings management (pydantic-settings)
│   ├── constants.py      # Application constants and error messages
│   └── security.py       # JWT utilities and authentication dependencies
├── db/                    # Database layer
│   ├── __init__.py
│   └── database.py       # Connection pool, database helpers, DataFrame conversion
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── auth.py           # Authentication endpoints (register, login, profile)
│   ├── users.py          # User profile endpoints
│   ├── market.py         # Market data endpoints (Bybit price queries)
│   ├── order.py          # Order management endpoints (buy/sell)
│   ├── watchlist.py      # Watchlist management endpoints
│   ├── log.py            # Trading log endpoints
│   ├── strategy.py       # Strategy management endpoints
│   └── trade_strategy.py # Trade strategy mapping endpoints
├── schemas/               # Pydantic models for request/response validation
│   ├── __init__.py
│   ├── common.py         # StandardResponse generic envelope
│   ├── user.py           # User-related schemas
│   ├── market.py         # Market data schemas
│   ├── order.py          # Order and transaction schemas
│   ├── watchlist.py      # Watchlist schemas
│   ├── log.py            # Log schemas
│   ├── strategy.py       # Strategy schemas
│   └── trade_strategy.py # Trade strategy schemas
├── clients/               # External API clients
│   ├── __init__.py
│   └── bybit.py          # Bybit API client for market data
└── services/              # Business logic services
    ├── __init__.py
    └── binance.py         # Binance service (legacy/placeholder)
```

## Code Organization Patterns

### Separation of Concerns

- **`core/`**: Application-wide configuration, security utilities, and constants
- **`db/`**: Database connection management, data access functions, and DataFrame helpers
- **`routers/`**: HTTP endpoint handlers organized by feature domain
- **`schemas/`**: Data validation and serialization models (Pydantic)
- **`clients/`**: External API client implementations (Bybit, etc.)
- **`services/`**: Business logic services and integrations

### Dependency Flow

```
main.py
  ├── routers/auth.py
  │     ├── db/database.py (user CRUD)
  │     ├── schemas/user.py (request/response models)
  │     └── core/security.py (JWT, auth dependencies)
  ├── routers/order.py
  │     ├── db/database.py (transaction CRUD, atomic operations)
  │     ├── schemas/order.py (order request/response models)
  │     ├── services/binance.py (price fetching)
  │     └── core/security.py (authentication)
  ├── routers/market.py
  │     ├── clients/bybit.py (Bybit API client)
  │     └── schemas/market.py (market data models)
  ├── routers/watchlist.py
  │     ├── db/database.py (watchlist CRUD)
  │     └── schemas/watchlist.py (watchlist models)
  ├── routers/strategy.py
  │     ├── db/database.py (strategy CRUD)
  │     └── schemas/strategy.py (strategy models)
  ├── routers/trade_strategy.py
  │     ├── db/database.py (trade strategy CRUD)
  │     └── schemas/trade_strategy.py (trade strategy models)
  ├── routers/log.py
  │     ├── db/database.py (log CRUD)
  │     └── schemas/log.py (log models)
  └── db/database.py
        └── core/config.py (settings)
```

### Router Pattern

Routers are defined in `app/routers/` and mounted in `main.py`:
- Each router uses `APIRouter` with a prefix (e.g., `/auth`, `/order`)
- Routers are tagged for API documentation grouping (e.g., `tags=["Auth"]`, `tags=["Orders"]`)
- Dependencies are injected via FastAPI's `Depends()`
- Protected endpoints use `Depends(get_current_user)` for authentication
- Current routers:
  - `auth.py` - Authentication (register, login, profile)
  - `users.py` - User profile endpoints
  - `market.py` - Market data (Bybit price queries)
  - `order.py` - Order management (buy/sell, list transactions)
  - `watchlist.py` - Watchlist management (CRUD operations)
  - `log.py` - Trading logs (create, list, symbol discovery)
  - `strategy.py` - Strategy management (CRUD with soft deletion)
  - `trade_strategy.py` - Trade strategy mapping (CRUD with soft deletion)

### Database Access Pattern

Direct SQL functions in `app/db/database.py`:
- Connection pool accessed via `get_db_pool()` (singleton pattern with global `_db_pool`)
- Functions use `async with pool.acquire() as conn:` pattern
- SQL queries use asyncpg's parameterized queries (`$1`, `$2`, etc.)
- No ORM layer - direct asyncpg.Record objects returned
- Pool configuration: min_size=5, max_size=20, command_timeout=60, max_queries=50000
- Atomic transactions: Use `async with conn.transaction():` for multi-step operations
- DataFrame helpers: `records_to_dataframe()` and `query_to_dataframe()` for pandas integration
- Database functions organized by domain:
  - User operations: `create_user()`, `get_user_by_email()`, `update_user_balance()`, etc.
  - Transaction operations: `create_order_atomic()`, `close_order_atomic()`, `get_user_transactions()`, etc.
  - Watchlist operations: `create_watchlist()`, `get_watchlists()`, `delete_watchlist()`
  - Log operations: `create_log()`, `get_logs()`, `get_unique_log_symbols()`
  - Strategy operations: `create_strategy()`, `get_all_strategies()`, `update_strategy()`, `soft_delete_strategy()`
  - Trade strategy operations: `create_trade_strategy()`, `get_trade_strategies()`, `update_trade_strategy()`, `soft_delete_trade_strategy()`

### Client Pattern

External API clients in `app/clients/`:
- **`bybit.py`**: Bybit API client for market data
  - Uses `httpx.AsyncClient` for async HTTP requests
  - Provides `fetch_last_price()` function
  - Handles errors with custom exceptions (`BybitUpstreamError`)
  - Returns structured data via `BybitTickerPrice` dataclass
  - Configured via `BYBIT_BASE_URL` and `BYBIT_TIMEOUT_SECONDS` settings

### Service Pattern

Business logic services in `app/services/`:
- **`binance.py`**: Binance service (legacy/placeholder)
  - Currently used for price fetching in order router
  - May be replaced or extended for future Binance integration

### Schema Organization

Pydantic models organized by domain:
- **`common.py`**: Shared response envelope (`StandardResponse[DataT]`) with Generic type support
- **`user.py`**: User-related request/response models (UserCreate, UserLogin, UserResponse, LoginResponse, TokenResponse)
- **`market.py`**: Market data models (MarketPrice)
- **`order.py`**: Order and transaction models (OrderCreate, OrderClose, OrderListResponse, TransactionResponse)
- **`watchlist.py`**: Watchlist models (WatchlistCreate, WatchlistResponse, WatchlistListResponse)
- **`log.py`**: Log models (LogCreate, LogResponse, LogListResponse)
- **`strategy.py`**: Strategy models (StrategyCreate, StrategyUpdate, StrategyResponse, StrategyListResponse)
- **`trade_strategy.py`**: Trade strategy models (TradeStrategyCreate, TradeStrategyUpdate, TradeStrategyResponse, TradeStrategyListResponse)
- All schemas use Pydantic v2 features (model_validate, model_dump, ConfigDict)
- Response models use `response_model_exclude_none=True` to omit None values

## File Naming Conventions

- **Python files**: `snake_case.py`
- **Directories**: `snake_case/`
- **Router files**: Match the feature domain (e.g., `auth.py`, `order.py`, `trade_strategy.py`)
- **Schema files**: Match the domain entity (e.g., `user.py`, `order.py`, `strategy.py`)
- **Database helpers**: Descriptive function names with domain prefix (e.g., `get_user_by_email`, `create_order_atomic`, `get_all_strategies`)
- **Client files**: Match the external service (e.g., `bybit.py`)
- **Service files**: Match the business domain (e.g., `binance.py`)

## Import Organization

Imports follow this pattern:

1. Standard library imports
2. Third-party imports (FastAPI, asyncpg, etc.)
3. Local application imports (from `app.*`)

Example from `app/routers/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from app.db.database import create_user, get_user_by_email, user_exists
from app.schemas.user import UserCreate, UserLogin, UserResponse, LoginResponse
from app.schemas.common import StandardResponse
from app.core.security import create_access_token, get_current_user
```

### Database Migration Structure

Flyway migrations in `db/migration/`:
- **Naming Convention**: `V{version}__{description}.sql`
  - Example: `V1__initial_schema.sql`
  - Version can be numbers with dots/underscores (e.g., `V1.1`, `V2_1`)
- **Versioned Migrations**: Run once in order, tracked in `schema_version` table
- **Repeatable Migrations**: `R__{description}.sql` (runs every time if changed)
- **Immutable**: Once applied, migration files cannot be modified (Flyway validates checksums)
- **Configuration**: `flyway.conf` defines database connection and migration location
- **Execution**: Run via `./scripts/run_migrations.sh` or `flyway migrate -configFiles=flyway.conf`

## Key Architectural Principles

### 1. Async-First Design
- All I/O operations use `async/await`
- Database operations are fully async via asyncpg
- FastAPI endpoints are async functions

### 2. Type Safety
- Type hints required for all public functions
- Pydantic models for request/response validation
- Generic types used for response envelopes (`StandardResponse[DataT]`)

### 3. Configuration Management
- All settings via `pydantic-settings` from environment variables
- No hardcoded configuration values (defaults provided but overridden by env vars)
- Settings accessed through `app.core.config.settings` singleton
- `.env` file loaded via `python-dotenv` for local development

### 4. Security by Default
- Passwords never logged or returned
- JWT tokens validated on every protected endpoint
- Generic error messages to prevent information leakage

### 5. Standardized Responses
- All endpoints use `StandardResponse` envelope
- Consistent error handling via HTTPException
- Optional fields excluded from responses when None

### 6. Database Initialization & Migrations
- Database schema managed via Flyway migrations in `db/migration/` directory
- Migrations use versioned naming: `V{version}__{description}.sql` (e.g., `V1__initial_schema.sql`)
- Flyway tracks applied migrations in `schema_version` table with checksum verification
- Connection pool initialized during application lifespan (via `get_db_pool()` in lifespan)
- Graceful shutdown closes connection pool (via `close_db_pool()` in lifespan)
- `init_db()` function only creates users table as backward-compatibility fallback
- All schema changes must go through Flyway migrations (see RULES.md)

### 7. Modular Router Design
- Feature-based router organization
- Routers mounted in `main.py` for discoverability
- Tags used for API documentation grouping

## Extension Points

When adding new features:

1. **New Domain Entity**: 
   - Create schema in `app/schemas/`
   - Add database helpers in `app/db/database.py`
   - Create Flyway migration in `db/migration/` for schema changes

2. **New API Endpoints**: 
   - Create router in `app/routers/`
   - Mount in `main.py` with `app.include_router()`
   - Use `Depends(get_current_user)` for protected endpoints

3. **New Configuration**: 
   - Add to `app/core/config.py` Settings class
   - Document in README.md and tech.md
   - Add to `.env.example` if created

4. **New Database Tables**: 
   - Create Flyway migration file in `db/migration/`
   - Follow naming convention: `V{version}__{description}.sql`
   - Never modify applied migrations (Flyway validates checksums)

5. **External API Integration**: 
   - Create client in `app/clients/` for API communication
   - Use `httpx.AsyncClient` for async HTTP requests
   - Add configuration to `app/core/config.py`

6. **Business Logic Services**: 
   - Create service in `app/services/` for complex business logic
   - Services can use clients and database helpers

7. **Update API Documentation**: 
   - Update `swagger.yaml` to reflect new endpoints and schemas
   - FastAPI auto-generates docs from Pydantic schemas

8. **Constants**: 
   - Add application constants to `app/core/constants.py`
   - Use constants for error messages and status strings

## Project Specifications

The `.claude/specs/` directory contains detailed specifications for completed and planned features:

- **`initial-migrations/`**: Contains requirements, design, and task documentation for the completed migration from PHP Binance Sandbox to Python FastAPI
  - `requirements.md`: Detailed feature requirements and acceptance criteria
  - `design.md`: Design documentation for the migration
  - `migration-todo.md`: Migration task tracking (completed)
  - `tasks.md`: Task breakdown (completed)

These specs follow spec-driven development principles and document the completed migration work. They serve as reference for understanding the architecture decisions and feature implementations.

## API Documentation Files

- **`swagger.yaml`**: OpenAPI 3.0.3 specification file defining the complete API schema
  - Includes all endpoints, request/response models, and security schemes
  - Manually maintained to ensure consistency with FastAPI implementation
  - Should be updated when adding new endpoints or modifying schemas

