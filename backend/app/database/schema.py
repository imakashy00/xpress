from typing import Optional,List
from enum import Enum
from uuid import UUID
from click import Option
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime


class NewUser(BaseModel):
    email: EmailStr
    name: str
    password: str
    publication:str

    class Config:
        from_attributes = True
        # Config class is used to configure various Settings and behaviors of the model.
        # The attribute orm_mode = True is a specific setting that allows the
        # Pydantic model to work seamlessly with ORMs by enabling data parsing from ORM objects.


class UserBase(BaseModel):
    email: str
    is_active: bool = False
    is_superuser: bool = False


class MeOut(BaseModel):
    email: EmailStr
    name: str
    about: str | None
    image: str |None
    publication: str
    pub_desc: str | None
    pub_image: str | None
    followers: int
    following: int
    bookmarks: List[str]
    history: List[str]



class UpdateAccount(BaseModel):
    
    pub_name: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    about: Optional[str] = None
    pub_description: Optional[str] = None
    user_image: Optional[str] = None
    pub_image: Optional[str] = None



class LoginUser(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    

class  TokenData(BaseModel):
    username: str | None = None


""" Blogs Schema """



class BlogResponse(BaseModel):
    id: UUID
    title: str
    content: str
    author: UUID
    likes: int
    views: int
    updated_at: datetime


class CreateBlog(BaseModel):
    title: str
    content: str
    author: EmailStr


class UpdateBlog(BaseModel):
    title: str
    content: str
    author: EmailStr


class BookmarkResponse(BaseModel):
    blog_id: str

    class Config:
       from_attributes = True

class AddBookmark(BaseModel):
    user_id: str
    blog_id: str
    
    class Connfig:
        from_attributes = True

class AddHistory(BaseModel):
    user_id: str
    blog_id: str
    
    class Connfig:
        from_attributes = True

class PublicationOut(BaseModel):
    blogs: Optional[List[BlogResponse]]
    about: str | None
    followers: int
    pub_desc: str | None
