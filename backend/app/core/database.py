from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings
database_url = settings.database_url
if database_url.startswith('postgres://'):
    database_url = 'postgresql+psycopg://' + database_url.removeprefix('postgres://')
elif database_url.startswith('postgresql://'):
    database_url = 'postgresql+psycopg://' + database_url.removeprefix('postgresql://')

kwargs = {'check_same_thread': False, 'timeout': 30} if database_url.startswith('sqlite') else {}
engine = create_engine(database_url, connect_args=kwargs, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
