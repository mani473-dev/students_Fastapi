from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Query,
    Path,
    status,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Student REST API",
    version="1.0.0",
    description="FastAPI Practice Project with Basic Authentication"
)

# ----------------------------------------------------
# Basic Authentication
# ----------------------------------------------------

security = HTTPBasic()

API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username_ok = secrets.compare_digest(
        credentials.username,
        API_USERNAME
    )

    password_ok = secrets.compare_digest(
        credentials.password,
        API_PASSWORD
    )

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Basic"
            }
        )

    return credentials.username


# ----------------------------------------------------
# Pydantic Model
# ----------------------------------------------------

class Student(BaseModel):
    id: int
    name: str = Field(..., min_length=3, max_length=30)
    age: int = Field(..., gt=0, lt=100)
    course: str


# ----------------------------------------------------
# Fake Database
# ----------------------------------------------------

students = [
    {
        "id": 1,
        "name": "John",
        "age": 22,
        "course": "Python"
    },
    {
        "id": 2,
        "name": "Alice",
        "age": 20,
        "course": "FastAPI"
    }
]


# ----------------------------------------------------
# Home
# ----------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to FastAPI Demo"
    }


# ----------------------------------------------------
# Get All Students
# ----------------------------------------------------

@app.get("/students")
def get_students(
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    user: str = Depends(authenticate)
):
    return {
        "logged_in_user": user,
        "students": students[skip: skip + limit]
    }


# ----------------------------------------------------
# Get Student By ID
# ----------------------------------------------------

@app.get("/students/{student_id}")
def get_student(
    student_id: int = Path(..., gt=0),
    user: str = Depends(authenticate)
):
    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )


# ----------------------------------------------------
# Create Student
# ----------------------------------------------------

@app.post("/students", status_code=201)
def create_student(
    student: Student,
    user: str = Depends(authenticate)
):

    for s in students:
        if s["id"] == student.id:
            raise HTTPException(
                status_code=400,
                detail="Student ID already exists"
            )

    students.append(student.model_dump())

    return {
        "message": "Student Created",
        "student": student
    }


# ----------------------------------------------------
# Update Student
# ----------------------------------------------------

@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    updated_student: Student,
    user: str = Depends(authenticate)
):

    for index, student in enumerate(students):
        if student["id"] == student_id:
            students[index] = updated_student.model_dump()

            return {
                "message": "Student Updated",
                "student": updated_student
            }

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )


# ----------------------------------------------------
# Delete Student
# ----------------------------------------------------

@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    user: str = Depends(authenticate)
):

    for index, student in enumerate(students):
        if student["id"] == student_id:
            students.pop(index)

            return {
                "message": "Student Deleted"
            }

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )