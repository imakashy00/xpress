from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Table, create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    about = Column(String)
    image = Column(String)
    publication_id = Column(UUID(as_uuid=True), ForeignKey('publications.id'))
    
    blogs = relationship("Author", backref="user")
    history = relationship("History", backref="user")
    comments = relationship("Comment", backref="user")
    bookmarks = relationship("Bookmark", backref="user")
    liked = relationship("Liked", backref="user")
    followers = relationship('Follow', foreign_keys='Follow.following_id', backref=backref('following', lazy='joined'))
    following = relationship('Follow', foreign_keys='Follow.follower_id', backref=backref('follower', lazy='joined'))

class Publication(Base):
    __tablename__ = 'publications'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    image = Column(String)
    createdAt = Column(DateTime, default=datetime.now())
    views = Column(Integer, default=0)
    subscribers = Column(Integer, default=0)
    
    writers = relationship("User", backref="publication")

class Blog(Base):
    __tablename__ = 'blogs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publication_id = Column(UUID(as_uuid=True), ForeignKey('publications.id'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    publish_at = Column(DateTime, default=datetime.now())
    tags = Column(ARRAY(String))
    
    comments = relationship("Comment", backref="blog")
    bookmarks = relationship("Bookmark", backref="blog")
    history = relationship("History", backref="blog")
    liked = relationship("Liked", backref="blog")
    authors = relationship("Author", backref="blog")


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    blog_id = Column(UUID(as_uuid=True), ForeignKey('blogs.id'), nullable=False)
    content = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.now())


class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blog_id = Column(UUID(as_uuid=True), ForeignKey('blogs.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)


class History(Base):
    __tablename__ = 'history'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    blog_id = Column(UUID(as_uuid=True), ForeignKey('blogs.id'), nullable=False)
    read_at = Column(DateTime, default=datetime.now())



class Liked(Base):
    __tablename__ = 'liked'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    blog_id = Column(UUID(as_uuid=True), ForeignKey('blogs.id'), nullable=False)


class Author(Base):
    __tablename__ = 'authors'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    blog_id = Column(UUID(as_uuid=True), ForeignKey('blogs.id'), nullable=False)


class Follow(Base):
    __tablename__ = 'follows'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    following_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
