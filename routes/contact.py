from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from repository.users import birthday_in_this_year
from fastapi import FastAPI, Path, Query, Depends, HTTPException, status
from schemas import ContactResponse, ContactModel
from database.db import get_db
from database.models import User, Contact
from datetime import datetime, timedelta, date
from typing import List
from sqlalchemy import and_
from services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/")
def root():
    return {"message": "Welcome to API!"}


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_user(body:ContactModel, current_user: User = Depends(auth_service.get_current_user), db:Session = Depends(get_db)):
    new_contact = db.query(Contact).filter(and_(Contact.email == body.email, Contact.user_id == current_user.id)).first()
    if new_contact:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "This email is exists!")
    new_contact = Contact(**body.dict(), user_id = current_user.id)
    new_contact.birthday_now = birthday_in_this_year(new_contact.day_birthday)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


@router.get("/", response_model=List[ContactResponse])
async def read_users(skip: int = 0, limit: int = Query(default=10, le=100, ge=10), current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    list_contacts = db.query(Contact).filter(Contact.user_id == current_user.id).offset(skip).limit(limit).all()
    return list_contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_user(contact_id: int = Path(description="The ID of the contact", ge=1), current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    search_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == current_user.id)).first()
    if search_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return search_contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_user(body:ContactModel, contact_id: int = Path(description="The ID of the user", ge=1), current_user: User = Depends(auth_service.get_current_user),  db: Session = Depends(get_db)):
    new_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == current_user.id)).first()
    if new_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    if new_contact:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "This email is exists!")
    new_contact.email = body.email
    new_contact.first_name = body.first_name
    new_contact.last_name = body.last_name
    new_contact.day_birthday = body.day_birthday
    new_contact.phone_number = body.phone_number
    new_contact.birthday_now = birthday_in_this_year(new_contact.day_birthday)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_user(email: str = None, first_name: str = None, last_name: str = None, day_birthday: date = None, phone_number: str = None, contact_id: int = Path(description="The ID of the user", ge=1), current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    new_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == current_user.id)).first()
    if new_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    if (email is not None) and (new_contact is not None):
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "This email is exists!")
    if email:
        new_contact.email = email
    if first_name:
        new_contact.first_name = first_name
    if last_name:
        new_contact.last_name = last_name
    if day_birthday:
        new_contact.day_birthday = day_birthday
        new_contact.birthday_now = birthday_in_this_year(day_birthday)
    if phone_number:
        new_contact.phone_number = phone_number
    db.commit()
    db.refresh(new_contact)
    return new_contact


@router.delete("/{contact_id}")
async def delete_user(contact_id: int = Path(description="The ID of the user", ge=1), current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    delete_contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == current_user.id)).first()
    if delete_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    db.delete(delete_contact)
    db.commit()


@router.get("/birthdays")
async def read_users(days:int = 7, current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    list_contacts = []
    for i in range(days):
        new_days = (datetime.now() + timedelta(days=i)).date()
        contacts = db.query(Contact).filter(and_(Contact.birthday_now == new_days, Contact.user_id == current_user.id)).all()
        list_contacts.append(contacts)
    return list_contacts


@router.get("/search/email", response_model=List[ContactResponse])
async def search_users(email: str, current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    list_contacts = db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == current_user.id)).all()
    return list_contacts

@router.get("/search/first_name", response_model=List[ContactResponse])
async def search_users(first_name: str, current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    list_contacts = db.query(Contact).filter(and_(Contact.first_name == first_name, Contact.user_id == current_user.id)).all()
    return list_contacts

@router.get("/search/last_name", response_model=List[ContactResponse])
async def search_users(last_name: str, current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    list_contacts = db.query(Contact).filter(and_(Contact.last_name == last_name, Contact.user_id == current_user.id)).all()
    return list_contacts

@router.get("/search", response_model=List[ContactResponse])
async def search_users(email: str = None, first_name: str = None, last_name: str = None, current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    if email and first_name and last_name:
        list_contacts = db.query(Contact).filter(and_(Contact.email == email, Contact.last_name == last_name, Contact.first_name == first_name, Contact.user_id == current_user.id)).all()
    elif not email:
        if first_name and last_name:
            list_contacts = db.query(Contact).filter(and_(Contact.last_name == last_name, Contact.first_name == first_name, Contact.user_id == current_user.id)).all()
        elif first_name:
            list_contacts = db.query(Contact).filter(and_(Contact.first_name == first_name, Contact.user_id == current_user.id)).all()
        elif last_name:
            list_contacts = db.query(Contact).filter(and_(Contact.last_name == last_name, Contact.user_id == current_user.id)).all()
    else:
        if first_name:
            list_contacts = db.query(Contact).filter(and_(Contact.email == email,Contact.first_name == first_name, Contact.user_id == current_user.id)).all()
        elif last_name:
            list_contacts = db.query(Contact).filter(and_(Contact.email == email, Contact.last_name == last_name, Contact.user_id == current_user.id)).all()
        else:
            list_contacts = db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == current_user.id)).all()
    if (email is None) and (first_name is None) and (last_name is None):
        list_contacts = db.query(Contact).all()
    return list_contacts

