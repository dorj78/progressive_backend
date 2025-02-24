from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Dict
import os
from os.path import join, dirname
from dotenv import load_dotenv

# Load environment variables
try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print(f"Environment not found: {e}")

# Database Connection
try:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
except Exception as e:
    print(f"Database not connected: {e}")

# Define DB Models
Base = declarative_base()

class User(Base):
    __tablename__ = "user_information"
    user_id = Column(Integer, primary_key=True, server_default="nextval('user_information_user_id_seq'::regclass)")
    account_name = Column(String(50), unique=True, nullable=False)
    user_password = Column(String(50), nullable=False)
    surname = Column(String(100), nullable=False)
    firstname = Column(String(100), nullable=False)
    gender = Column(String(30), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    registerid = Column(String(12), unique=True, nullable=False)
    country = Column(String(50), nullable=True)

class Isma(Base):
    __tablename__ = "isma"
    isma_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    sleep_enough = Column(Integer)
    appetite_change = Column(Integer)
    guilt_feeling = Column(Integer)
    overthinking = Column(Integer)
    focus_memory = Column(Integer)
    no_hobby_time = Column(Integer)
    muscle_pain = Column(Integer)
    addiction = Column(Integer)
    work_at_home = Column(Integer)
    enough_time = Column(Integer)
    ignore_problems = Column(Integer)
    perfectionist = Column(Integer)
    bad_time_estimate = Column(Integer)
    overwhelmed = Column(Integer)
    low_self_esteem = Column(Integer)
    impatient = Column(Integer)
    hurried = Column(Integer)
    road_rage = Column(Integer)
    competitive = Column(Integer)
    critical = Column(Integer)
    distracted = Column(Integer)
    low_libido = Column(Integer)
    teeth_grinding = Column(Integer)
    performance_drop = Column(Integer)
    total_sum = Column(Integer)
    question_mn = Column(String)

# Create all tables
Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schema for User Creation
class UserCreate(BaseModel):
    username: str
    password: str
    last_name: str
    first_name: str
    gender: str
    email: str
    registry_number: str
    country: str | None

# Pydantic Schema for Survey Submission
class SurveySubmission(BaseModel):
    responses: Dict[str, int]  # e.g., {"sleep_enough": 1, "appetite_change": 0}
    user_id: int

# Constant list of question IDs
QUESTIONS = [
    "sleep_enough", "appetite_change", "guilt_feeling", "overthinking",
    "focus_memory", "no_hobby_time", "muscle_pain", "addiction",
    "work_at_home", "enough_time", "ignore_problems", "perfectionist",
    "bad_time_estimate", "overwhelmed", "low_self_esteem", "impatient",
    "hurried", "road_rage", "competitive", "critical", "distracted",
    "low_libido", "teeth_grinding", "performance_drop"
]

# POST endpoint to create a user
@app.post("/users/", response_model=UserCreate)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check for existing username, email, or registerid
    if db.query(User).filter(User.account_name == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.registerid == user.registry_number).first():
        raise HTTPException(status_code=400, detail="Register ID already registered")
    
    new_user = User(
        account_name=user.username,
        user_password=user.password,
        surname=user.last_name,
        firstname=user.first_name,
        gender=user.gender,
        email=user.email,
        registerid=user.registry_number,
        country=user.country if user.country else None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return user

# GET endpoint to fetch all users
@app.get("/users/")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# POST endpoint to submit survey
@app.post("/survey/submit")
async def submit_survey(submission: SurveySubmission, db: Session = Depends(get_db)):
    # Validate that all expected questions are present and no extras
    if set(QUESTIONS) != set(submission.responses.keys()):
        raise HTTPException(status_code=400, detail="Missing or extra questions in submission")
    
    # Calculate total sum of responses
    total_sum = sum(submission.responses.values())
    
    # Determine question_mn based on total_sum
    if total_sum <= 5:
        question_mn = "Стрессээр өвчлөх магадлал бага"
    elif total_sum <= 10:
        question_mn = "Стрессээр өвчлөх магадлал өндөр"
    else:
        question_mn = "Стрессийн түвшин маш өндөр байна"
    
    # Prepare data for Isma model with individual responses
    isma_data = {q: submission.responses[q] for q in QUESTIONS}
    isma_data["user_id"] = submission.user_id
    isma_data["total_sum"] = total_sum
    isma_data["question_mn"] = question_mn
    
    # Insert into Isma table
    new_isma = Isma(**isma_data)
    db.add(new_isma)
    db.commit()
    db.refresh(new_isma)
    
    # Return question_mn to frontend
    return {"question_mn": question_mn}