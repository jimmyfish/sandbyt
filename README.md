# Newsly FastAPI Application

A FastAPI skeleton application with PostgreSQL database connection and health check endpoint.

## Features

- FastAPI web framework
- PostgreSQL database connection using asyncpg
- Health check endpoint (`/health`)
- Authentication endpoints for register/login backed by PostgreSQL
- Database migrations with version tracking and file hash verification
- Environment variable configuration using `.env` file
- Database connection pooling

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

 2. Configure database, JWT, and Binance API settings:
   
   Copy the example environment file and update with your values:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` file with your configuration:
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

 3. Make sure PostgreSQL is running and the database `newsly` exists:
```bash
createdb newsly
```

 4. Run database migrations to set up the schema:
```bash
./scripts/run_migrations.sh
```

Or using Flyway directly:
```bash
flyway migrate -configFiles=flyway.conf
```

This will create all required tables and track applied migrations. Flyway ensures migrations are versioned and immutable - once applied, migration files cannot be modified.

## Running the Application

Start the development server (module path updated for new layout):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative API Documentation: http://localhost:8000/redoc

## Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint (checks API and database connectivity)
- `POST /auth/register` - Create a new user account (`email`, `password` ≤72 chars)
- `POST /auth/login` - Authenticate with `email`/`password` JSON body (password ≤72 chars) and receive a bearer JWT plus user info
- `GET /auth/profile` - Return the authenticated user's profile (requires `Authorization: Bearer <token>` header)

Passwords are hashed using `passlib`'s bcrypt implementation before being stored (bcrypt allows up to 72 characters). Database schema is managed through migrations (see Database Migrations section below).

### Response shape

All successful endpoints wrap their payloads in a consistent envelope:

```json
{
  "status": "success",
  "message": "optional string",
  "meta": { "optional": "object" },
  "data": { "endpoint-specific": "payload" }
}
```

`message`, `meta`, and `data` are omitted if they would be empty. Error responses use the same envelope with `"status": "error"` when returned directly from the service (FastAPI's default error bodies are still used for validation/auth failures).

## Database Migrations

This project uses [Flyway](https://flywaydb.org/) for database migrations - a battle-tested, industry-standard migration tool.

### Running Migrations

To apply all pending migrations:
```bash
./scripts/run_migrations.sh
```

Or using Flyway directly:
```bash
flyway migrate -configFiles=flyway.conf
```

### Migration Features

- **Version Tracking**: Migrations are tracked in the `schema_version` table automatically
- **File Checksum Verification**: Flyway validates file checksums to ensure migrations are immutable after being applied
- **Ordered Execution**: Migrations run in version order (V1, V2, V3...)
- **Transaction Safety**: Each migration runs in its own transaction
- **Idempotent**: Already-applied migrations are skipped automatically
- **Validation**: Flyway validates migration files before execution

### Creating New Migrations

1. Create a new SQL file in `db/migration/` following Flyway naming convention:
   ```
   db/migration/V2__add_user_indexes.sql
   ```

2. Write your SQL statements in the file

3. Run migrations: `./scripts/run_migrations.sh`

### Flyway Naming Convention

- **Versioned migrations**: `V{version}__{description}.sql`
  - Example: `V1__initial_schema.sql`, `V2__add_indexes.sql`, `V2_1__fix_constraint.sql`
  - Version can be numbers with dots/underscores (e.g., `V1.1`, `V2_1`)
- **Repeatable migrations**: `R__{description}.sql` (runs every time if changed)
  - Example: `R__update_views.sql`

### Migration Rules

- **Never modify applied migrations**: Once a migration is applied, Flyway stores its checksum. Modifying the file will cause Flyway to fail on validation.
- **Use descriptive names**: Migration files should follow Flyway naming convention with descriptive names
- **Test migrations**: Always test migrations on a development database before applying to production
- **Version numbers**: Use sequential version numbers (V1, V2, V3...) or semantic versions (V1.1, V1.2...)

### Flyway Commands

- **Migrate**: `flyway migrate -configFiles=flyway.conf` - Apply pending migrations
- **Info**: `flyway info -configFiles=flyway.conf` - Show migration status
- **Validate**: `flyway validate -configFiles=flyway.conf` - Validate migration files
- **Baseline**: `flyway baseline -configFiles=flyway.conf` - Baseline existing database

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application and routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Settings management
│   │   └── security.py       # JWT utilities & dependencies
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py       # Database pool + helpers
├── db/
│   └── migration/            # Flyway migration files
│       └── V*.sql            # Versioned migration files (V1__, V2__, etc.)
├── flyway.conf               # Flyway configuration
├── scripts/
│   └── run_migrations.sh     # Migration runner script
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py           # Auth endpoints
│   └── schemas/
│       ├── __init__.py
│       └── user.py           # Pydantic models
├── .env                      # Environment variables (not in git)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── RULES.md                  # Project rules

```
