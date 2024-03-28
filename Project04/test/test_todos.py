from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..models import Todos
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

def test_read_all_authenticated(test_todo):
    """
    Test that authenticated users can read all todos.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'Learn to code',
                                'description': 'Learn to code',
                                'priority': 5,
                                'complete': False,
                                'owner_id': 1,
                                'id': 1,}]


def test_read_one_authenticated(test_todo):
    """
    Test that authenticated users can read one todo.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    response = client.get('/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title': 'Learn to code',
                                'description': 'Learn to code',
                                'priority': 5,
                                'complete': False,
                                'owner_id': 1,
                                'id': 1,}

def test_read_one_authenticated_not_found():
    """
    Test that authenticated users can read one todo.
    This should return a 404 Not Found error, because we supplied an invalid id.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    response = client.get('/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}

def test_create_todo(test_todo):
    """
    Test that authenticated users can create a new todo.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Create dummy todo data
    request_data = {
        'title': 'New todo title',
        'description': 'New todo description',
        'priority': 5,
        'complete': False,
    }

    # Make a request to create a new todo
    response = client.post('/todo/', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()

    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

def test_update_todo(test_todo):
    """
    Test that authenticated users can update a todo.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Create dummy todo data
    request_data = {
        'title': 'Updated todo title',
        'description': 'Updated todo description',
        'priority': 1,
        'complete': True,
    }

    # Make a request to create a new todo
    response = client.put('/todo/1', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')

def test_update_todo_not_found():
    """
    Test that authenticated users can update a todo.
    This should return a 404 Not Found error, because we supplied an invalid id.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Create dummy todo data
    request_data = {
        'title': 'Updated todo title',
        'description': 'Updated todo description',
        'priority': 1,
        'complete': True,
    }

    # Make a request to create a new todo
    response = client.put('/todo/999', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}

def test_delete_todo(test_todo):
    """
    Test that authenticated users can delete a todo.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Make a request to create a new todo
    response = client.delete('/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model is None

def test_delete_todo_not_found():
    """
    Test that authenticated users can delete a todo.
    This should return a 404 Not Found error, because we supplied an invalid id.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Make a request to create a new todo
    response = client.delete('/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}

