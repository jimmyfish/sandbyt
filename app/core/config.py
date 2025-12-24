from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables or .env file.
    Binance API settings:
    - BINANCE_API_URL: Binance API base URL (default: https://api.binance.com)
      Can be set to testnet URL (https://testnet.binance.vision) via .env file.
    """

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

    # Binance API settings
    BINANCE_API_URL: str = "https://api.binance.com"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
