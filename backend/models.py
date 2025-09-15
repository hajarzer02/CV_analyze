from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

# Request/Response Models
class CandidateCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    raw_cv_path: str
    extracted_data: Dict[str, Any]

class CandidateResponse(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    raw_cv_path: str
    extracted_data: Dict[str, Any]
    status: str = 'New'
    created_at: datetime
    recommendations: Optional[List[List[Dict[str, str]]]] = None

    class Config:
        from_attributes = True

class CandidateSummary(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[str]
    skills: List[str]
    location: Optional[str]
    status: str = 'New'
    created_at: datetime

    class Config:
        from_attributes = True

class JobRecommendationResponse(BaseModel):
    id: int
    candidate_id: int
    recommendations: List[Dict[str, str]]
    created_at: datetime

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    candidate_id: int
    extracted_data: Dict[str, Any]
    message: str

class StatusUpdateRequest(BaseModel):
    status: str

class JobMatchRequest(BaseModel):
    job_description: str

class JobMatchResponse(BaseModel):
    candidate_id: int
    match: int
    missing_skills: List[str]

# Internal data models (matching the existing CV extractor output)
class ContactInfo(BaseModel):
    emails: List[str] = []
    phones: List[str] = []
    linkedin: str = ""
    address: str = ""

class Language(BaseModel):
    language: str
    level: str

class EducationEntry(BaseModel):
    date_range: Optional[str] = None
    degree: Optional[str] = None
    institution: Optional[str] = None
    details: List[str] = []

class ExperienceEntry(BaseModel):
    date_range: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    details: List[str] = []

class Project(BaseModel):
    title: str
    description: str = ""

class ExtractedCVData(BaseModel):
    contact_info: Optional[ContactInfo] = None
    professional_summary: List[str] = []
    skills: List[str] = []
    languages: List[Language] = []
    education: List[EducationEntry] = []
    experience: List[ExperienceEntry] = []
    projects: List[Project] = []
