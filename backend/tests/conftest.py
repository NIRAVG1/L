import os
os.environ.setdefault('LLM_API_KEYS','test-key-one,test-key-two')
os.environ.setdefault('ENABLE_FAILURE_SIMULATION','true')
os.environ.setdefault('DATABASE_URL','sqlite://')
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.main import app

@pytest.fixture
def client():
    engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    TestingSession=sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)
    Base.metadata.create_all(engine)
    def override():
        db=TestingSession()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db]=override
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear(); Base.metadata.drop_all(engine); engine.dispose()
