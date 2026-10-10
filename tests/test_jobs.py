import io
import time
from app.db.models import CertificateJob, RecipientRecord, JobStatus, RecipientStatus
from app.services.processor import process_certificate_job


def test_create_job_json_and_process(client, db_session):
    payload = {
        "title": "JSON Test Job",
        "event_name": "Full Stack Mastery",
        "issuer": "Global Academy",
        "issue_date": "2026-10-10",
        "recipients": [
            {"name": "Alice Smith", "email": "alice@example.com"},
            {"name": "Bob Jones", "email": "bob@example.com"}
        ]
    }

    res = client.post("/api/v1/jobs", json=payload)
    assert res.status_code == 202
    data = res.json()
    assert data["status"] == "PENDING"
    assert data["total_count"] == 2

    job_id = data["job_id"]

    # Check status endpoint

    status_res = client.get(f"/api/v1/jobs/{job_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["status"] == "COMPLETED"
    assert status_data["success_count"] == 2
    assert status_data["failed_count"] == 0
    assert len(status_data["recipients"]) == 2


def test_individual_recipient_failure_handling(client, db_session):
    """Test partial failure isolation where 1 recipient is valid and 1 fails."""
    job = CertificateJob(
        title="Partial Failure Job",
        event_name="Edge Case Testing",
        issuer="Test Org",
        issue_date="2026-10-10",
        total_count=2,
        status=JobStatus.PENDING.value
    )
    db_session.add(job)
    db_session.commit()

    r1 = RecipientRecord(job_id=job.id, name="Valid Recipient", email="valid@example.com")
    r2 = RecipientRecord(job_id=job.id, name="   ", email="bad-email")  # Intentionally blank name
    db_session.add_all([r1, r2])
    db_session.commit()

    # Process job
    process_certificate_job(job.id, db=db_session)


    # Query job details
    res = client.get(f"/api/v1/jobs/{job.id}")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "PARTIALLY_FAILED"
    assert data["success_count"] == 1
    assert data["failed_count"] == 1

    # Verify per-recipient statuses
    recipients = data["recipients"]
    valid_rec = next(r for r in recipients if r["name"] == "Valid Recipient")
    failed_rec = next(r for r in recipients if r["name"] == "   ")

    assert valid_rec["status"] == "SUCCESS"
    assert valid_rec["certificate_id"] is not None

    assert failed_rec["status"] == "FAILED"
    assert "blank or missing" in failed_rec["error_message"]


def test_create_job_csv_upload(client, db_session):
    csv_content = "name,email\nGrace Hopper,grace@example.com\nAda Lovelace,ada@example.com\n"
    files = {"file": ("recipients.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    form_data = {
        "title": "CSV Test Job",
        "event_name": "Computer Science Pioneers",
        "issuer": "CS Institute",
        "issue_date": "2026-10-10"
    }

    res = client.post("/api/v1/jobs/csv", data=form_data, files=files)
    assert res.status_code == 202
    data = res.json()
    assert data["total_count"] == 2
