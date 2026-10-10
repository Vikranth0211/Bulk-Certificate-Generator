import csv
import io
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import CertificateJob, RecipientRecord, JobStatus, RecipientStatus
from app.schemas.job import JobCreate, JobResponse, JobDetailResponse, RecipientInput
from app.services.processor import process_certificate_job

router = APIRouter(prefix="/api/v1/jobs", tags=["Certificate Jobs"])


def build_job_response(job: CertificateJob) -> JobResponse:
    progress = 0.0
    if job.total_count > 0:
        progress = round((job.processed_count / job.total_count) * 100.0, 2)

    return JobResponse(
        job_id=job.id,
        title=job.title,
        event_name=job.event_name,
        issuer=job.issuer,
        issue_date=job.issue_date,
        status=job.status,
        total_count=job.total_count,
        processed_count=job.processed_count,
        success_count=job.success_count,
        failed_count=job.failed_count,
        progress_percentage=progress,
        created_at=job.created_at,
        completed_at=job.completed_at
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_bulk_job(
    payload: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit a bulk certificate generation job with a JSON payload."""
    job = CertificateJob(
        title=payload.title,
        event_name=payload.event_name,
        issuer=payload.issuer or "Organization",
        issue_date=payload.issue_date,
        total_count=len(payload.recipients),
        status=JobStatus.PENDING.value
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Insert recipient records
    for item in payload.recipients:
        custom_str = json.dumps(item.custom_fields) if item.custom_fields else None
        rec = RecipientRecord(
            job_id=job.id,
            name=item.name,
            email=item.email,
            custom_fields=custom_str,
            status=RecipientStatus.PENDING.value
        )
        db.add(rec)
    
    db.commit()

    # Trigger background processor
    background_tasks.add_task(process_certificate_job, job.id)

    return build_job_response(job)


@router.post("/csv", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_bulk_job_from_csv(
    background_tasks: BackgroundTasks,
    title: str = Form(..., description="Job Title"),
    event_name: str = Form(..., description="Event Name"),
    issuer: str = Form("Organization", description="Issuer"),
    issue_date: Optional[str] = Form(None, description="Issue Date"),
    file: UploadFile = File(..., description="CSV file with 'name' and optional 'email' columns"),
    db: Session = Depends(get_db)
):
    """Upload a CSV file containing recipients for bulk certificate generation."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV format (.csv)")

    content = await file.read()
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames or "name" not in [f.lower().strip() for f in reader.fieldnames]:
        raise HTTPException(status_code=400, detail="CSV must contain a header with a 'name' column.")

    recipients_list = []
    for row in reader:
        # Standardize key names
        normalized_row = {k.lower().strip(): v.strip() for k, v in row.items() if k}
        name_val = normalized_row.get("name", "")
        email_val = normalized_row.get("email", None)
        if name_val:
            recipients_list.append((name_val, email_val))

    if not recipients_list:
        raise HTTPException(status_code=400, detail="No valid recipient rows found in the CSV file.")

    job = CertificateJob(
        title=title.strip(),
        event_name=event_name.strip(),
        issuer=issuer.strip(),
        issue_date=issue_date.strip() if issue_date else "Today",
        total_count=len(recipients_list),
        status=JobStatus.PENDING.value
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    for name_val, email_val in recipients_list:
        rec = RecipientRecord(
            job_id=job.id,
            name=name_val,
            email=email_val,
            status=RecipientStatus.PENDING.value
        )
        db.add(rec)
    db.commit()

    background_tasks.add_task(process_certificate_job, job.id)

    return build_job_response(job)


@router.get("", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    """List all certificate generation jobs."""
    jobs = db.query(CertificateJob).order_by(CertificateJob.created_at.desc()).all()
    return [build_job_response(j) for j in jobs]


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job_details(job_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed status, statistics, and per-recipient breakdown for a specific job."""
    job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Certificate job '{job_id}' not found.")

    base_resp = build_job_response(job)
    recipients = db.query(RecipientRecord).filter(RecipientRecord.job_id == job_id).all()

    recipient_results = [
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "status": r.status,
            "error_message": r.error_message,
            "certificate_id": r.certificate_id
        }
        for r in recipients
    ]

    return JobDetailResponse(
        **base_resp.model_dump(),
        recipients=recipient_results
    )
