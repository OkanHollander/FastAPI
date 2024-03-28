from fastapi import status
from jose import jwt
from datetime import timedelta
import pytest
from .utils import *
from ..routers.auth import get_db, auth_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user


app.dependency_overrides[get_db] = override_get_db

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

def test_create_access_token(test_user):
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_valid_token():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user['username'] == 'testuser'
    assert user['id'] == 1
    assert user['user_role'] == 'admin'
