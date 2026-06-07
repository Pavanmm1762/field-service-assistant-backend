from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FRONTEND_URL: str
    GEMINI_API_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()