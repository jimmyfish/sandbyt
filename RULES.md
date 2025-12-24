# Project Rules - Newsly API

These rules define how to build, test, and extend the Newsly FastAPI service. Follow them for every change to keep the codebase consistent and secure.

## 1. General Code Style
- Use modern Python (3.10+) features; prefer async/await for I/O.
- Keep files ASCII unless there is a strong reason not to.
- Type annotations are required for all public functions, FastAPI endpoints, and database helpers.
- Use `black`-style formatting (4-space indent) and run linters/tests before submitting changes.
- Never commit `.env` or secrets—use sample placeholders in docs only.
- Always use Context7 for any code generation, setup/configuration steps, or library/API documentation needs. Automatically resolve library IDs and pull docs via Context7 MCP tools without waiting for manual requests.

## 2. Configuration & Secrets
 - Load configuration exclusively via `pydantic-settings` (`app/core/config.py`). Do not fetch from `os.getenv` inside business logic.
- Add new settings to `.env.example` (if created later) and document them in `README.md`.
- Database name remains `newsly`. Never hardcode credentials in source files.

## 3. Dependencies
- Pin new libraries in `requirements.txt` with a minimum version. Keep optional extras explicit (e.g., `passlib[bcrypt]`).
- Before adding heavy or security-sensitive deps, explain why in PR/commit message.
- After changing deps, update setup instructions if needed.

## 4. Database & Migrations
- All schema changes MUST go through Flyway migration files in `db/migration/`.
- Migrations use Flyway naming convention: `V{version}__{description}.sql` (e.g., `V1__initial_schema.sql`)
- Run migrations with: `./scripts/run_migrations.sh` or `flyway migrate -configFiles=flyway.conf`
- Never modify `init_db()` to create tables - it only initializes the connection pool.
- Table/column names use snake_case. Prefer `TIMESTAMPTZ` for timestamps.
- Never bypass the connection pool—use helpers in `database.py`.
- Flyway tracks migrations in `schema_version` table automatically.
- Migrations are immutable - Flyway validates file checksums to prevent modifications.

## 5. Authentication & Security
- Passwords must be hashed with `passlib`’s bcrypt context. Never log or return hashes.
- Auth endpoints return generic failure messages (no user existence leaks).
- Validate and sanitize all user inputs through Pydantic schemas.
- For new protected routes, integrate proper authentication/authorization (JWT or session) before exposing sensitive data.

## 6. API Design
- Route organization: keep feature-specific routers (e.g., `auth.py`) and mount them in `main.py`.
- Every endpoint must declare response models and status codes.
- Use descriptive HTTP errors (`HTTPException`) with consistent messages.
- Update API docs (`README.md`) when new endpoints are added or payloads change.

## 7. Logging & Observability
- Use FastAPI/uvicorn logging; add structured logs for critical actions (log level ≥ INFO).
- Never log secrets, tokens, or password hashes.

## 8. Testing & Verification
- Provide unit tests/integration tests for new features when possible (test stack TBD).
- Run local checks: `pip install -r requirements.txt`, `uvicorn main:app --reload`, and hit `/health` before pushing.
- Validate auth flows (`/auth/register`, `/auth/login`) whenever DB schema changes.

## 9. Git Hygiene
- Keep commits focused (one logical change per commit).
- Do not revert or overwrite user’s local changes unless explicitly asked.
- Reference issues/task IDs in commit messages if applicable.

## 10. Documentation
- Update `README.md` and any relevant docs for new endpoints, env vars, or setup steps.
- Document breaking changes explicitly and provide migration instructions if needed.

Failure to follow these rules risks regressions or rejected changes. When in doubt, ask for clarification before diverging.
