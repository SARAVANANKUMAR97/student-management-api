
from dotenv import load_dotenv
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Integer, Float

load_dotenv()

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)

engine = create_engine(DATABASE_URL)

# Test connection
with engine.connect() as conn:
    version = conn.execute(text("SELECT version()"))
    print(f"Connected to {version.scalar()}")


# Student Model
class StudentDB(Base):

    __tablename__ = "student_records"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    email = Column(String, unique=True)
    course = Column(String)
    marks = Column(Float)


# Create table AFTER defining the model
Base.metadata.create_all(bind=engine)

print("Table ready...")


# Create Session
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

try:
    if db.get(StudentDB, "S001") is None:

        db.add(StudentDB(
            id="S001",
            name="Arun Kumar",
            age=21,
            email="arun@gmail.com",
            course="Computer Engineering",
            marks=85.5
        ))

        db.commit()
        print("Student inserted successfully!")

    # Fetch all students
    for i in db.query(StudentDB).all():
        print(i.id, i.name, i.age, i.marks)

finally:
    db.close()


#update 
aarav=db.get(StudentDB,"S001") #arrav==(id=S001,name="Aarav")
aarav.age=23

db.commit()


'''
DeclarativeBase-> SQLAlchemy paraent class that gives "table powers" 
we make our own Base once and every table inherits from it.
Basae:gives table Powers
'''
class Base(DeclarativeBase):
    pass

