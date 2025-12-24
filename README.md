# Newsly FastAPI Application

A FastAPI skeleton application with PostgreSQL database connection and health check endpoint.

## Features

- FastAPI web framework
- PostgreSQL database connection using asyncpg
- Health check endpoint (`/health`)
- Authentication endpoints for register/login backed by PostgreSQL
- Automatic creation of `users` table on startup
- Environment variable configuration using `.env` file
- Database connection pooling

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

 2. Configure database and JWT settings in `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=newsly
DB_USER=postgres
DB_PASSWORD=postgres
JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60
```

 3. Make sure PostgreSQL is running and the database `newsly` exists:
```bash
createdb newsly
```

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
- `GET /market/price` - Return the current symbol price from Bybit (public endpoint)

Passwords are hashed using `passlib`'s bcrypt implementation before being stored (bcrypt allows up to 72 characters). The `users` table is created automatically on startup if it does not exist.

## Bybit sandbox (testnet) configuration

This project can query **Bybit market data** from either:

- **Sandbox/testnet**: `api-testnet.bybit.com`
- **Mainnet**: `api.bybit.com`

Environment variables (in `.env`):

```env
# Bybit integration
BYBIT_SANDBOX=true
BYBIT_TIMEOUT_SECONDS=10
# Optional override (useful behind proxies / restricted networks)
# BYBIT_BASE_URL_OVERRIDE=https://api-testnet.bybit.com
```

Example:

```bash
curl "http://localhost:8000/market/price?symbol=BTCUSDT&category=spot"
```

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
