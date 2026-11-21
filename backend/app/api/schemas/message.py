from pydantic import BaseModel
class HistoryMessage(BaseModel):
    role: str
    content: str
    metadata: dict | None = None
class HistoryResponse(BaseModel):
    session_id: str
    messages: list[HistoryMessage]
