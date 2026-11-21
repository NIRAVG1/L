from app.integrations.litellm_gateway import gateway

def fake(*args,**kwargs): return {'reply':'Hello there','model':'gemini/gemini-2.0-flash','latency_ms':12,'input_tokens':8,'output_tokens':2,'key_id':'key_1','fallback_attempts':0,'resolution_source':'LIVE_INFERENCE'}
def test_chat_and_persistence(client,monkeypatch):
    monkeypatch.setattr(gateway,'chat',fake)
    r=client.post('/chat',json={'session_id':'s-1','message':' hello '})
    assert r.status_code==200 and r.json()['metadata']['input_tokens']==8
    hist=client.get('/sessions/s-1/messages').json()['messages']
    assert [m['role'] for m in hist]==['user','assistant']
    assert hist[0]['content']=='hello' and hist[1]['metadata']['key_id']=='key_1'
def test_validation(client):
    assert client.post('/chat',json={'session_id':'x','message':'   '}).status_code==422
    assert client.post('/chat',json={'session_id':'x','message':'x'*4001}).status_code==422
    assert client.post('/chat',json={'message':'x'}).status_code==422
def test_unknown_session(client):
    assert client.get('/sessions/nope/messages').status_code==404

def test_followup_context_and_session_isolation(client,monkeypatch):
    contexts=[]
    def record(messages,simulation_header=None):
        contexts.append(messages)
        return fake()
    monkeypatch.setattr(gateway,'chat',record)
    client.post('/chat',json={'session_id':'context-a','message':'Remember the word indigo'})
    client.post('/chat',json={'session_id':'context-a','message':'What word did I ask you to remember?'})
    client.post('/chat',json={'session_id':'context-b','message':'Is there any prior context?'})
    assert [m['role'] for m in contexts[1]]==['system','user','assistant','user']
    assert contexts[1][1]['content']=='Remember the word indigo'
    assert len(contexts[2])==2
    assert all('indigo' not in m['content'] for m in contexts[2])
