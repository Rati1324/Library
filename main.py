from fastapi import FastAPI, status, HTTPException, Depends, Request
from src.config import Base, engine, SessionLocal
from src.schemas import UserSchema, UserLoginSchema, TokenSchema, BookSchema, GiveawaySchema, Token, EditBookSchema
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from src.models import User, Genre, Book, Author, Giveaway
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

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/clear_users")
async def clear_users(db: Session = Depends(get_db)):
    db.query(User).delete()
    db.commit()
    return {"result": "all users deleted"}

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
    genre_id = await check_existing_rows(db, Genre, book_data.genre)
    author_id = await check_existing_rows(db, Author, book_data.author)

    current_user = db.query(User).filter_by(username=dependencies.username).first().id

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

# endpoint for editing book, send all data in the body
@app.put("/book")
async def edit_book(db: Session = Depends(get_db), dependencies = Depends(get_current_user), book_data: EditBookSchema = None):
    current_user = db.query(User).filter_by(username=dependencies.username).first().id

    book = db.query(Book).filter_by(owner_id=current_user).first()
    if book is None:
        raise HTTPException(status_code=400, detail="Book not found")

    book = Book(
        title=book_data.title,
        condition=book_data.condition,
        genre_id=book_data.genre,
        author_id=book_data.author,
        owner_id=current_user,
    )

    db.commit()
    db.refresh(book)
    return book

@app.post("/request_book", dependencies = [Depends(get_current_user)])
async def request_borrow(book_request: GiveawaySchema, db: Session = Depends(get_db), dependencies = Depends(get_current_user)):
    current_user = db.query(User).filter_by(username=dependencies.username).first().id
    book_id = book_request.book_id

    giveaway = Giveaway(
        book_id=book_id,
        requester_id=current_user,
    )

    db.add(giveaway)
    return giveaway

@app.get("/borrowings")
async def get_borrowings(db: Session = Depends(get_db), dependencies = Depends(get_current_user)):
    decoded_token = decode_jwt(dependencies)
    current_user = db.query(User).filter_by(email=decoded_token["sub"]).first().id

    # find books that the user owns that are also in the borrowings table
    borrowings = db.query(Book).filter_by(owner_id=current_user).join(Giveaway).all()
    print(borrowings)
    return borrowings


@app.post("/test", dependencies=[Depends(get_current_user)])
async def get_me(user: dict):
    return {"data": user}