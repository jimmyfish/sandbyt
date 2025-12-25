#!/bin/bash
# Run Flyway migrations using environment variables from .env file

# Load environment variables from .env file (handles empty values and special chars)
if [ -f .env ]; then
    set -a  # automatically export all variables
    source .env
    set +a  # stop automatically exporting
fi

# Set defaults if not set
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-goblin}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}

# Export Flyway environment variables (Flyway automatically reads these)
export FLYWAY_URL="jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}"
export FLYWAY_USER="${DB_USER}"
export FLYWAY_PASSWORD="${DB_PASSWORD}"

# Debug output (can be removed in production)
if [ "${DEBUG_MIGRATIONS:-}" = "1" ]; then
    echo "Using database: ${DB_NAME} on ${DB_HOST}:${DB_PORT}"
    echo "User: ${DB_USER}"
fi

# Run Flyway migrate (will use environment variables and flyway.conf)
flyway migrate -configFiles=flyway.conf

