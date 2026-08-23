"""
Centralized application configuration.

WHY: Hardcoding config values (API keys, DB URLs, model names) throughout the
codebase makes it impossible to change environments (dev/staging/prod) safely
and risks leaking secrets into source control. Pydantic's BaseSettings loads
config from environment variables (and a local .env file) with validation and
type-safety, which is the standard production pattern.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Customer Support AI Agent"
    ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # --- Security ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    RATE_LIMIT_PER_MINUTE: int = 60

    # --- LLM Provider ---
    # "groq" or "gemini" — both offer usable free tiers, unlike most paid-only APIs.
    LLM_PROVIDER: str = "groq"

    # Groq (OpenAI-compatible, free tier, very fast Llama/Mixtral inference)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    # Google Gemini (free tier via AI Studio)
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 1024
    CONFIDENCE_THRESHOLD: float = 0.55  # below this -> escalate to human

    # --- Embeddings / Vector store ---
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_DB_PATH: str = "./data/vectorstore"
    VECTOR_COLLECTION_NAME: str = "support_knowledge_base"
    RETRIEVAL_TOP_K: int = 4

    # --- Database ---
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/support_agent"

    # --- Misc ---
    MAX_CONVERSATION_TURNS_IN_MEMORY: int = 12

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we parse env vars once per process."""
    return Settings()
