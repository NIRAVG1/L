def normalize_metadata(response, key_id, fallback_attempts, latency_ms, cache_hit):
    usage=getattr(response,'usage',None)
    input_tokens=getattr(usage,'prompt_tokens',None)
    output_tokens=getattr(usage,'completion_tokens',None)
    if input_tokens is None or output_tokens is None:
        raise ValueError('provider token usage unavailable')
    return {
        'reply':response.choices[0].message.content,
        'model':getattr(response,'model',None),
        'latency_ms':latency_ms,
        'input_tokens':int(input_tokens),
        'output_tokens':int(output_tokens),
        'key_id':None if cache_hit else key_id,
        'fallback_attempts':0 if cache_hit else fallback_attempts,
        'resolution_source':'LLM_CACHE' if cache_hit else 'LIVE_INFERENCE',
    }
