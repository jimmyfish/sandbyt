from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "newsly"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    # JWT settings
    JWT_SECRET_KEY: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60

    # Bybit settings (market data; public endpoints)
    # Configured entirely via environment variables (no testnet/mainnet URLs hardcoded here).
    # Example values:
    # - https://api-testnet.bybit.com
    # - https://api.bybit.com
    BYBIT_BASE_URL: str = ""
    BYBIT_TIMEOUT_SECONDS: float = 10.0

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
