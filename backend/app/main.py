from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.database import Base, engine
from app.core.config import settings
from app.core.logging import configure_logging
from app.models.message import Message
from app.api.routes import health, chat, sessions

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
configure_logging()
app=FastAPI(title='Lyftr AI',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=['GET','POST'],allow_headers=['*'])
app.include_router(health.router); app.include_router(chat.router); app.include_router(sessions.router)
@app.exception_handler(RequestValidationError)
async def validation_error(request, exc): return JSONResponse(status_code=422,content={'detail':'invalid request'})

@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    logging.getLogger('lyftr').error('request_failed path=%s error_type=%s', request.url.path, type(exc).__name__)
    return JSONResponse(status_code=500, content={'detail':'internal server error'})
