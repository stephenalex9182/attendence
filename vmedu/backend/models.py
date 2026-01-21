from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Table
from sqlalchemy.orm import relationship
from .database import Base

enrollment = Table(
    "enrollment",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("users.id")),
    Column("course_id", Integer, ForeignKey("courses.id"))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # "student" or "faculty"
    roll_number = Column(String, unique=True, nullable=True) # Only for students

    attendances = relationship("Attendance", back_populates="student")
    courses = relationship("Course", secondary=enrollment, back_populates="students")
    courses_taught = relationship("Course", back_populates="faculty")

    # For easy access to enrolled courses as a list of IDs or similar?
    # relationship handles it.

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, index=True)
    faculty_id = Column(Integer, ForeignKey("users.id"))

    faculty = relationship("User", back_populates="courses_taught")
    students = relationship("User", secondary=enrollment, back_populates="courses")
    attendances = relationship("Attendance", back_populates="course")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True) # Nullable for migration safety or general attendance
    date = Column(Date, index=True)
    status = Column(String) # "present", "absent"
    locked = Column(Boolean, default=True) 

    student = relationship("User", back_populates="attendances")
    course = relationship("Course", back_populates="attendances")
