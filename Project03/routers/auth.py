from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from models import User
from database import SessionLocal
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


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
    return True

@router.post("/auth", status_code=status.HTTP_201_CREATED)
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
    )
    db.add(create_user_model)
    db.commit()

@router.post("/auth/login", status_code=status.HTTP_200_OK)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                     db: db_dependancy):
    user = auth_user(form_data.username, form_data.password, db)
    if not user:
        return 'Failed to authenticate'

    return 'Successfully logged in'
