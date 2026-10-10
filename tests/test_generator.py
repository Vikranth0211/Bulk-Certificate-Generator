from pathlib import Path
from app.services.generator import generate_certificate, generate_verification_code, calculate_file_checksum


def test_generate_verification_code():
    code1 = generate_verification_code("Alice", "Python Course", "2026-10-10")
    code2 = generate_verification_code("Alice", "Python Course", "2026-10-10")
    assert len(code1) == 16
    assert code1 != code2  # Uniqueness check


def test_generate_certificate_files():
    cert_data = generate_certificate(
        recipient_name="Test Student",
        event_name="FastAPI Workshop",
        issuer="PyTech Institute",
        issue_date="October 10, 2026",
        job_id="test_job_123",
        recipient_id="test_rec_456"
    )

    pdf_path = Path(cert_data["file_path_pdf"])
    png_path = Path(cert_data["file_path_png"])

    assert pdf_path.exists()
    assert png_path.exists()
    assert pdf_path.stat().st_size > 0
    assert png_path.stat().st_size > 0

    assert cert_data["checksum"] == calculate_file_checksum(pdf_path)
