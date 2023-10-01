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

class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    condition = Column(String)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    author_id = Column(Integer, ForeignKey('author.id'))
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=True)

    bookRequest_books = relationship("BookRequest", backref="book", foreign_keys="BookRequest.book_id")

class Genre(Base):
    __tablename__ = "genre"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    books = relationship("Book", backref="genre")

class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    books = relationship("Book", backref="author")

class BookRequest(Base):
    __tablename__ = "bookRequest"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('book.id'))
    requester_id = Column(Integer, ForeignKey('user.id'))
    location = Column(String)
    accepted = Column(Boolean, default=False)