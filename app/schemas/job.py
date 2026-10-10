import re
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class RecipientInput(BaseModel):
    name: str = Field(..., description="Full name of recipient")
    email: Optional[str] = Field(None, description="Email address of recipient")
    custom_fields: Optional[Dict[str, Any]] = Field(default=None, description="Additional custom fields (role, score, grade, etc.)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip() if v else ""
        if not stripped:
            raise ValueError("Recipient name cannot be blank or empty.")
        return stripped

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        stripped = v.strip()
        if not stripped:
            return None
        email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(email_regex, stripped):
            raise ValueError(f"Invalid email format: '{v}'")
        return stripped


class JobCreate(BaseModel):
    title: str = Field(..., description="Title of the certificate job (e.g. Workshop Completion)")
    event_name: str = Field(..., description="Event or Course Name")
    issuer: Optional[str] = Field("Global Learning Institute", description="Organization issuing the certificate")
    issue_date: Optional[str] = Field(None, description="Issue date in YYYY-MM-DD or readable string format")
    recipients: List[RecipientInput] = Field(..., min_length=1, description="List of recipient records")

    @field_validator("title", "event_name", "issuer")
    @classmethod
    def validate_non_empty_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Field cannot be empty or whitespace.")
            return stripped
        return v

    @field_validator("issue_date")
    @classmethod
    def default_issue_date(cls, v: Optional[str]) -> str:
        if not v or not v.strip():
            return date.today().strftime("%B %d, %Y")
        return v.strip()


class RecipientResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    certificate_id: Optional[str] = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    title: str
    event_name: str
    issuer: str
    issue_date: str
    status: str
    total_count: int
    processed_count: int
    success_count: int
    failed_count: int
    progress_percentage: float
    created_at: datetime
    completed_at: Optional[datetime] = None


class JobDetailResponse(JobResponse):
    recipients: List[RecipientResult]

