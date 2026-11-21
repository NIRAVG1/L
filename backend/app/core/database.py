from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings
kwargs = {'check_same_thread': False, 'timeout': 30} if settings.database_url.startswith('sqlite') else {}
engine = create_engine(settings.database_url, connect_args=kwargs, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
