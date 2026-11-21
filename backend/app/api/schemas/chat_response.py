from pydantic import BaseModel
class Metadata(BaseModel):
    resolution_source: str
    model: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    key_id: str | None
    fallback_attempts: int
class ChatResponse(BaseModel):
    session_id: str
    reply: str
    metadata: Metadata
