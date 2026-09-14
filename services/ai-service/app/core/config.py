from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    PROJECT_NAME: str
    INTERNAL_API_KEY: str
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    GEMINI_BASE_URL: str

    QDRANT_HOST: str
    QDRANT_PORT: int
    QDRANT_COLLECTION_NAME: str

    EMBEDDING_MODEL: str
    CHAT_MODEL: str

settings = Settings()
