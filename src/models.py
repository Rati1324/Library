from sqlalchemy import  Column, Integer, String
from .config import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    book_id = Column(Integer, ForeignKey('book.id'))

# make a model for the book table
class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
 