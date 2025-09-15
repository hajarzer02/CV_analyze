from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import json
import shutil
from datetime import datetime

import sys
import os

# Add ai-service to path for llama_service only
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai-service'))

from database import get_db, create_tables, Candidate, JobRecommendation, User
from models import (
    CandidateResponse, 
    CandidateSummary, 
    JobRecommendationResponse, 
    UploadResponse,
    ExtractedCVData,
    StatusUpdateRequest,
    JobMatchRequest,
    JobMatchResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    Token
)
from auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash, 
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from cv_extractor_cli import CVExtractor
from llama_service import LlamaService  # Now uses LLaMA models

# Create FastAPI app
app = FastAPI(title="CV Analysis & Job Recommendation API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Initialize services
cv_extractor = CVExtractor()
llama_service = LlamaService()

# Create uploads directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        is_active=db_user.is_active == 'true',
        created_at=db_user.created_at
    )

@app.post("/auth/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.is_active != 'true':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if user_credentials.remember_me:
        access_token_expires = timedelta(days=7)  # Longer expiry for remember me
    
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            is_active=user.is_active == 'true',
            created_at=user.created_at
        )
    )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        is_active=current_user.is_active == 'true',
        created_at=current_user.created_at
    )

@app.post("/auth/logout")
async def logout_user(current_user: User = Depends(get_current_active_user)):
    """Logout user (client should remove token)."""
    return {"message": "Successfully logged out"}

