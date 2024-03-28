from fastapi import status
from .utils import *
from ..routers.admin import get_db, get_current_user
from ..models import Todos

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_admin_read_all_authenticated(test_todo):
    """
    Test that authenticated users can read all todos.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Make a request to create a new todo
    response = client.get('/admin/todos')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "title": "Learn to code",
            "description": "Learn to code",
            "priority": 5,
            "complete": False,
            "owner_id": 1,
        }
    ]

def test_admin_delete_todo(test_todo):
    """
    Test that authenticated users can delete a todo.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Make a request to delete a todo
    response = client.delete('/admin/todos/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model is None

def test_admin_delete_todo_not_found(test_todo):
    """
    Test that authenticated users can delete a todo.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Make a request to delete a todo
    response = client.delete('/admin/todos/100')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 100).first()

    assert model is None
