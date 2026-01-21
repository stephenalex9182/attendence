from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import database, schemas, models, auth, deps

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/add", response_model=schemas.User, dependencies=[Depends(deps.get_current_faculty)])
def create_student(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email, 
        hashed_password=hashed_password, 
        role="student", # Enforce student role for this endpoint or allow param
        roll_number=user.roll_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/students", response_model=List[schemas.User], dependencies=[Depends(deps.get_current_faculty)])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    users = db.query(models.User).filter(models.User.role == "student").offset(skip).limit(limit).all()
    return users

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user

