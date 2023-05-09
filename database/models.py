from sqlalchemy import Boolean, Column, func, DateTime, Integer, String, Date, ForeignKey
from database.db import Base, engine
from sqlalchemy.orm import relationship

class Contact(Base):
    __tablename__ = "contact"

    id = Column('id',Integer, primary_key = True, index = True)
    first_name = Column('first_name', String(length=50))
    last_name = Column('last_name',String(length=50))
    email = Column('email', String(length=150), unique=True)
    phone_number = Column('phone', String(length=150))
    day_birthday = Column('birthday', Date)
    hashed_password = Column('password', String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    update_at = Column(DateTime, default=func.now(), onupdate=func.now())
    birthday_now = Column(Date)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="contact")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)


Base.metadata.create_all(bind=engine)
