from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduPath AI"
    API_V1_STR: str = "/api/v1"

    # Groq (free) — get key at console.groq.com
    GROQ_API_KEY: str = ""

    # API Key (production auth)
    API_KEY: str = "changeme-set-in-env"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Environment
    ENV: str = "development"

    # Redis cache (optional — free via Upstash or local Docker)
    # Leave empty to use in-memory fallback (no setup needed)
    # Upstash free tier: https://upstash.com
    # Local:  redis://localhost:6379
    # Upstash: rediss://:password@host.upstash.io:port
    REDIS_URL: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
