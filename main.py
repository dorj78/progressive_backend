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
    user_id = Column(Integer, primary_key=True)  # Fixed: Removed server_default
    account_name = Column(String(50), unique=True, nullable=False)
    user_password = Column(String(50), nullable=False)
    surname = Column(String(100), nullable=False)
    firstname = Column(String(100), nullable=False)
    gender = Column(String(30), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    registerid = Column(String(12), unique=True, nullable=False)
    country = Column(String(50), nullable=True)

class Isma(Base):
    __tablename__ = "isma_web"
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

class Insomnia(Base):
    __tablename__ = "insomnia_web"
    insomnia_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    fall_asleep = Column(Integer)
    stay_asleep = Column(Integer)
    early_rising = Column(Integer)
    sleep_satisfaction = Column(Integer)
    daily_impact = Column(Integer)
    life_quality = Column(Integer)
    sleep_concern = Column(Integer)
    total_sum = Column(Integer)
    question_mn = Column(String)

class Fatigue(Base):
    __tablename__ = "fatigue"
    fatigue_id = Column(Integer, primary_key=True)  # Fixed from insomnia_id
    user_id = Column(Integer, nullable=False)
    sleep_disorder = Column(Integer)
    waking_fatigue = Column(Integer)
    focus_issue = Column(Integer)
    muscle_pain = Column(Integer)
    body_pain = Column(Integer)
    head_pain = Column(Integer)
    neck_shoulder_stiffness = Column(Integer)
    throat_pain = Column(Integer)
    motion_dizziness = Column(Integer)
    exercise_fatigue = Column(Integer)
    eye_sensitivity = Column(Integer)
    numb_sensation = Column(Integer)
    anxiety_issue = Column(Integer)
    restless_sleep = Column(Integer)
    cold_sensitivity = Column(Integer)
    stomach_upset = Column(Integer)
    allergic_reaction = Column(Integer)
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
ISMA_QUESTIONS = [
    "sleep_enough", "appetite_change", "guilt_feeling", "overthinking",
    "focus_memory", "no_hobby_time", "muscle_pain", "addiction",
    "work_at_home", "enough_time", "ignore_problems", "perfectionist",
    "bad_time_estimate", "overwhelmed", "low_self_esteem", "impatient",
    "hurried", "road_rage", "competitive", "critical", "distracted",
    "low_libido", "teeth_grinding", "performance_drop"
]

INSOMNIA_QUESTIONS = [
    "Fall Asleep", "Stay Asleep", "Early Rising", "Sleep Satisfaction",
    "Daily Impact", "Life Quality", "Sleep Concern"
]

FATIGUE_QUESTIONS = [
    "Sleep Disorder", "Waking Fatigue", "Focus Issue", "Muscle Pain",
    "Body Pain", "Head Pain", "Neck Shoulder Stiffness", "Throat Pain",
    "Motion Dizziness", "Exercise Fatigue", "Eye Sensitivity", "Numb Sensation",
    "Anxiety Issue", "Restless Sleep", "Cold Sensitivity", "Stomach Upset",
    "Allergic Reaction"
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
@app.post("/survey/isma")
async def submit_isma_survey(submission: SurveySubmission, db: Session = Depends(get_db)):
    # Validate that all expected questions are present and no extras
    if set(ISMA_QUESTIONS) != set(submission.responses.keys()):
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
    isma_data = {q: submission.responses[q] for q in ISMA_QUESTIONS}
    isma_data["user_id"] = submission.user_idisma_data
    isma_data["total_sum"] = total_sum
    isma_data["question_mn"] = question_mn
    
    # Insert into Isma table
    new_isma = Isma(**isma_data)
    db.add(new_isma)
    db.commit()
    db.refresh(new_isma)
    
    # Return question_mn to frontend
    return {"question_mn": question_mn}

@app.post("/survey/insomnia")
async def submit_insomnia_survey(submission: SurveySubmission, db: Session = Depends(get_db)):
    # Validate that all expected questions are present and no extras
    if set(INSOMNIA_QUESTIONS) != set(submission.responses.keys()):
        raise HTTPException(status_code=400, detail="Missing or extra questions in submission")
    
    # Calculate total sum of responses
    total_sum = sum(submission.responses.values())

    # Determine question_mn based on total_sum
    if total_sum < 8:
        question_mn = "Нойргүйдэл байхгүй"
    elif total_sum < 15:
        question_mn = "Нойргүйдлийн зэрэг бага"
    elif total_sum < 22:
        question_mn = "Дунд зэргийн нойргүйдэлтэй"
    else:
        question_mn = "Нойргүйдлийн зэрэг хүнд явцтай"
    
    # Prepare data for Isma model with individual responses
    insomnia_data = {
        q.replace(" ", "_").lower(): submission.responses[q] 
        for q in INSOMNIA_QUESTIONS
    }
    insomnia_data["user_id"] = submission.user_id
    insomnia_data["total_sum"] = total_sum
    insomnia_data["question_mn"] = question_mn
    
    # Insert into Isma table
    new_insomnia = Insomnia(**insomnia_data)
    db.add(new_insomnia)
    db.commit()
    db.refresh(new_insomnia)
    
    # Return question_mn to frontend
    return {"question_mn": question_mn}

@app.post("/survey/fatigue")
async def submit_fatigue_survey(submission: SurveySubmission, db: Session = Depends(get_db)):
    if set(FATIGUE_QUESTIONS) != set(submission.responses.keys()):
        raise HTTPException(status_code=400, detail="Missing or extra questions in Fatigue submission")
    
    total_sum = sum(submission.responses.values())
    if total_sum <= 10:
        question_mn = "Архаг ядаргаатай"
    elif total_sum <= 24:
        question_mn = "Бага зэргийн архаг ядаргаатай"
    elif total_sum <= 51:
        question_mn = "Дунд зэргийн архаг ядаргаатай"
    else:
        question_mn = "Хүнд зэргийн архаг ядаргаатай"
    
    # Transform keys to match Fatigue model columns
    fatigue_data = {q.replace(" ", "_").lower(): submission.responses[q] for q in FATIGUE_QUESTIONS}
    fatigue_data["user_id"] = submission.user_id
    fatigue_data["total_sum"] = total_sum
    fatigue_data["question_mn"] = question_mn
    
    # Use the Fatigue model
    new_fatigue = Fatigue(**fatigue_data)
    db.add(new_fatigue)
    db.commit()
    db.refresh(new_fatigue)
    
    return {"question_mn": question_mn}