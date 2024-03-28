from fastapi import status
from ..routers.users import get_current_user, get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    """
    Test that authenticated users can read all todos.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Make a request to create a new todo
    response = client.get('/user')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'test_user'
    assert response.json()['first_name'] == 'John'
    assert response.json()['last_name'] == 'Doe'
    assert response.json()['email'] == 'john@example.com'
    assert response.json()['phone_number'] == '+1234567890'

def test_change_password(test_user):
    """
    Test that authenticated users can change their password.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Make a request to create a new todo
    response = client.put('/user/change_password', json={
        'password': 'testpassword',
        'new_password': 'newpassword'
    })
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_incorrect_password(test_user):
    """
    Test that authenticated users can change their password.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Make a request to create a new todo
    response = client.put('/user/change_password', json={
        'password': 'wrongpassword',
        'new_password': 'newpassword'
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect password.'}

def test_change_phone_number(test_user):
    """
    Test that authenticated users can change their phone number.

    Args:
        test_todo (object): A test todo object.

    Returns:
        None

    """
    # Make a request to create a new todo
    response = client.put('/user/update_phone_number/123123123')
    assert response.status_code == status.HTTP_204_NO_CONTENT