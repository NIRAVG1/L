from pydantic import BaseModel, Field, field_validator
class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    message: str
    system_prompt: str | None = None
    @field_validator('session_id')
    @classmethod
    def trim_session(cls,v):
        v=v.strip()
        if not v: raise ValueError('session_id must not be empty')
        return v
    @field_validator('message')
    @classmethod
    def valid_message(cls,v):
        v=v.strip()
        if not 1 <= len(v) <= 4000: raise ValueError('message must contain 1–4000 characters after trimming')
        return v
    @field_validator('system_prompt')
    @classmethod
    def trim_prompt(cls,v): return v.strip() if v else v
