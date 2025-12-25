# Product Overview: goblin API

## Product Description

goblin is a FastAPI-based REST API service that provides user authentication and management capabilities. It serves as a foundation for building applications that require secure user registration, login, and profile management.

**Note**: The project is currently in a migration phase, with plans to extend functionality for a Binance trading sandbox application. See `.claude/specs/initial-migrations/` for detailed migration requirements.

## Core Features

- **User Registration**: Create new user accounts with email and password validation
- **User Authentication**: Secure login with JWT token-based authentication
- **User Profile Management**: Retrieve authenticated user profile information
- **Health Monitoring**: Health check endpoint for API and database connectivity monitoring
- **Automatic Database Setup**: Automatic creation of required database tables on startup

## Target Use Cases

- **Backend API Foundation**: Starting point for applications requiring user authentication
- **Microservice Architecture**: Authentication service component in a distributed system
- **RESTful API Development**: Template for building FastAPI-based REST services
- **Learning/Prototyping**: Educational project demonstrating FastAPI, async PostgreSQL, and JWT authentication patterns

## Key Value Propositions

- **Modern Async Architecture**: Built with FastAPI and asyncpg for high-performance async I/O operations
- **Security-First Design**: Password hashing with bcrypt, JWT-based authentication, and secure credential handling
- **Developer-Friendly**: Automatic API documentation (Swagger/ReDoc), clear project structure, and comprehensive error handling
- **Production-Ready Patterns**: Connection pooling, environment-based configuration, and standardized response envelopes
- **Minimal Dependencies**: Lightweight stack with focused, well-maintained libraries

## API Response Standard

All endpoints use a consistent response envelope:

```json
{
  "status": "success" | "error",
  "message": "optional string",
  "meta": { "optional": "object" },
  "data": { "endpoint-specific": "payload" }
}
```

This ensures predictable API behavior and simplifies client-side error handling.

## API Documentation

- **OpenAPI Specification**: `swagger.yaml` (OpenAPI 3.0.3) provides complete API schema definition
- **Interactive Docs**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when server is running
- **Schema Definitions**: All request/response models are defined in both Pydantic schemas (`app/schemas/`) and OpenAPI spec

