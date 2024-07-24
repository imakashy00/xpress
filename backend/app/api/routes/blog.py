
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException,status
from database.models import Blog,Publication,User
from database.crud import already_registered
from database.schema import LoginUser, PublicationOut,BlogResponse, TokenData
from auth.auth import get_current_user
from core.db import get_db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


router = APIRouter()



@router.get('/search/{topic}', )
async def searched_topic(topic, db:Session = Depends(get_db)):
    blogs = db.query(Blog).filter(Blog.title.contains(topic)).all()
    return blogs   
  

@router.get('/{publication_id}',response_model=PublicationOut)
async def published_blogs(publication_id:str, current_user:TokenData = Depends(get_current_user),db: Session = Depends(get_db)):

    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")
    
    user = db.query(User).filter(User.id == publication.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    blogs = db.query(Blog).filter(Blog.publication_id == publication_id).order_by(Blog.updated_at.desc()).all()
    blog_list = [BlogResponse(
        id = blog.id,
        title= blog.title,
        content = blog.content,
        author=blog.author_id,
        likes=blog.likes_count,
        views=blog.read_count,
        updated_at=blog.updated_at
    )for blog in blogs]
    publicaton_details = PublicationOut(
        blogs=blog_list,
        about= user.about,
        followers=publication.followers_count,
        pub_desc=publication.description    
    )
    return publicaton_details


@router.get('/{publication_id}/{blog_id}',response_model=BlogResponse)
async def public_blog(publication_id:UUID, blog_id:UUID, current_user:LoginUser = Depends(get_current_user),db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.publication_id == publication_id,Blog.id == blog_id).first()
    print(blog)
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No blogs found for this publication")
    
    blog_response = BlogResponse(
        id=blog.id,
        title=blog.title,
        content=blog.content,
        author=blog.author_id,
        likes=blog.likes_count,
        views=blog.read_count,
        updated_at=blog.updated_at
    )
    
    return blog_response





