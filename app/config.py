from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Financial Market Data Warehouse"
    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "financial_market_dwh"
    NASDAQ_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()