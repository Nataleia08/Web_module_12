from pydantic import BaseModel, EmailStr, PastDate, Field, FutureDate
from datetime import datetime, date
from typing import Optional

class ContactModel(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str
    day_birthday: PastDate
class ContactResponse(BaseModel):
    id: int = Field(default=1, ge=1)
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str
    day_birthday: PastDate
    birthday_now: date
    is_active: bool
    created_at: datetime
    update_at: datetime

    class Config():
        orm_mode = True

class UserAuthModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserAuthResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"