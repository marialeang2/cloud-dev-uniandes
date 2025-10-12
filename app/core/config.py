from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE_MB: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

