from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime
from core.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    about = Column(String)
    image = Column(String)
    registered_at = Column(DateTime, default=datetime.now)
    publication_id = Column(UUID(as_uuid=True), ForeignKey('publication.id', use_alter=True, name='fk_publication_id'), nullable=True)

    blogs = relationship("Blog", backref="author")
    comments = relationship("Comment", backref="user")
    bookmarks = relationship("Bookmark", backref="user")
    likes = relationship("Like", backref="user")
    history = relationship("History", backref="user")
    following = relationship('Follow', foreign_keys='Follow.follower_id', backref="follower")
    followers = relationship('Follow', foreign_keys='Follow.following_id', backref="following")
    user_publications = relationship("Publication", foreign_keys=[publication_id], backref="user_publication")


class Publication(Base):
    __tablename__ = 'publication'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    image = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    views = Column(Integer, default=0)
    blogs_count = Column(Integer, default=0)
    followers_count = Column(Integer, default=0)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    user = relationship("User",foreign_keys=[user_id], backref=backref("publications_list", foreign_keys=[user_id], post_update=True))
    blogs = relationship("Blog", backref="publication")


class Blog(Base):
    __tablename__ = 'blogs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    likes_count = Column(Integer, default=0)
    read_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.now)
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    publication_id = Column(UUID(as_uuid=True), ForeignKey('publication.id'), nullable=False)

    comments = relationship("Comment", backref="blog")
    bookmarks = relationship("Bookmark", backref="blog")
    likes = relationship("Like", backref="blog")
    history = relationship("History", backref="blog")


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    blog_id = Column(UUID(as_uuid=True), ForeignKey('blogs.id'), nullable=False)


class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    blog_id = Column(UUID(as_uuid=True), ForeignKey('blogs.id'), nullable=False)
    marked_at = Column(DateTime, default=datetime.now)


class Like(Base):
    __tablename__ = 'likes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    blog_id = Column(UUID(as_uuid=True), ForeignKey('blogs.id'), nullable=False)


class History(Base):
    __tablename__ = 'history'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    read_at = Column(DateTime, default=datetime.now)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    blog_id = Column(UUID(as_uuid=True), ForeignKey('blogs.id'), nullable=False)


class Follow(Base):
    __tablename__ = 'follow'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    following_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)



