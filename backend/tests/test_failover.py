from app.integrations.litellm_gateway import gateway, ProviderFailure
from app.core.config import settings

def test_simulation_parse():
    assert gateway.parse_simulation('key_1=429,key_2=502,*=503')=={'key_1':429,'key_2':502,'*':503}
def test_simulated_failure_does_not_persist(client,monkeypatch):
    monkeypatch.setattr(settings,'enable_failure_simulation',True)
    def fail(*args,**kwargs): raise ProviderFailure('all providers unavailable')
    monkeypatch.setattr(gateway,'chat',fail)
    response=client.post('/chat',json={'session_id':'failed','message':'test'},headers={'X-Simulate-Failure':'*=429'})
    assert response.status_code==503
    assert client.get('/sessions/failed/messages').status_code==404
from types import SimpleNamespace

def test_gateway_tries_next_real_key(monkeypatch):
    import app.integrations.litellm_gateway as module
    calls=[]
    def provider(**kwargs):
        calls.append(kwargs['api_key'])
        if len(calls)==1: raise RuntimeError('429')
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='genuine reply'))],usage=SimpleNamespace(prompt_tokens=10,completion_tokens=3),model='gemini/gemini-2.0-flash',_hidden_params={})
    monkeypatch.setattr(module,'completion',provider)
    result=module.gateway.chat([{'role':'user','content':'unique failover prompt'}])
    assert calls==settings.keys
    assert result['key_id']=='key_2' and result['fallback_attempts']==1
    assert result['reply']=='genuine reply'
