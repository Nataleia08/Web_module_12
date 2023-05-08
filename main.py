from sqlalchemy.orm import Session
from fastapi import FastAPI, Path, Query, Depends, HTTPException, status

from schemas import UserResponse, UserModel
from database.db import get_db
from database.models import User
from datetime import datetime, timedelta, date
from repository.users import birthday_in_this_year
from typing import List

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to API!"}


@app.post("/users", response_model=UserResponse, tags=["users"])
async def create_user(body:UserModel, db:Session = Depends(get_db)):
    user = db.query(User).filter_by(email = body.email).first()
    if user:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "This email is exists!")
    user = User(**body.dict())
    user.birthday_now = birthday_in_this_year(user.day_birthday)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users", response_model=List[UserResponse], tags=["users"])
async def read_users(skip: int = 0, limit: int = Query(default=10, le=100, ge=10), db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def read_user(user_id: int = Path(description="The ID of the user", ge=1), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return user

@app.put("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def update_user(body:UserModel, user_id: int = Path(description="The ID of the user", ge=1), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "This email is exists!")
    user.email = body.email
    user.first_name = body.first_name
    user.last_name = body.last_name
    user.day_birthday = body.day_birthday
    user.phone_number = body.phone_number
    user.birthday_now = birthday_in_this_year(user.day_birthday)
    db.commit()
    db.refresh(user)
    return user

@app.patch("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def update_user(email: str = None, first_name: str = None, last_name: str = None, day_birthday: date = None, phone_number: str = None, user_id: int = Path(description="The ID of the user", ge=1), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    if (email is not None)and (db.query(User).filter(User.email == email).first() is not None):
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "This email is exists!")
    if email:
        user.email = email
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if day_birthday:
        user.day_birthday = day_birthday
        user.birthday_now = birthday_in_this_year(day_birthday)
    if phone_number:
        user.phone_number = phone_number
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int = Path(description="The ID of the user", ge=1), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    db.delete(user)
    db.commit()


@app.get("/birthdays", tags=["birthday"])
async def read_users(days:int = 7, db: Session = Depends(get_db)):
    list_users = []
    for i in range(days):
        new_days = (datetime.now() + timedelta(days=i)).date()
        users = db.query(User).filter(User.birthday_now == new_days).all()
        list_users.append(users)
    return list_users


@app.get("/search/email", response_model=List[UserResponse], tags=["search"])
async def search_users(email: str, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.email == email).all()
    return users

@app.get("/search/first_name", response_model=List[UserResponse], tags=["search"])
async def search_users(first_name: str, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.first_name == first_name).all()
    return users

@app.get("/search/last_name", response_model=List[UserResponse], tags=["search"])
async def search_users(last_name: str, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.last_name == last_name).all()
    return users

@app.get("/search", response_model=List[UserResponse], tags=["search"])
async def search_users(email: str = None, first_name: str = None, last_name: str = None, db: Session = Depends(get_db)):
    if email and first_name and last_name:
        users = db.query(User).filter((User.email == email) and (User.last_name == last_name) and (User.first_name == first_name)).all()
    elif not email:
        if first_name and last_name:
            users = db.query(User).filter((User.last_name == last_name) and (User.first_name == first_name)).all()
        elif first_name:
            users = db.query(User).filter((User.first_name == first_name)).all()
        elif last_name:
            users = db.query(User).filter((User.last_name == last_name)).all()
    else:
        if first_name:
            users = db.query(User).filter(
                (User.email == email) and (User.first_name == first_name)).all()
        elif last_name:
            users = db.query(User).filter(
                (User.email == email) and (User.last_name == last_name)).all()
        else:
            users = db.query(User).filter(User.email == email).all()
    if (email is None) and (first_name is None) and (last_name is None):
        users = db.query(User).all()
    return users