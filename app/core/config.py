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
    # If BYBIT_SANDBOX=true, uses Bybit testnet (api-testnet.bybit.com).
    BYBIT_SANDBOX: bool = True
    BYBIT_MAINNET_BASE_URL: str = "https://api.bybit.com"
    BYBIT_TESTNET_BASE_URL: str = "https://api-testnet.bybit.com"
    # Optional override (useful for proxies or restricted networks).
    BYBIT_BASE_URL_OVERRIDE: str | None = None
    BYBIT_TIMEOUT_SECONDS: float = 10.0

    @property
    def BYBIT_BASE_URL(self) -> str:
        if self.BYBIT_BASE_URL_OVERRIDE:
            return self.BYBIT_BASE_URL_OVERRIDE
        return self.BYBIT_TESTNET_BASE_URL if self.BYBIT_SANDBOX else self.BYBIT_MAINNET_BASE_URL

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
