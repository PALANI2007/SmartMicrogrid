from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./microgrid2.db"
    MODEL_PATH: str = "../ml/models/forecast_model.joblib"
    DATA_PATH: str = "../data"
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    DEBUG: bool = True

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()
