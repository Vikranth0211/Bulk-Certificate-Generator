from app.db.models import CertificateJob, RecipientRecord
from app.services.processor import process_certificate_job


def test_certificate_retrieval_and_verification(client, db_session):
    # 1. Create & process a job
    job = CertificateJob(
        title="Retrieval Test",
        event_name="Security 101",
        issuer="Cyber Institute",
        issue_date="2026-10-10",
        total_count=1
    )
    db_session.add(job)
    db_session.commit()

    r1 = RecipientRecord(job_id=job.id, name="David Miller", email="david@example.com")
    db_session.add(r1)
    db_session.commit()

    process_certificate_job(job.id, db=db_session)


    job_res = client.get(f"/api/v1/jobs/{job.id}")
    cert_id = job_res.json()["recipients"][0]["certificate_id"]

    # 2. Get Certificate Metadata
    cert_res = client.get(f"/api/v1/certificates/{cert_id}")
    assert cert_res.status_code == 200
    cert_data = cert_res.json()
    assert cert_data["recipient_name"] == "David Miller"

    # 3. Download PDF Certificate
    pdf_res = client.get(f"/api/v1/certificates/{cert_id}/download?format=pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 0

    # 4. Download PNG Certificate
    png_res = client.get(f"/api/v1/certificates/{cert_id}/download?format=png")
    assert png_res.status_code == 200
    assert png_res.headers["content-type"] == "image/png"
    assert len(png_res.content) > 0

    # 5. Public Verification Endpoint
    verify_res = client.get(f"/api/v1/certificates/verify/{cert_id}")
    assert verify_res.status_code == 200
    assert verify_res.json()["valid"] is True
    assert verify_res.json()["recipient_name"] == "David Miller"

    # 6. Bulk ZIP Download
    zip_res = client.get(f"/api/v1/jobs/{job.id}/download-all")
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"
    assert len(zip_res.content) > 0
