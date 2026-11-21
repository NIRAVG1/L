from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[3] / '.env', extra='ignore')
    llm_api_keys: str = ''
    open_ai_key: str = ''
    open_ai_key2: str = ''
    llm_model: str = 'gemini/gemini-2.0-flash'
    database_url: str = ''
    database_postgres_url: str = ''
    allowed_origins: str = 'http://localhost:3000'
    enable_failure_simulation: bool = False
    default_system_prompt: str = 'You are a helpful AI assistant.'
    max_history_messages: int = 100
    @property
    def keys(self):
        configured = [k.strip() for k in self.llm_api_keys.split(',') if k.strip()]
        if configured:
            return configured
        return [key for key in (self.open_ai_key, self.open_ai_key2) if key]
    @property
    def effective_database_url(self):
        return self.database_url or self.database_postgres_url or 'sqlite:///./lyftr.db'
    @property
    def origins(self): return [x.strip() for x in self.allowed_origins.split(',') if x.strip()]
@lru_cache
def get_settings(): return Settings()
settings = get_settings()
