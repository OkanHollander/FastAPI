from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import status
from ..database import Base
from ..main import app
from ..routers.todos import get_current_user, get_db

# Create a new TEST SQLITE database for testing
SQLALCHEMY_DATABASE = "sqlite:///./test.db"

# Create the database engine
engine = create_engine(SQLALCHEMY_DATABASE,
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool,)

# Create a SessionLocal object using the engine
TestingSessionLocal = sessionmaker(autocommit=False,
                                   autoflush=False,
                                   bind=engine)


Base.metadata.create_all(bind=engine)

# Override the get_db dependency to use a TestingSessionLocal
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_current_user dependency to return a test user
def override_get_current_user():
    return {'username': 'test_user', 'id': 1, 'user_role': 'admin'} 

# Change the dependencies for testing
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# force the app to run in testing mode
client = TestClient(app)

def test_read_all_authenticated():
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
