import os

class Settings:
    PROJECT_NAME: str = "SSL & Domain Checker"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "changethis_in_prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://sslchecker:secure_db_password@localhost:5432/sslchecker_db")
    
    # App Config
    EXPIRY_THRESHOLD_DAYS: int = int(os.environ.get("EXPIRY_THRESHOLD_DAYS", 10))
    CHECK_INTERVAL_HOURS: int = int(os.environ.get("CHECK_INTERVAL_HOURS", 24))
    
    # Default Admin
    DEFAULT_ADMIN_USER: str = os.environ.get("DEFAULT_ADMIN_USER", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin")

settings = Settings()