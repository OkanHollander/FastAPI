from fastapi import APIRouter, Depends, Path
from fastapi.exceptions import HTTPException
from models import User
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def auth_failed(user):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")

db_dependancy = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=8, max_length=32)

@router.get("/get_user", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependancy, db: db_dependancy):
    auth_failed(user)
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user_model

@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependancy,
                          db: db_dependancy,
                          user_verification: UserVerification):
    auth_failed(user)
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password.")
    
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()

@router.put("/update_phone_number", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(user: user_dependancy,
                              db: db_dependancy,
                              phone_number: str):
    # check is user is authenticated
    auth_failed(user)
    # check if the correct user is fetched
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    # bind phone number to user
    user_model.phone_number = phone_number
    # update user in database
    db.add(user_model)
    # commit changes to database
    db.commit()
