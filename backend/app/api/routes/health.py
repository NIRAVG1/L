from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.core.database import engine
from app.core.config import settings
from app.integrations.litellm_gateway import gateway
router=APIRouter()
@router.get('/health')
def health():
    try:
        with engine.connect() as conn: conn.execute(text('SELECT 1'))
    except Exception: raise HTTPException(503,'database unavailable')
    if len(settings.keys)<2 or not gateway.cache_enabled: raise HTTPException(503,'required configuration unavailable')
    return {'status':'ok','keys_configured':len(settings.keys),'cache_enabled':gateway.cache_enabled}
