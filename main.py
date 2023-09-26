from fastapi import FastAPI, HTTPException, Depends
from src.config import Base, engine, SessionLocal
from src.schemas import UserSchema
from src.models import User
from sqlalchemy.orm import Session
from src.utils import get_hashed_password

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

@app.post("/users")
async def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/signup")
async def signup(db: Session = Depends(get_db), user_data: UserSchema = None):
    # find user in the db based on user_data.email
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
