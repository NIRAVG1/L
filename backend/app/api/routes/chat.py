from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.schemas.chat_request import ChatRequest
from app.api.schemas.chat_response import ChatResponse
from app.services.chat_service import run_chat
from app.core.exceptions import ProviderFailure
router=APIRouter()
@router.post('/chat',response_model=ChatResponse)
def chat(request: ChatRequest, db: Session=Depends(get_db), simulation: str|None=Header(default=None,alias='X-Simulate-Failure')):
    try:
        result=run_chat(db,request,simulation)
        metadata={k:result[k] for k in ('resolution_source','model','latency_ms','input_tokens','output_tokens','key_id','fallback_attempts')}
        return {'session_id':request.session_id,'reply':result['reply'],'metadata':metadata}
    except ProviderFailure: raise HTTPException(503,'all providers unavailable')
    except Exception: raise HTTPException(503,'chat service unavailable')
