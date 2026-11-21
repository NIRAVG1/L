import json
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.message import Message

def list_messages(db: Session, session_id: str):
    return list(db.scalars(select(Message).where(Message.session_id==session_id).order_by(Message.id)))
def save_exchange(db: Session, session_id: str, user: str, reply: str, metadata: dict):
    now=datetime.now(timezone.utc).isoformat()
    try:
        db.add_all([Message(session_id=session_id,role='user',content=user,metadata_json=None,created_at=now), Message(session_id=session_id,role='assistant',content=reply,metadata_json=json.dumps(metadata),created_at=now)])
        db.commit()
    except Exception:
        db.rollback(); raise
