from datetime import datetime
from typing import Annotated, Any, List
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy import UUID
from database.crud import already_registered
from database.schema import CreateBlog, LoginUser, MeOut, TokenData,BookmarkResponse,AddBookmark,AddHistory, UpdateAccount
from auth.auth import get_current_user
from database.schema import LoginUser,UpdateBlog
from database.models import Bookmark, Follow, History, Publication, Blog, User
from sqlalchemy.exc import SQLAlchemyError
from core.db import get_db
from database.crud import registerd_publication
from sqlalchemy.orm import Session
from auth.auth import get_hashed_password

router = APIRouter()



@router.get('/me',response_model=MeOut)
async def profile(current_user:TokenData = Depends(get_current_user),db:Session = Depends(get_db))-> MeOut:
    
    try:
        user = db.query(User).filter(User.email == current_user.username).first()
        publication = db.query(Publication).filter(Publication.user_id == user.id).first()
        history_list = db.query(History.blog_id).filter(History.user_id == user.id).order_by(History.read_at.desc()).all()
        bookmark_list = db.query(Bookmark.blog_id).filter(Bookmark.user_id == user.id).order_by(Bookmark.marked_at.desc()).all()
        followers = db.query(Follow.follower_id).filter(Follow.following_id == user.id).all().count(Follow.follower_id)
        following = db.query(Follow.following_id).filter(Follow.follower_id == user.id).all().count(Follow.following_id)
        userout = MeOut(
            email = user.email,
            name = user.name,
            image= user.image,
            about = user.about,
            publication = publication.name,
            pub_desc = publication.description,
            pub_image = publication.image,
            followers = followers,
            following = following,
            bookmarks = bookmark_list,
            history = history_list,
            )
        return userout
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Something went wrong!")



@router.put('/me/settings/account')
async def settings(update_account:UpdateAccount, current_user:TokenData = Depends(get_current_user),db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    publication = db.query(Publication).filter(Publication.user_id == user.id).first()

    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if update_account.name:
        user.name = update_account.name

    if update_account.pub_name:
        found_pub = registerd_publication(update_account.pub_name,db)
        if found_pub:
            print(found_pub.name)
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"{update_account.name} already exists")
        publication.name = update_account.pub_name

    if update_account.about:
        user.about = update_account.name
    if update_account.pub_description:
        publication.description = update_account.pub_description

    if update_account.password:

        user.password = get_hashed_password(update_account.password)
    if update_account.user_image:
        user.image = update_account.user_image
    if update_account.pub_image:
        publication.image = update_account.pub_image
    try:
        db.commit()
        return {"Updated"}
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Something went wrong!")



@router.put('/me/settings/notification')
async def settings(current_user:TokenData = Depends(get_current_user),db:Session = Depends(get_db)):
    return{"hello from account settings"}

@router.get('/me/blogs')
async def library(current_user:TokenData = Depends(get_current_user),db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user.username).first()
    blogs = db.query(Blog).filter(Blog.author_id == user.id).all()
    return blogs


@router.get('/me/history')
async def history(current_user:TokenData = Depends(get_current_user), db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user.username).first()
    history_list = db.query(History.blog_id).filter(History.user_id == user.id).order_by(History.read_at.desc()).all()
    return history_list


@router.post('/me/history/{blog_id}')
async def history(blog_id:str, current_user:TokenData = Depends(get_current_user), db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user.username).first()
    new_history = AddHistory(
        user_id=user.id,
        blog_id=blog_id
        )
    try:
        db.add(new_history)
        db.commit()
        return {"message":f"{blog_id} added to history"}
    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Something went wrong!")

@router.get('/me/saved',response_model=List[BookmarkResponse])
async def saved(current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    bookmark_list = db.query(Bookmark).filter(Bookmark.user_id == user.id).order_by(Bookmark.marked_at.desc()).all()
    response = [BookmarkResponse(blog_id=str(bookmark.blog_id)) for bookmark in bookmark_list]
    return response


@router.get('/me/saved/{blog_id}',)
async def saved(blog_id:str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    bookmark_blog = db.query(Bookmark).filter(Bookmark.user_id == user.id).where(Bookmark.blog_id == blog_id).first()
   
    return bookmark_blog


@router.post('/me/saved/{blog_id}')
async def saved(blog_id:str, current_user:TokenData = Depends(get_current_user),db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user.username).first()
    new_bookmark = AddBookmark(
        user_id=user.id,
        blog_id= blog_id,
    )
    try:
        db.add(new_bookmark)
        db.commit()
        return {"message":f"{blog_id} added to bookmark"}
    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Something went wrong!")


@router.delete('/me/saved/{blog_id}')
async def saved(blog_id:str, current_user:TokenData = Depends(get_current_user),db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user.username).first()
    try:
        db.query(Bookmark).filter(Bookmark().user_id == user.id).where(Bookmark.blog_id == blog_id).delete()
        db.commit()
        return {"messahe":f"{blog_id} removed from bookmark"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details = "Something went wrong!")




""" CREATE Blog"""

@router.post('/create')
async def create_blog(blog:CreateBlog, current_user:LoginUser = Depends(get_current_user),db:Session = Depends(get_db)):
    author = already_registered(blog.author,db)

    if author.id:
        publication = db.query(Publication).filter(Publication.user_id == author.id).first()
        
        new_blog = Blog(
            title = blog.title,
            content = blog.content,
            author = author,
            publication_id = publication.id
        )
        try:
            db.add(new_blog)
            db.commit()
            return {"message": f"Blog '{blog.title}' created successfully!"}
        except SQLAlchemyError as e:
            db.rollback()
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Something went wrong")

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Author {blog.author} not found!")

""" UPDATE Blog """

@router.put('/update/{blog_id}')
async def update_blog(blog_id:str,blog:UpdateBlog, current_user:LoginUser = Depends(get_current_user),db:Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user.email).first()
    existing_blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not existing_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    if existing_blog.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this blog")

    if blog.title:
        existing_blog.title = blog.title
    if blog.content:
        existing_blog.content = blog.content

    existing_blog.updated_at = datetime.now()
    try:
        db.commit()
        return {"message": f"Blog '{existing_blog.title}' updated successfully!"}
    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")

""" DELETE Blog """

@router.delete('/delete/{blog_id}')
async def delete_blog(blog_id:str, db:Session = Depends(get_db), current_user:LoginUser = Depends(get_current_user)):
    user = db.query(User).filter(User.email == current_user.email).first()
    existing_blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not existing_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    
    if existing_blog.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this blog")
    
    db.query(Blog).filter(Blog.author_id == user.id).where(Blog.id == blog_id).delete()
    
    try:
        db.commit()
        return {"message": f"Blog '{existing_blog.title}' deleted successfully!"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Something went wrong!")
