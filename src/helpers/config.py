from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    
    FILE_ALLOWED_EXTENSTION: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE:int

    MONGODB_DATABASE: str
    MONGODB_URL: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None
    HF_ACCESS_TOKEN: str = None

    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None

    DEFAULT_INPUT_MAX_CHARACTER: int = None
    DEFAULT_GENERATION_MAX_TOKENS: int = None
    DEFAULT_GENERATION_TEMPERATURE: float = None
    

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()