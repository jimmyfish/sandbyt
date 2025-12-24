# Project Structure

## Root Directory Organization

```
hola/
├── app/                    # Main application package
├── .claude/                # Claude AI configuration and specs
│   ├── specs/             # Project specifications
│   │   └── initial-migrations/  # Migration requirements and design docs
│   └── steering/          # Steering documents (this directory)
├── scripts/               # Utility scripts
├── __pycache__/           # Python bytecode cache
├── CLAUDE.md              # Context retrieval protocol rules (asyncpg/FastAPI)
├── README.md              # Project documentation
├── RULES.md               # Development rules and guidelines
├── requirements.txt       # Python dependencies
├── swagger.yaml           # OpenAPI 3.0.3 specification for API documentation
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
│   └── security.py       # JWT utilities and authentication dependencies
├── db/                    # Database layer
│   ├── __init__.py
│   └── database.py       # Connection pool, init_db, user CRUD helpers
├── routers/               # API route handlers
│   ├── __init__.py
│   └── auth.py           # Authentication endpoints (register, login, profile)
└── schemas/               # Pydantic models for request/response validation
    ├── __init__.py
    ├── common.py         # StandardResponse generic envelope
    └── user.py           # User-related schemas (UserCreate, UserLogin, UserResponse, etc.)
```

## Code Organization Patterns

### Separation of Concerns

- **`core/`**: Application-wide configuration and security utilities
- **`db/`**: Database connection management and data access functions
- **`routers/`**: HTTP endpoint handlers organized by feature domain
- **`schemas/`**: Data validation and serialization models

### Dependency Flow

```
main.py
  ├── routers/auth.py
  │     ├── db/database.py (user CRUD)
  │     ├── schemas/user.py (request/response models)
  │     └── core/security.py (JWT, auth dependencies)
  └── db/database.py
        └── core/config.py (settings)
```

### Router Pattern

Routers are defined in `app/routers/` and mounted in `main.py`:
- Each router uses `APIRouter` with a prefix (e.g., `/auth`)
- Routers are tagged for API documentation grouping (e.g., `tags=["Auth"]`)
- Dependencies are injected via FastAPI's `Depends()`
- Current routers: `auth.py` (register, login, profile endpoints)

### Database Access Pattern

Direct SQL functions in `app/db/database.py`:
- Connection pool accessed via `get_db_pool()` (singleton pattern with global `_db_pool`)
- Functions use `async with pool.acquire() as conn:` pattern
- SQL queries use asyncpg's parameterized queries (`$1`, `$2`, etc.)
- No ORM layer - direct asyncpg.Record objects returned
- Pool configuration: min_size=5, max_size=20, command_timeout=60, max_queries=50000

### Schema Organization

Pydantic models organized by domain:
- **`common.py`**: Shared response envelope (`StandardResponse[DataT]`) with Generic type support
- **`user.py`**: User-related request/response models (UserCreate, UserLogin, UserResponse, LoginResponse, TokenResponse)
- All schemas use Pydantic v2 features (model_validate, model_dump, ConfigDict)
- Response models use `response_model_exclude_none=True` to omit None values

## File Naming Conventions

- **Python files**: `snake_case.py`
- **Directories**: `snake_case/`
- **Router files**: Match the feature domain (e.g., `auth.py`)
- **Schema files**: Match the domain entity (e.g., `user.py`)
- **Database helpers**: Descriptive function names (e.g., `get_user_by_email`, `create_user`)

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

### 6. Database Initialization
- Tables created automatically on startup via `init_db()` (called in lifespan startup)
- Connection pool initialized during application lifespan (via `get_db_pool()` in lifespan)
- Graceful shutdown closes connection pool (via `close_db_pool()` in lifespan)
- Uses `CREATE TABLE IF NOT EXISTS` to avoid errors on restart

### 7. Modular Router Design
- Feature-based router organization
- Routers mounted in `main.py` for discoverability
- Tags used for API documentation grouping

## Extension Points

When adding new features:

1. **New Domain Entity**: Create schema in `app/schemas/`, add database helpers in `app/db/database.py`
2. **New API Endpoints**: Create router in `app/routers/`, mount in `main.py` with `app.include_router()`
3. **New Configuration**: Add to `app/core/config.py` Settings class, document in README and tech.md
4. **New Database Tables**: Add CREATE TABLE to `init_db()` function in `app/db/database.py`
5. **Update API Documentation**: Update `swagger.yaml` to reflect new endpoints and schemas
6. **Authentication**: Use `get_current_user` dependency from `app.core.security` for protected endpoints

## Project Specifications

The `.claude/specs/` directory contains detailed specifications for planned features:

- **`initial-migrations/`**: Contains requirements, design, and task documentation for migrating PHP Binance Sandbox features to Python FastAPI
  - `requirements.md`: Detailed feature requirements and acceptance criteria
  - `design.md`: Design documentation (to be created)
  - `migration-todo.md`: Migration task tracking
  - `tasks.md`: Task breakdown

These specs follow spec-driven development principles and should be referenced when implementing new features.

## API Documentation Files

- **`swagger.yaml`**: OpenAPI 3.0.3 specification file defining the complete API schema
  - Includes all endpoints, request/response models, and security schemes
  - Manually maintained to ensure consistency with FastAPI implementation
  - Should be updated when adding new endpoints or modifying schemas

