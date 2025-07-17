from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    HF_ACCESS_TOKEN: str
    FILE_ALLOWED_EXTENSTION: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE:int

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()