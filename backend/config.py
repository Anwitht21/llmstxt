from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    cors_origins: str = "http://localhost:3000"
    r2_endpoint: str | None = None
    r2_access_key: str | None = None
    r2_secret_key: str | None = None
    r2_bucket: str | None = None
    r2_public_domain: str | None = None
    supabase_url: str | None = None
    supabase_key: str | None = None
    cron_secret: str | None = None
    brightdata_api_key: str | None = None
    brightdata_enabled: bool = True
    brightdata_zone: str = "scraping_browser1"
    brightdata_password: str | None = None
    openrouter_api_key: str | None = None
    openrouter_model: str = "x-ai/grok-4.1-fast:free"
    llm_enhancement_enabled: bool = False
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3
    llm_temperature: float = 0.3

    class Config:
        env_file = ".env"

settings = Settings()
