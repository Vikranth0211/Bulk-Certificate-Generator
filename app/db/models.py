import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    PARTIALLY_FAILED = "PARTIALLY_FAILED"
    FAILED = "FAILED"


class RecipientStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class CertificateJob(Base):
    __tablename__ = "certificate_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    event_name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False, default="Organization")
    issue_date = Column(String(50), nullable=False)
    
    status = Column(String(50), default=JobStatus.PENDING.value, nullable=False)
    total_count = Column(Integer, default=0, nullable=False)
    processed_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    recipients = relationship("RecipientRecord", back_populates="job", cascade="all, delete-orphan")
    certificates = relationship("CertificateRecord", back_populates="job", cascade="all, delete-orphan")


class RecipientRecord(Base):
    __tablename__ = "recipient_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("certificate_jobs.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    custom_fields = Column(Text, nullable=True)  # JSON formatted string
    
    status = Column(String(50), default=RecipientStatus.PENDING.value, nullable=False)
    error_message = Column(Text, nullable=True)
    certificate_id = Column(String(36), nullable=True)

    job = relationship("CertificateJob", back_populates="recipients")


class CertificateRecord(Base):
    __tablename__ = "certificate_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("certificate_jobs.id"), nullable=False)
    recipient_id = Column(String(36), ForeignKey("recipient_records.id"), nullable=False)
    
    recipient_name = Column(String(255), nullable=False)
    event_name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=False)
    issue_date = Column(String(50), nullable=False)
    
    verification_code = Column(String(64), unique=True, nullable=False)
    file_path_pdf = Column(String(512), nullable=False)
    file_path_png = Column(String(512), nullable=True)
    checksum = Column(String(64), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("CertificateJob", back_populates="certificates")
