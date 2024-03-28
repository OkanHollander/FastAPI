from fastapi import status
from .utils import *
from ..routers.auth import get_current_user, get_db

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_auth_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = auth_user(test_user.username,
                                   'testpassword',
                                   db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = auth_user('non_existent_user',
                                  'testpassword',
                                  db)
    assert non_existent_user is False

    wrong_password_user = auth_user(test_user.username,
                                    'wrongpassword',
                                    db)
    assert wrong_password_user is False
