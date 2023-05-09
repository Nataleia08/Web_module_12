from datetime import datetime
from libgravatar import Gravatar
from sqlalchemy.orm import Session

from database.models import User
from schemas import UserAuthModel

def birthday_in_this_year(date_birthday: datetime):
    new_date = datetime(year=2023, month=date_birthday.month, day=date_birthday.day).date()
    return new_date

async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserAuthModel, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()