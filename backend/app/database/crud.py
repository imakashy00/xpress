from datetime import datetime
from os import name
from fastapi import HTTPException,status
from sqlalchemy.exc import SQLAlchemyError
from pydantic import EmailStr
from sqlalchemy.orm import Session
from database.models import Publication, User



def already_registered(email:EmailStr,db: Session):
    return db.query(User).filter(User.email == email).first()


def registerd_publication(publication:str,db: Session):
    return db.query(Publication).filter(Publication.name == publication).first()
    

def register_user(db: Session,email, password, name):
    new_user = User(email=email,password = password,name = name)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except SQLAlchemyError as e:
        print("Going to rollback")
        db.rollback()
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong!")
    
def register_publication(email: EmailStr, publication:str,db: Session):
    user_id = db.query(User).filter(User.email == email).first().id
    new_publication = Publication(
        name = publication,
        created_at = datetime.now(),
        user_id = user_id
        )
    try:
        db.add(new_publication)
        db.commit()
        db.refresh(new_publication)
    except SQLAlchemyError as e :
        print("Going to rollback")
        db.rollback()
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong!")

def add_publication_id(publication_name:str,email: EmailStr, db: Session):

    publication = db.query(Publication).filter(Publication.name == publication_name).first()

    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Publication '{publication_name}' not found!")
    
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email '{email}' not found!")
    
    try:
        user.publication_id = publication.id
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong while updating the user's publication ID!")
    
    

