# Part 1
from http.client import HTTPException
import os
from dotenv import load_dotenv


load_dotenv()
Database_url=os.getenv("DATABASE_URL")
print(Database_url)

# Part 2 
from sqlalchemy import create_engine,text

engine =create_engine(Database_url)
with engine.connect() as conn:
    version=conn.execute(text("SELECT version()")).scalar()
    print(f"Connected to {version.split(',')[0]}")

# Part 3

from sqlalchemy.orm import Query, declarative_base,sessionmaker

SessionLocal=sessionmaker(bind=engine)
dv=SessionLocal()
Base = declarative_base()


# Part 4
from sqlalchemy import Column,String,Integer,Float
from pydantic import field_validator
class StudentDB(Base):

    __tablename__ = "student_records"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    email = Column(String, unique=True)
    course = Column(String)
    marks = Column(Float)

Base.metadata.create_all(bind=engine)
print("Table ready...")


# Part 5
from pydantic import BaseModel, EmailStr,Field,computed_field,ConfigDict
from fastapi import Depends, HTTPException, Path, Query

class StudentCreate(BaseModel):
    id:str=Field(..., description="Student ID")
    name:str=Field(..., min_length=2,max_length=50,description="Student Name")
    age:int=Field(...,ge=0,le=100,description="Student Age")
    email:EmailStr=Field(..., description="Student Email")
    course:str=Field(..., description="Student Course")
    marks:float=Field(..., ge=0, le=100, description="Student Marks")

    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        return value.title()


class StudentUpdate(BaseModel):
    id :str | None=Field(None, description="Student ID")
    name:str | None=Field(None, min_length=2,max_length=50,description="Student Name")
    age:int | None=Field(None,ge=0,le=100,description="Student Age")
    email:EmailStr | None=Field(None, description="Student Email") 
    course:str | None=Field(None, description="Student Course")
    marks:float | None=Field(None, ge=0, le=100, description="Student Marks")


    
    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        return value.title()

# Part 6
class StudentResponse(StudentCreate):

    model_config=ConfigDict(from_attributes=True) #this is used to tell pydantic that the data is coming from a database model and not from a dictionary    
    @computed_field
    @property
    def grade(self)->str:
        if self.marks>=90:
            return "A"
        elif self.marks>=80:
            return "B"
        elif self.marks>=70:
            return "C"
        elif self.marks>=60:
            return "D"
        else:
            return "F"



# Part 7
def get_db():
    db=SessionLocal()
    try:
        yield db   #opens a session pauses at yield while the endpoint doest its work and once the endpoint completed it's work the session will closed
    
    finally:
        db.close() 


# Part 8
from fastapi import FastAPI

app=FastAPI()

# Part 9
from sqlalchemy.orm import Session

@app.get("/student/{student_id}", response_model=StudentResponse)
def get_student(
    student_id:str =Path(..., description="Student ID"),
    db:Session=Depends(get_db)): #Depends(get_db) means: "before running this endpoint, run the get_db() function and give me what it returns"

    student=db.get(StudentDB, student_id) #select ...where id=
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# Part 10
@app.post("/students", response_model=StudentResponse, tags=["POST ROUTES"])
def create_student(
    student:StudentCreate,
    db:Session=Depends(get_db)):

    if db.get(StudentDB, student.id) is not None:
        raise HTTPException(status_code=400, detail="Student already exists")
    
    new_student=StudentDB(**student.model_dump()) #model_dump() converts the pydantic model to a dictionary
    db.add(new_student)

    try:
        db.commit()
    except Exception as e:
        db.rollback() #rollback the transaction if there is an error
        raise HTTPException(status_code=400, detail=str(e))
        

    db.refresh(new_student) #refresh the new_student object with the data from the database
    return new_student

# Part 11
@app.put("/student/{student_id}", response_model=StudentResponse, tags=["PUT ROUTES"])
def update_student(student_update:StudentUpdate,
    student_id:str=Path(..., description="Student ID"),
    db:Session=Depends(get_db)):

    existing_student=db.get(StudentDB, student_id)
    if existing_student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    changes=student_update.model_dump(exclude_unset=True) #exclude_unset=True means: "only include the fields that were provided in the request body"
    for key, value in changes.items():
        setattr(existing_student, key, value) #setattr(object, attribute, value) is used to set the value of an attribute of an object
    
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    db.refresh(existing_student)
    return existing_student

# Part 12
@app.delete("/student/{student_id}", tags=["DELETE ROUTES"])
def delete_student(student_id:str=Path(..., description="Student ID"),
    db:Session=Depends(get_db)):

    existing_student=db.get(StudentDB, student_id)
    if existing_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(existing_student)
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Student deleted successfully"}

# Part 13
Sort_field = ["id", "name", "age", "email", "course", "marks"]
Sort_order = ["asc", "desc"]


# PART 13: FILTER + SORT + PAGINATION

Sort_field = ["id", "name", "age", "email", "course", "marks"]
Sort_order = ["asc", "desc"]


@app.get("/students",tags=["GET ROUTES"])
def get_all(
    course: str = Query(None, description="Filter by course"),
    sort_by: str = Query("id", description="Sort by field"),
    order: str = Query("asc", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
    db: Session = Depends(get_db)
):

    # 1. VALIDATE SORT FIELD
    if sort_by not in Sort_field:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort field. Must be one of {Sort_field}"
        )

    # 2. VALIDATE SORT ORDER
    if order not in Sort_order:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort order. Must be one of {Sort_order}"
        )

    # 3. CREATE QUERY
    query = db.query(StudentDB)

    # 4. FILTER BY COURSE
    if course:
        query = query.filter(StudentDB.course == course)

    # 5. SORT RECORDS
    sort_column = getattr(StudentDB, sort_by)

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # 6. TOTAL RECORDS
    total = query.count()

    # 7. PAGINATION
    start = (page - 1) * limit

    students = query.offset(start).limit(limit).all()

    # 8. RETURN RESPONSE
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "students": students
    }