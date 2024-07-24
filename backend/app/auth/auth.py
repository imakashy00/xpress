
from fastapi import APIRouter, Depends, HTTPException, Security,status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database.schema import NewUser, TokenData
from core.db import get_db
from database.crud import already_registered, register_publication,register_user,registerd_publication,add_publication_id
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError
import jwt



import os
from dotenv import load_dotenv


load_dotenv()



SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getcwd('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')



pwd_context = CryptContext(schemes=['bcrypt'],deprecated = 'auto')

auth = OAuth2PasswordBearer(tokenUrl='login')

router = APIRouter()


def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)


def get_hashed_password(password):
    return pwd_context.hash(password)


def authenticate_user(username:str, password:str,db:Session):
    user = already_registered(username,db)
    if not user:
        return False
    if not verify_password(password,user.password):
        return False
    return user


def create_access_token(data:dict, expire:timedelta | None = None):
    to_encode = data.copy()
    if expire:
        expire = datetime.now(timezone.utc) +expire
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token:str,credentials_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        email:str = payload.get('sub')
        if email is None:
            raise credentials_exception
        token_data = TokenData(username=email)
        return token_data
    except jwt.PyJWTError:
        raise credentials_exception

def get_current_user(data:str = Depends(auth)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_token(data,credentials_exception)


@router.post('/register')
async def register(req: NewUser, db: Session = Depends(get_db)):
    user = already_registered(req.email,db)
    publication = registerd_publication(req.publication,db)
    print(publication)
    if user:
        raise HTTPException(status_code=400,detail="User already exists!")
    
    elif publication:
        raise HTTPException(status_code=400,detail=f"{req.publication} already exists!")
    else:
        email = req.email
        hashed_password = get_hashed_password(req.password)
        try:
            register_user(db,email,hashed_password,req.name)
            register_publication(req.email,req.publication,db)
            add_publication_id(req.publication, req.email,db)
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Something went wrong!")

        return {"message":f"Registration sucessful for {req.email}"}

@router.post('/login')
async def login(request:OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user_found = already_registered(request.username,db)
    if not user_found:
        raise HTTPException(status_code=401,detail='Invalid username or password')
    verfied = verify_password(request.password,user_found.password)
    if not verfied:
        raise HTTPException(status_code=401,detail='Invalid username or password')
    access_token = create_access_token(data = {"sub":user_found.email})
    return {'access_token':access_token,'token_type':'bearer'}


    