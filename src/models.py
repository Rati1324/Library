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
    borrowings_books = relationship("Borrowing", backref="borrow_requester", foreign_keys="Borrowing.requester_id")

class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    location = Column(String)
    condition = Column(String)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    author_id = Column(Integer, ForeignKey('author.id'))
    giving_away = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=True)

    giveaway_books = relationship("Giveaway", backref="book", foreign_keys="Giveaway.book_id")

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

class Giveaway(Base):
    __tablename__ = "borrowing"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('book.id'))
    requester_id = Column(Integer, ForeignKey('user.id'))