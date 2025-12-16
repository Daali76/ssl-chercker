"""Application configuration management."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        """Initialize settings from environment variables."""
        # Project Info
        self.PROJECT_NAME: str = "SSL & Domain Checker"

        # Security
        self.SECRET_KEY: str = os.environ.get("SECRET_KEY", "changethis_in_prod")
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

        # Database
        self.DATABASE_URL: str = os.environ.get(
            "DATABASE_URL",
            "postgresql://sslchecker:secure_db_password@localhost:5432/sslchecker_db"
        )

        # Application Configuration
        self.EXPIRY_THRESHOLD_DAYS: int = int(os.environ.get("EXPIRY_THRESHOLD_DAYS", 10))
        self.CHECK_INTERVAL_HOURS: int = int(os.environ.get("CHECK_INTERVAL_HOURS", 24))

        # Shodan Configuration
        self.shodan_api_key: str = os.environ.get("SHODAN_API_KEY", "")

        # Default Admin Credentials
        self.DEFAULT_ADMIN_USER: str = os.environ.get("DEFAULT_ADMIN_USER", "admin")
        self.DEFAULT_ADMIN_PASSWORD: str = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin")

        # Logging
        self.LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")


# Create global settings instance
settings = Settings()