@app.post("/upload-cv", response_model=UploadResponse)
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Upload a CV file, extract data, and store in database.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Please upload PDF, DOCX, or TXT files."
            )
        
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        print(f"DEBUG: Saving file to: {file_path}")
        print(f"DEBUG: File exists before save: {os.path.exists(file_path)}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"DEBUG: File exists after save: {os.path.exists(file_path)}")
        print(f"DEBUG: File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'}")
        
        # Extract CV data using existing extractor
        print(f"DEBUG: About to extract data from: {file_path}")
        extracted_data = cv_extractor.extract_cv_data(file_path)
        
        # Extract basic info for database
        contact_info = extracted_data.get("contact_info", {})
        name = None
        if contact_info.get("emails"):
            # Try to extract name from first email
            email = contact_info["emails"][0]
            name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
        
        # Create candidate record
        candidate = Candidate(
            name=name,
            email=contact_info.get("emails", [None])[0] if contact_info.get("emails") else None,
            phone=contact_info.get("phones", [None])[0] if contact_info.get("phones") else None,
            location=contact_info.get("address", ""),
            raw_cv_path=file_path,
            extracted_data=json.dumps(extracted_data)
        )
        
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        # Clean up the uploaded file after processing
        try:
            os.remove(file_path)
        except Exception as cleanup_error:
            print(f"Warning: Could not clean up file {file_path}: {cleanup_error}")
        
        return UploadResponse(
            candidate_id=candidate.id,
            extracted_data=extracted_data,
            message="CV uploaded and processed successfully"
        )
        
    except Exception as e:
        # Clean up file if there was an error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing CV: {str(e)}")

@app.get("/candidate/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Get candidate profile with extracted data and recommendations.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Parse extracted data
    extracted_data = json.loads(candidate.extracted_data) if candidate.extracted_data else {}
    
    # Get recommendations
    recommendations = []
    job_recs = db.query(JobRecommendation).filter(JobRecommendation.candidate_id == candidate_id).all()
    for rec in job_recs:
        recommendations.append(json.loads(rec.recommendations))
    
    return CandidateResponse(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
        raw_cv_path=candidate.raw_cv_path,
        extracted_data=extracted_data,
        status=candidate.status or 'New',
        created_at=candidate.created_at,
        recommendations=recommendations
    )

@app.post("/recommend/{candidate_id}", response_model=JobRecommendationResponse)
async def generate_recommendations(candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Generate job recommendations for a candidate using LLaMA models.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Parse extracted data
    extracted_data = json.loads(candidate.extracted_data) if candidate.extracted_data else {}
    
    # Generate recommendations using LLaMA service
    recommendations = llama_service.generate_recommendations(extracted_data)
    
    # Store recommendations in database
    job_recommendation = JobRecommendation(
        candidate_id=candidate_id,
        recommendations=json.dumps(recommendations)
    )
    
    db.add(job_recommendation)
    db.commit()
    db.refresh(job_recommendation)
    
    return JobRecommendationResponse(
        id=job_recommendation.id,
        candidate_id=candidate_id,
        recommendations=recommendations,
        created_at=job_recommendation.created_at
    )

@app.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Delete a candidate and all associated data.
    """
    # Check if candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    try:
        # Delete associated job recommendations first (due to foreign key constraint)
        db.query(JobRecommendation).filter(JobRecommendation.candidate_id == candidate_id).delete()
        
        # Delete the candidate
        db.delete(candidate)
        db.commit()
        
        # Optionally delete the uploaded file
        if candidate.raw_cv_path and os.path.exists(candidate.raw_cv_path):
            try:
                os.remove(candidate.raw_cv_path)
            except Exception as e:
                print(f"Warning: Could not delete file {candidate.raw_cv_path}: {e}")
        
        return {"message": f"Candidate {candidate_id} deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting candidate: {str(e)}")

@app.get("/candidates", response_model=List[CandidateSummary])
async def get_candidates(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Get list of all candidates with summary information.
    """
    candidates = db.query(Candidate).all()
    
    result = []
    for candidate in candidates:
        extracted_data = json.loads(candidate.extracted_data) if candidate.extracted_data else {}
        skills = extracted_data.get("skills", [])
        
        result.append(CandidateSummary(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            skills=skills,
            location=candidate.location,
            status=candidate.status or 'New',
            created_at=candidate.created_at
        ))
    
    return result

@app.patch("/candidate/{candidate_id}/status")
async def update_candidate_status(
    candidate_id: int, 
    status_update: StatusUpdateRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update candidate status.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Validate status
    valid_statuses = ['New', 'Interview Scheduled', 'Offer', 'Hired', 'Rejected']
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    candidate.status = status_update.status
    db.commit()
    
    return {"message": f"Candidate status updated to {status_update.status}"}

@app.post("/match-job", response_model=List[JobMatchResponse])
async def match_job(job_request: JobMatchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Match candidates against a job description.
    """
    try:
        # Extract required skills from job description using LLaMA
        required_skills = llama_service.extract_skills_from_job_description(job_request.job_description)
        
        # Get all candidates
        candidates = db.query(Candidate).all()
        
        matches = []
        for candidate in candidates:
            extracted_data = json.loads(candidate.extracted_data) if candidate.extracted_data else {}
            candidate_skills = extracted_data.get("skills", [])
            
            # Calculate match percentage
            match_percentage, missing_skills = calculate_skill_match(candidate_skills, required_skills)
            
            matches.append(JobMatchResponse(
                candidate_id=candidate.id,
                match=match_percentage,
                missing_skills=missing_skills
            ))
        
        # Sort by match percentage (highest first)
        matches.sort(key=lambda x: x.match, reverse=True)
        
        return matches
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching job: {str(e)}")

def calculate_skill_match(candidate_skills: List[str], required_skills: List[str]) -> tuple[int, List[str]]:
    """
    Calculate match percentage and missing skills.
    """
    if not required_skills:
        return 100, []
    
    # Normalize skills to lowercase for comparison
    candidate_skills_lower = [skill.lower().strip() for skill in candidate_skills]
    required_skills_lower = [skill.lower().strip() for skill in required_skills]
    
    # Find matching skills
    matching_skills = []
    missing_skills = []
    
    for required_skill in required_skills_lower:
        # Check for exact match or partial match
        matched = False
        for candidate_skill in candidate_skills_lower:
            if (required_skill in candidate_skill or 
                candidate_skill in required_skill or
                any(word in candidate_skill for word in required_skill.split() if len(word) > 2)):
                matching_skills.append(required_skill)
                matched = True
                break
        
        if not matched:
            missing_skills.append(required_skill)
    
    # Calculate match percentage
    match_percentage = int((len(matching_skills) / len(required_skills_lower)) * 100)
    
    return match_percentage, missing_skills

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "CV Analysis API is running"}

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "CV Analysis & Job Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "upload_cv": "POST /upload-cv",
            "get_candidate": "GET /candidate/{id}",
            "generate_recommendations": "POST /recommend/{id}",
            "get_candidates": "GET /candidates",
            "delete_candidate": "DELETE /candidates/{id}",
            "update_candidate_status": "PATCH /candidate/{id}/status",
            "match_job": "POST /match-job"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)