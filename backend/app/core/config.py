from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[3] / '.env', extra='ignore')
    llm_api_keys: str = ''
    llm_model: str = 'gemini/gemini-2.0-flash'
    database_url: str = 'sqlite:///./lyftr.db'
    allowed_origins: str = 'http://localhost:3000'
    enable_failure_simulation: bool = False
    default_system_prompt: str = 'You are a helpful AI assistant.'
    max_history_messages: int = 100
    @property
    def keys(self): return [k.strip() for k in self.llm_api_keys.split(',') if k.strip()]
    @property
    def origins(self): return [x.strip() for x in self.allowed_origins.split(',') if x.strip()]
@lru_cache
def get_settings(): return Settings()
settings = get_settings()
