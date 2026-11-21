from threading import Lock
from app.services.context_service import build_context
from app.repositories.message_repository import save_exchange
from app.integrations.litellm_gateway import gateway
_locks={}; _locks_guard=Lock()
def session_lock(session_id):
    with _locks_guard: return _locks.setdefault(session_id,Lock())
def run_chat(db, request, simulation_header=None):
    with session_lock(request.session_id):
        context=build_context(db,request.session_id,request.message,request.system_prompt)
        result=gateway.chat(context,simulation_header)
        metadata={k:result[k] for k in ('resolution_source','model','latency_ms','input_tokens','output_tokens','key_id','fallback_attempts')}
        save_exchange(db,request.session_id,request.message,result['reply'],metadata)
        return result
