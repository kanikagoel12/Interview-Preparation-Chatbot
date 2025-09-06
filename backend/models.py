from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class InterviewSession(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True)
    domain = Column(String)
    mode = Column(String)
    question = Column(Text)
    answer = Column(Text)
    score = Column(Float)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

# Create tables automatically
init_db()
