from fastapi import FastAPI, status, HTTPException, Depends
from src.config import Base, engine, SessionLocal
from src.schemas import UserSchema, UserLoginSchema, TokenSchema
# from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from src.models import User
from sqlalchemy.orm import Session
from src.utils import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_refresh_token,
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

@app.get("/")
def greet():
    return {"message": "hi"}

@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/clear_users")
async def clear_users(db: Session = Depends(get_db)):
    db.query(User).delete()
    db.commit()
    return {"result": "all users deleted"}

@app.post("/users")
async def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/signup")
async def signup(db: Session = Depends(get_db), user_data: UserSchema = None):
    user = db.query(User).filter_by(email=user_data.email).first()
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

@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(db: Session = Depends(get_db), user_data: UserLoginSchema = None):
    user = db.query(User).filter_by(email=user_data.email).first()
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
    return {
        # "access_token": create_access_token(user.email),
        "access_token": create_access_token("asdas"),
        "refresh_token": create_refresh_token(user.email),
    }

@app.get("/test", dependencies=[Depends(JWTBearer())])
async def get_me():
    return {"data": "sads"}
