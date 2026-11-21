from sqlalchemy import select
from app.repositories.message_repository import list_messages
from app.core.config import settings
from app.models.session_config import SessionConfig

def build_context(db, session_id, message, system_prompt):
    config=db.get(SessionConfig,session_id)
    if system_prompt:
        effective=system_prompt
        if config is None: db.add(SessionConfig(session_id=session_id,system_prompt=effective))
        else: config.system_prompt=effective
    else: effective=config.system_prompt if config else settings.default_system_prompt
    prior=list_messages(db,session_id)[-settings.max_history_messages:]
    messages=[{'role':'system','content':effective}]
    messages.extend({'role':m.role,'content':m.content} for m in prior)
    messages.append({'role':'user','content':message})
    return messages
