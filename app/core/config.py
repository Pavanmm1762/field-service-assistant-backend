from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    FRONTEND_URL: str
    DATABASE_URL: str

    LLM_PROVIDER: str = "gemini"
    LLM_BASE_URL: str | None = None
    LLM_API_KEY: SecretStr | None = None
    LLM_API_TYPE: str = "openai"
    LLM_API_VERSION: str | None = None
    LLM_MODEL: str
    LLM_EMBEDDING_MODEL: str | None = None
    LLM_VISION_MODEL: str | None = None

    # Backward compatibility for the current deployment. Prefer LLM_API_KEY.
    GEMINI_API_KEY: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def llm_api_key_value(self) -> str:
        key = self.LLM_API_KEY or self.GEMINI_API_KEY
        return key.get_secret_value() if key else ""


settings = Settings()
