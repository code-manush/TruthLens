import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    # Tavily API
    tavily_api_key: str = ""

    # Scoring Weights
    weight_clickbait: float = 0.20
    weight_emotion: float = 0.15
    weight_relevance: float = 0.15
    weight_ad_density: float = 0.10
    weight_authenticity: float = 0.20
    weight_claim_verification: float = 0.20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
