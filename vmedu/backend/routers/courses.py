from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import database, schemas, models, deps

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
)

@router.post("/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_faculty)):
    # Check if course code exists
    db_course = db.query(models.Course).filter(models.Course.code == course.code).first()
    if db_course:
        raise HTTPException(status_code=400, detail="Course code already registered")
    
    new_course = models.Course(**course.dict(), faculty_id=current_user.id)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/my", response_model=List[schemas.Course])
def read_my_courses(db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    if current_user.role == "faculty":
        return db.query(models.Course).filter(models.Course.faculty_id == current_user.id).all()
    else:
        # For students, return enrolled courses
        return current_user.courses

@router.get("/", response_model=List[schemas.Course])
def read_all_courses(db: Session = Depends(deps.get_db), current_user=Depends(deps.get_current_user)):
     return db.query(models.Course).all()

@router.post("/{course_id}/enroll", response_model=schemas.User)
def enroll_student(course_id: int, student_email: str, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_faculty)):
    # Get Course making sure it belongs to faculty
    course = db.query(models.Course).filter(models.Course.id == course_id, models.Course.faculty_id == current_user.id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found or not authorized")
    
    # Get Student
    student = db.query(models.User).filter(models.User.email == student_email, models.User.role == "student").first()
    if not student:
         raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if already enrolled
    if student in course.students:
        return student # Idempotent

    course.students.append(student)
    db.commit()
    return student

@router.get("/{course_id}/students", response_model=List[schemas.User])
def get_course_students(course_id: int, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_faculty)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    # Authorization verify? 
    if course.faculty_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized")
    
    return course.students
