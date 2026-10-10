import json
import logging
import re
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import CertificateJob, RecipientRecord, CertificateRecord, JobStatus, RecipientStatus
from app.services.generator import generate_certificate


logger = logging.getLogger(__name__)


def validate_recipient_data(recipient: RecipientRecord) -> tuple[bool, str]:
    """Validate recipient name and email format."""
    if not recipient.name or not recipient.name.strip():
        return False, "Recipient name is blank or missing."
    
    if recipient.email and recipient.email.strip():
        email = recipient.email.strip()
        email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(email_regex, email):
            return False, f"Invalid email format: '{recipient.email}'"
            
    return True, ""


def process_certificate_job(job_id: str, db: Optional[Session] = None):
    """Process a certificate generation job asynchronously."""
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True

    try:
        job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found for background processing.")
            return


        # Mark job as processing
        job.status = JobStatus.PROCESSING.value
        db.commit()

        recipients = db.query(RecipientRecord).filter(RecipientRecord.job_id == job_id).all()

        for recipient in recipients:
            # 1. Input Validation
            is_valid, err_msg = validate_recipient_data(recipient)
            if not is_valid:
                recipient.status = RecipientStatus.FAILED.value
                recipient.error_message = err_msg
                job.failed_count += 1
                job.processed_count += 1
                db.commit()
                continue

            # 2. Certificate Generation
            try:
                cert_data = generate_certificate(
                    recipient_name=recipient.name.strip(),
                    event_name=job.event_name,
                    issuer=job.issuer,
                    issue_date=job.issue_date,
                    job_id=job.id,
                    recipient_id=recipient.id
                )

                # Create Certificate Record
                cert_record = CertificateRecord(
                    id=cert_data["certificate_id"],
                    job_id=job.id,
                    recipient_id=recipient.id,
                    recipient_name=recipient.name.strip(),
                    event_name=job.event_name,
                    issuer=job.issuer,
                    issue_date=job.issue_date,
                    verification_code=cert_data["verification_code"],
                    file_path_pdf=cert_data["file_path_pdf"],
                    file_path_png=cert_data["file_path_png"],
                    checksum=cert_data["checksum"],
                    created_at=datetime.utcnow()
                )
                db.add(cert_record)

                recipient.status = RecipientStatus.SUCCESS.value
                recipient.certificate_id = cert_data["certificate_id"]
                job.success_count += 1
                job.processed_count += 1
                db.commit()

            except Exception as e:
                logger.exception(f"Failed to generate certificate for recipient {recipient.id}")
                recipient.status = RecipientStatus.FAILED.value
                recipient.error_message = f"Generation error: {str(e)}"
                job.failed_count += 1
                job.processed_count += 1
                db.commit()

        # Final Job Status update
        if job.failed_count == 0:
            job.status = JobStatus.COMPLETED.value
        elif job.success_count > 0:
            job.status = JobStatus.PARTIALLY_FAILED.value
        else:
            job.status = JobStatus.FAILED.value

        job.completed_at = datetime.utcnow()
        db.commit()

    except Exception as exc:
        logger.exception(f"Unhandled error in job processing {job_id}")
        db.rollback()
    finally:
        if close_db:
            db.close()

