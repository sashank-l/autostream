from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    groq_api_key: str
    google_creds_path: str = str(BASE_DIR / "gen-lang-client-0761784189-cd5c32525c54.json")
    knowledge_base_path: str = str(BASE_DIR / "app" / "rag" / "knowledge_base.json")
    model_name: str = "llama-3.1-8b-instant"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
