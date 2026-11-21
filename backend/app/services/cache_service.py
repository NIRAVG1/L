import hashlib,json
import litellm
from litellm.caching.caching import Cache
from app.core.config import settings
class CacheService:
    def __init__(self):
        # LiteLLM's SDK defaults to local memory, made explicit here.
        litellm.cache=Cache(type='local')
        self.enabled=True
        self._known=set()
    @staticmethod
    def prompt_key(messages): return hashlib.sha256(json.dumps([settings.llm_model,messages],sort_keys=True).encode()).hexdigest()
    def known(self,key): return key in self._known
    def record(self,key): self._known.add(key)
cache_service=CacheService()
