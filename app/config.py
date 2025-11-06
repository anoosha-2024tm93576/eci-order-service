from pydantic import BaseSettings

class Settings(BaseSettings):
    MYSQL_HOST: str = "db"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str


    SERVICE_PORT: int = 8000
    INVENTORY_URL: str
    PAYMENT_URL: str
    CATALOG_URL: str
    RESERVATION_TTL: int = 900
    LOG_LEVEL: str = "info"


    class Config:
        env_file = ".env"


settings = Settings()