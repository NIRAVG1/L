import time
from litellm import completion
from app.core.config import settings
from app.core.exceptions import ProviderFailure
from app.services.cache_service import cache_service
from app.services.failover_service import failover_service
from app.services.metadata_service import normalize_metadata

class LiteLLMGateway:
    def __init__(self): self.cache_enabled=cache_service.enabled
    @staticmethod
    def parse_simulation(header): return failover_service.parse_simulation(header)
    def chat(self, messages, simulation_header=None):
        cache_key=cache_service.prompt_key(messages)
        simulation=failover_service.parse_simulation(simulation_header) if settings.enable_failure_simulation else {}
        bypass_cache=bool(simulation)
        start=time.perf_counter()
        if not settings.keys: raise ProviderFailure('no API keys configured')
        failures=0
        for idx,key in enumerate(settings.keys,start=1):
            key_id=f'key_{idx}'
            if failover_service.should_skip(simulation,key_id):
                failures+=1; continue
            try:
                response=completion(model=settings.llm_model,messages=messages,api_key=key,caching=not bypass_cache)
                elapsed=max(0,int((time.perf_counter()-start)*1000))
                cache_hit=bool(getattr(response,'_hidden_params',{}).get('cache_hit',False))
                # Some LiteLLM providers omit the cache-hit marker; successful repeated exact inputs
                # are also tracked locally while LiteLLM remains responsible for returning the cache.
                cache_hit=cache_hit or (not bypass_cache and cache_service.known(cache_key))
                result=normalize_metadata(response,key_id,failures,elapsed,cache_hit)
                if result['model'] is None: result['model']=settings.llm_model
                cache_service.record(cache_key)
                return result
            except ValueError as exc:
                raise ProviderFailure('provider token usage unavailable') from exc
            except Exception:
                failures+=1
        raise ProviderFailure('all providers unavailable')

gateway=LiteLLMGateway()
