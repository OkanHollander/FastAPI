from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from ..models import User
from ..database import SessionLocal

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = "0554859da927ff564fc428398d491b5bae536d469937d25159812cae1bbe80f9"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[Session, Depends(get_db)]

def auth_user(username: str,
              password: str,
              db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str,
                        user_id: int,
                        role: str,
                        expires_delta: timedelta):
    encode = {'sub': username,
              'id': user_id,
              'role': role,}
    expired = datetime.utcnow() + expires_delta
    encode.update({'exp': expired})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials') from exc



@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependancy,
                      CreateUserRequest: CreateUserRequest):
    create_user_model = User(
        email=CreateUserRequest.email,
        username=CreateUserRequest.username,
        first_name=CreateUserRequest.first_name,
        last_name=CreateUserRequest.last_name,
        hashed_password=bcrypt_context.hash(CreateUserRequest.password),
        role=CreateUserRequest.role,
        is_active=True,
        phone_number=CreateUserRequest.phone_number,
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                     db: db_dependancy):
    user = auth_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    token = create_access_token(user.username,
                                user.id,
                                user.role,
                                timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}
