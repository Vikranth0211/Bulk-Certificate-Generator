from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    certificate_id: str
    job_id: str
    recipient_name: str
    event_name: str
    issuer: str
    issue_date: str
    verification_code: str
    checksum: str
    created_at: datetime
    pdf_download_url: str
    png_download_url: Optional[str] = None



class VerificationResponse(BaseModel):
    valid: bool
    message: str
    certificate_id: Optional[str] = None
    recipient_name: Optional[str] = None
    event_name: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    verification_code: Optional[str] = None
    checksum: Optional[str] = None
    issued_at: Optional[datetime] = None
