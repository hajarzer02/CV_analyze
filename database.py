import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/cvdb")

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database Models
class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    location = Column(Text)
    raw_cv_path = Column(Text)
    extracted_data = Column(Text)  # JSONB as text for SQLite compatibility
    status = Column(Text, default='New')  # New, Interview Scheduled, Offer, Hired, Rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    recommendations = relationship("JobRecommendation", back_populates="candidate")

class JobRecommendation(Base):
    __tablename__ = "job_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    recommendations = Column(Text)  # JSONB as text for SQLite compatibility
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    candidate = relationship("Candidate", back_populates="recommendations")

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
