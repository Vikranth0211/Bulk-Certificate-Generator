from pathlib import Path
from typing import Optional
import zipfile
from sqlalchemy.orm import Session
from app.config import CERTIFICATES_DIR
from app.db.models import CertificateJob, CertificateRecord


def create_job_zip_archive(job_id: str, db: Optional[Session] = None) -> Optional[Path]:
    """Package all generated PDF certificates for a job into a ZIP file."""
    close_db = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_db = True
    try:
        job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
        if not job:
            return None

        certificates = db.query(CertificateRecord).filter(CertificateRecord.job_id == job_id).all()
        if not certificates:
            return None

        zip_path = CERTIFICATES_DIR / f"job_{job_id}_certificates.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for cert in certificates:
                pdf_path = Path(cert.file_path_pdf)
                if pdf_path.exists():
                    safe_name = "".join(c for c in cert.recipient_name if c.isalnum() or c in (" ", "_", "-")).rstrip()
                    zip_arcname = f"{safe_name}_{cert.id[:8]}.pdf"
                    zipf.write(pdf_path, arcname=zip_arcname)

        return zip_path
    finally:
        if close_db:
            db.close()

