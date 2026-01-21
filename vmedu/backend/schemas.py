from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: str
    roll_number: Optional[str] = None

class User(UserBase):
    id: int
    role: str
    roll_number: Optional[str] = None
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    # id: Optional[int] = None # Useful to have

class CourseBase(BaseModel):
    name: str
    code: str

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    faculty_id: int
    
    class Config:
        orm_mode = True

class AttendanceBase(BaseModel):
    date: date
    status: str
    course_id: Optional[int] = None # Optional for backward compatibility or general

class AttendanceCreate(AttendanceBase):
    student_id: int

class Attendance(AttendanceBase):
    id: int
    student_id: int
    locked: bool

    class Config:
        orm_mode = True
