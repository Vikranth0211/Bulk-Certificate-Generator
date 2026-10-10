from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import CertificateRecord, CertificateJob
from app.schemas.certificate import CertificateResponse, VerificationResponse
from app.services.exporter import create_job_zip_archive

router = APIRouter(prefix="/api/v1", tags=["Certificates"])


@router.get("/certificates/verify/{identifier}", response_model=VerificationResponse)
def verify_certificate(identifier: str, db: Session = Depends(get_db)):
    """Public verification endpoint to verify certificate authenticity by ID or verification code."""
    cleaned = identifier.strip()
    cert = db.query(CertificateRecord).filter(
        (CertificateRecord.id == cleaned) | (CertificateRecord.verification_code == cleaned)
    ).first()

    if not cert:
        return VerificationResponse(
            valid=False,
            message="No matching certificate record found in the verification database."
        )

    return VerificationResponse(
        valid=True,
        message="Certificate is authentic and valid.",
        certificate_id=cert.id,
        recipient_name=cert.recipient_name,
        event_name=cert.event_name,
        issuer=cert.issuer,
        issue_date=cert.issue_date,
        verification_code=cert.verification_code,
        checksum=cert.checksum,
        issued_at=cert.created_at
    )


@router.get("/certificates/{certificate_id}", response_model=CertificateResponse)
def get_certificate_metadata(certificate_id: str, db: Session = Depends(get_db)):
    """Retrieve metadata and download URLs for a single certificate."""
    cert = db.query(CertificateRecord).filter(CertificateRecord.id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail=f"Certificate '{certificate_id}' not found.")

    return CertificateResponse(
        certificate_id=cert.id,
        job_id=cert.job_id,
        recipient_name=cert.recipient_name,
        event_name=cert.event_name,
        issuer=cert.issuer,
        issue_date=cert.issue_date,
        verification_code=cert.verification_code,
        checksum=cert.checksum,
        created_at=cert.created_at,
        pdf_download_url=f"/api/v1/certificates/{cert.id}/download?format=pdf",
        png_download_url=f"/api/v1/certificates/{cert.id}/download?format=png" if cert.file_path_png else None
    )


@router.get("/certificates/{certificate_id}/download")
def download_certificate(
    certificate_id: str,
    format: str = Query("pdf", description="File format to download ('pdf' or 'png')"),
    db: Session = Depends(get_db)
):
    """Download single certificate file in PDF or PNG format."""
    cert = db.query(CertificateRecord).filter(CertificateRecord.id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail=f"Certificate '{certificate_id}' not found.")

    fmt = format.lower().strip()
    if fmt == "png":
        file_path = Path(cert.file_path_png) if cert.file_path_png else None
        media_type = "image/png"
        ext = "png"
    else:
        file_path = Path(cert.file_path_pdf)
        media_type = "application/pdf"
        ext = "pdf"

    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested certificate file is missing from server storage.")

    safe_name = "".join(c for c in cert.recipient_name if c.isalnum() or c in (" ", "_")).strip()
    filename = f"{safe_name}_Certificate.{ext}"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


@router.get("/jobs/{job_id}/download-all")
def download_all_certificates(job_id: str, db: Session = Depends(get_db)):
    """Download all successfully generated certificates in a job as a single ZIP archive."""
    job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    zip_path = create_job_zip_archive(job_id)
    if not zip_path or not zip_path.exists():
        raise HTTPException(
            status_code=400,
            detail="No certificates available to download for this job. Ensure at least one certificate succeeded."
        )

    safe_title = "".join(c for c in job.title if c.isalnum() or c in (" ", "_")).strip()
    filename = f"{safe_title}_Certificates.zip"

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=filename
    )
