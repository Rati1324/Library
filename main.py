from fastapi import FastAPI, status, HTTPException, Depends, Request
from src.config import Base, engine, SessionLocal
from src.schemas import UserSchema, UserLoginSchema, TokenSchema, BookSchema, BookRequestSchema, Token
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from src.models import User, Genre, Book, Author, BookRequest
from sqlalchemy.orm import Session
from datetime import timedelta
from decouple import config
from src.utils import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_jwt,
    get_current_user,
    oauth_2_scheme, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    JWT_SECRET_KEY,
    JWT_REFRESH_SECRET_KEY
)
from src.jwt_bearer import JWTBearer
from src.config import get_db

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# @app.get("/clear_users")
# async def clear_users(db: Session = Depends(get_db)):
#     db.query(User).delete()
#     db.commit()
#     return {"result": "all users deleted"}

@app.post("/signup")
async def signup(db: Session = Depends(get_db), user_data: UserSchema = None):
    user = db.query(User).filter(User.username==user_data.username).first()

    if user is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        username=user_data.username, 
        email=user_data.email, 
        password=get_hashed_password(user_data.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"result": "user successfully created"}

@app.post("/login", response_model=Token)
async def login(db: Session = Depends(get_db), user_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter_by(username=user_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.password
    if not verify_password(user_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}

# write an endpont for getting all books
@app.get("/books")
async def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()

async def check_existing_rows(db: Session, table, value):
    row = db.query(table).filter_by(name=value).first()
    if row is None:
        row = table(name=value)
        db.add(row)
        db.commit()
        db.refresh(row)
        row_id = row.id
    else:
        row_id = row.id
    print(row)
    return row_id

# @app.post("/book", dependencies=[Depends(JWTBearer())])
@app.post("/book")
async def insert_book(db: Session = Depends(get_db), dependencies = Depends(get_current_user), book_data: BookSchema = None):
    current_user = db.query(User).filter_by(username=dependencies.username).first().id
    genre_id = await check_existing_rows(db, Genre, book_data.genre)
    author_id = await check_existing_rows(db, Author, book_data.author)

    book = Book(
        title=book_data.title,
        condition=book_data.condition,
        genre_id=genre_id,
        author_id=author_id,
        owner_id=current_user,
    )

    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@app.put("/book")
async def edit_book(db: Session = Depends(get_db), dependencies = Depends(get_current_user), book_data: BookSchema = None, book_id: int = None):
    current_user = db.query(User).filter_by(username=dependencies.username).first().id

    # search for book by book id and owner id
    book = db.query(Book).filter_by(id=book_id, owner_id=current_user).first()

    if book is None:
        raise HTTPException(status_code=400, detail="Book not found")

    genre_id = await check_existing_rows(db, Genre, book_data.genre)
    author_id = await check_existing_rows(db, Author, book_data.author)

    book.id = book_id
    book.title = book_data.title
    book.condition = book_data.condition
    book.genre_id = genre_id
    book.author_id = author_id
    book.location = book_data.location

    db.commit()
    db.refresh(book)
    return book

@app.delete("/book")
async def delete_book(db: Session = Depends(get_db), dependencies = Depends(get_current_user), book_id: int = None):
    current_user = db.query(User).filter_by(username=dependencies.username).first().id

    book = db.query(Book).filter_by(id=book_id, owner_id=current_user).first()
    if book is None:
        raise HTTPException(status_code=400, detail="Book not found")

    db.delete(book)
    db.commit()
    return {"result": "book deleted"}

@app.post("/request_book")
async def request_book(book_request: BookRequestSchema, db: Session = Depends(get_db), dependencies = Depends(get_current_user)):
    current_user = db.query(User).filter_by(username=dependencies.username).first().id
    book_id = book_request.book_id

    check_book = db.query(Book).filter_by(id=book_id, owner_id=current_user).first()
    if check_book:
        raise HTTPException(status_code=400, detail="You can't request your own book")

    check_book = db.query(BookRequest).filter_by(book_id=book_id, requester_id=current_user).first()
    if check_book:
        raise HTTPException(status_code=400, detail="You already requested this book")

    request = BookRequest(
        book_id=book_id,
        requester_id=current_user,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return {"result": "book requested"}

@app.get("/requests", tags=["Requests for my books"])
async def get_requests(db: Session = Depends(get_db), dependencies = Depends(get_current_user)):
    current_user = db.query(User).filter_by(username=dependencies.username).first().id

    # get all requests from the BookRequest table that have books that the current user owns
    requests = db.query(BookRequest).join(Book).filter(Book.owner_id==current_user).all()
    return {"requests": requests}

@app.get("/my_requests", tags=["Requests that I've sent"])
async def get_my_requests(db: Session = Depends(get_db), dependencies = Depends(get_current_user)):
    current_user = db.query(User).filter_by(username=dependencies.username).first().id

    requests = db.query(BookRequest).filter(BookRequest.requester_id==current_user).all()
    return {"data": requests}

@app.put("/accept_request")
async def accept_request(request_id: int, db: Session = Depends(get_db), dependencies = Depends(get_current_user)):
    current_user = db.query(User).filter_by(username=dependencies.username).first().id

    # search for request with request id and owner id, you need to join book to get the owner id
    request = db.query(BookRequest).join(Book).filter(Book.owner_id==current_user, BookRequest.id==request_id).first()
    if request is None:
        raise HTTPException(status_code=400, detail="Request not found")

    request.accepted = True
    db.commit()

    db.query(BookRequest).filter(BookRequest.book_id==request.book_id, BookRequest.accepted==False).delete()
    # db.commit()
    return {"result": "request accepted"}

# @app.post("/test", dependencies=[Depends(get_current_user)])
# async def get_me(user: dict):
#     return {"data": user}