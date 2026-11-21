from app.integrations.litellm_gateway import gateway

def test_cache_metadata_contract(client,monkeypatch):
    seen=[]
    def fake(messages,simulation_header=None):
        seen.append(messages)
        cached=len(seen)>1
        return {'reply':'same','model':'m','latency_ms':1,'input_tokens':4,'output_tokens':1,'key_id':None if cached else 'key_1','fallback_attempts':0,'resolution_source':'LLM_CACHE' if cached else 'LIVE_INFERENCE'}
    monkeypatch.setattr(gateway,'chat',fake)
    a=client.post('/chat',json={'session_id':'a','message':'same'}).json()
    b=client.post('/chat',json={'session_id':'b','message':'same'}).json()
    assert a['reply']==b['reply'] and b['metadata']['resolution_source']=='LLM_CACHE'
