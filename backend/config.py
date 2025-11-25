from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    cors_origins: str = "http://localhost:3000"
    r2_endpoint: str | None = None
    r2_access_key: str | None = None
    r2_secret_key: str | None = None
    r2_bucket: str | None = None
    r2_public_domain: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
