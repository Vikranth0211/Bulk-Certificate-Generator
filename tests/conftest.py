import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DB_FILE = Path(__file__).resolve().parent / "test_certificates.db"
SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

# Import Base and models
import app.db.database as db_module
from app.db.database import Base, get_db
from app.main import app

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Monkeypatch db_module.SessionLocal so background processor uses test DB!
db_module.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """Create fresh database tables for each test and cleanup after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except PermissionError:
            pass


@pytest.fixture(scope="function")
def db_session(setup_test_database):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Provide FastAPI TestClient override with test database dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
