import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.message_repository import list_messages
router=APIRouter()
@router.get('/sessions/{session_id}/messages')
def history(session_id: str, db: Session=Depends(get_db)):
    rows=list_messages(db,session_id)
    if not rows: raise HTTPException(404,'session not found')
    return {'session_id':session_id,'messages':[{'role':m.role,'content':m.content,**({'metadata':json.loads(m.metadata_json)} if m.metadata_json else {})} for m in rows]}
