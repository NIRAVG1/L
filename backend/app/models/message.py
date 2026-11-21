from sqlalchemy import Column, Integer, String, Text, Index
from app.core.database import Base
class Message(Base):
    __tablename__='messages'
    id=Column(Integer, primary_key=True, autoincrement=True)
    session_id=Column(String(128), nullable=False, index=True)
    role=Column(String(16), nullable=False)
    content=Column(Text, nullable=False)
    metadata_json=Column('metadata', Text, nullable=True)
    created_at=Column(String(40), nullable=False)
    __table_args__=(Index('ix_messages_session_order','session_id','id'),)
