from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE_MB: int = 100
    
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

