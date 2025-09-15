from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
from models import Student, StudentCreate, StudentUpdate, StudentResponse
from database import get_database, create_tables
from utils import calculate_gpa, validate_student_age, get_grade_level, calculate_average

app = FastAPI(title="Student Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()

@app.get("/")
def read_root():
    return {"message": "Student Management API", "version": "1.0.0"}

@app.post("/students/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_database)):
    db_student = db.query(Student).filter(Student.email == student.email).first()
    if db_student:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=List[StudentResponse])
def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_database)):
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_database)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_database)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = student_update.dict(exclude_unset=True)
    
    if "email" in update_data:
        existing_student = db.query(Student).filter(
            Student.email == update_data["email"], 
            Student.id != student_id
        ).first()
        if existing_student:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    return student

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_database)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

@app.post("/students/{student_id}/calculate-gpa")
def calculate_student_gpa(student_id: int, scores: List[float], db: Session = Depends(get_database)):
    """計算指定學生的 GPA"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        gpa = calculate_gpa(scores)
        return {
            "student_id": student_id,
            "student_name": student.name,
            "scores": scores,
            "gpa": gpa,
            "total_subjects": len(scores)
        }
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/utils/grade-level/{score}")
def get_student_grade_level(score: float):
    """根據分數獲取等級"""
    try:
        grade_level = get_grade_level(score)
        return {
            "score": score,
            "grade_level": grade_level,
            "description": f"Score {score} corresponds to grade {grade_level}"
        }
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/utils/calculate-average")
def get_average(numbers: List[float]):
    """計算數字列表的平均值"""
    try:
        average = calculate_average(numbers)
        return {
            "numbers": numbers,
            "average": average,
            "count": len(numbers)
        }
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)