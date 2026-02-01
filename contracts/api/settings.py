# settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    NUBANC_ENV: str= "dev"
    REDIS_URL: str

    class Config:
        env_file= ".env"
        env_file_encoding= "utf-8"

Settings= Settings()
model_config=SettingsConfigDict(env_file= ".env")
