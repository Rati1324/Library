from fastapi import FastAPI, HTTPException, Depends
from src.config import Base, engine, SessionLocal
from src.schemas import UserSchema
import src.models as models
from sqlalchemy.orm import Session

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
    return db.query(models.User).all()

@app.post("/users")
async def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = models.User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user