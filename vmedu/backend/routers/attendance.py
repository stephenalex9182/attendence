from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from .. import database, schemas, models, deps

router = APIRouter(
    prefix="/attendance",
    tags=["attendance"],
)

# Student Endpoints
@router.get("/my", response_model=List[schemas.Attendance])
def read_own_attendance(course_id: int = None, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    query = db.query(models.Attendance).filter(models.Attendance.student_id == current_user.id)
    if course_id:
        query = query.filter(models.Attendance.course_id == course_id)
    return query.all()

@router.get("/stats")
def read_own_stats(course_id: int = None, db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    query = db.query(models.Attendance).filter(models.Attendance.student_id == current_user.id)
    if course_id:
        query = query.filter(models.Attendance.course_id == course_id)
    
    total = query.count()
    present = query.filter(models.Attendance.status == "present").count()
    absent = total - present
    percentage = (present / total * 100) if total > 0 else 0
    return {"total": total, "present": present, "absent": absent, "percentage": round(percentage, 2)}

# Faculty Endpoints

# ... (omitting batch old version, keeping batch_upsert)

@router.post("/batch_upsert", dependencies=[Depends(deps.get_current_faculty)])
def mark_batch_attendance_upsert(
    attendance_data: List[schemas.AttendanceCreate], 
    db: Session = Depends(deps.get_db)
):
    count = 0
    for item in attendance_data:
        # Check existing based on student + date + course
        # If course_id is None, it's ambiguous if we have multiple courses.
        # But for now, we assume frontend sends course_id.
        
        query = db.query(models.Attendance).filter(
            models.Attendance.student_id == item.student_id,
            models.Attendance.date == item.date
        )
        
        if item.course_id:
            query = query.filter(models.Attendance.course_id == item.course_id)
        else:
            query = query.filter(models.Attendance.course_id == None)

        existing = query.first()

        if existing:
            # Edit allowed
            existing.status = item.status
        else:
            # Create new
            new_record = models.Attendance(
                student_id=item.student_id,
                date=item.date,
                status=item.status,
                course_id=item.course_id,
                locked=True 
            )
            db.add(new_record)
        count += 1
    db.commit()
    return {"message": f"Processed {count} records"}

# ... (unlock mostly same)

@router.get("/by_date", response_model=List[schemas.Attendance], dependencies=[Depends(deps.get_current_faculty)])
def get_attendance_by_date(date: date, course_id: int = None, db: Session = Depends(deps.get_db)):
    query = db.query(models.Attendance).filter(models.Attendance.date == date)
    if course_id:
        query = query.filter(models.Attendance.course_id == course_id)
    return query.all()
