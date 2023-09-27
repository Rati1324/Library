from sqlalchemy import  Column, ForeignKey, Integer, String, Boolean 
from sqlalchemy.orm import relationship
from .config import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)

    owner_books = relationship("Book", backref="owner", foreign_keys="Book.owner_id")
    borrower_books = relationship("Book", backref="borrower",foreign_keys="Book.borrower_id")

class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    conditon = Column(String)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    author_id = Column(Integer, ForeignKey('author.id'))
    for_borrow = Column(Boolean)
    owner_id = Column(Integer, ForeignKey('user.id'))
    borrower_id = Column(Integer, ForeignKey('user.id'))

class Genre(Base):
    __tablename__ = "genre"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    books = relationship("Book", backref="genre")

class author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    books = relationship("Book", backref="author")