from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import pytest
from ..database import Base
from ..main import app
from ..models import Todos, User
from ..routers.auth import bcrypt_context


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

# force the app to run in testing mode
client = TestClient(app)

# Create a test todo object for testing
@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code",
        description="Learn to code",
        priority=5,
        complete=False,
        owner_id=1,
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    # Delete the test todo object after the test is complete
    # This will ensure that the test todo object is not left in the database
    # And that every test ran, will be in a clean database
    yield todo
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM todos;"))
        conn.commit()

@pytest.fixture
def test_user():
    user = User(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone_number="+1234567890",
        hashed_password="jemoederislelijk",
        role="admin",
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    # Delete the test todo object after the test is complete
    # This will ensure that the test todo object is not left in the database
    # And that every test ran, will be in a clean database
    yield user
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users;"))
        conn.commit()
