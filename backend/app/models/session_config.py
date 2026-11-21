from sqlalchemy import Column, String
from app.core.database import Base
class SessionConfig(Base):
    __tablename__='session_configs'
    session_id=Column(String(128),primary_key=True)
    system_prompt=Column(String,nullable=False)
