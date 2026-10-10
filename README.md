**Bulk Certificate Generator API & Verification System**

A high-performance, resilient backend API and interactive web application built with **Python**, **FastAPI**, **SQLAlchemy**, and **ReportLab**. The system accepts bulk certificate generation requests for hundreds of recipients, validates data asynchronously, isolates per-recipient failures, renders crisp vector PDF & PNG certificates, and provides public verification and batch ZIP export capabilities.



**Key Features**

1. **Bulk Request Processing**: Submit certificate requests for multiple recipients in a single API call via JSON or CSV file upload.
2. **Asynchronous Non-Blocking Processing**: Uses FastAPI background processing. Requests return immediately with HTTP `202 Accepted` and a job tracking ID.
3. **Isolated Recipient Failure Handling**: An invalid recipient (e.g. blank name or malformed email) will not interrupt or fail the remaining valid certificates in the batch. The overall job status dynamically transitions to `COMPLETED`, `PARTIALLY_FAILED`, or `FAILED`.
4. **Dual Format Generation**: Automatically renders high-resolution vector **PDF certificates** (for printing/sharing) and **PNG previews** (for instant web viewing).
5. **Cryptographic Integrity & Public Verification**: Every certificate includes a unique 16-character verification code and SHA-256 file checksum searchable via public verification endpoint.
6. **One-Click Bulk ZIP Export**: Download all generated PDF certificates in a job packaged cleanly inside a single `.zip` archive.
7. **Interactive Web UI Dashboard**: Modern dark-themed dashboard served at `/` featuring live job progress polling, sample data loader, preview modal, and public verifier.
8. **Comprehensive Automated Test Suite**: 100% test pass rate across validation, generator engine, API endpoints, partial failure handling, and file downloads.

---

**Technology Stack**

- **Language**: Python 3.10+
- **Web Framework**: FastAPI (Async, Pydantic v2, OpenAPI/Swagger docs)
- **Database & ORM**: SQLite (via SQLAlchemy 2.0 ORM)
- **PDF/Image Rendering**: ReportLab & Pillow
- **Testing**: Pytest & HTTPX / TestClient

---

**Setup & Installation**

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Clone / Navigate to Directory
```bash
cd "d:/Projects/Bulk Certificate Generator"
```

### 3. Create & Activate Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

**Install Dependencies**
```bash
pip install -r requirements.txt
```

---

**Running the Application**

Start the development server using `uvicorn`:

```bash
uvicorn app.main:app --reload --port 8000
```

Once running, access the following in your browser:
- **Interactive Web Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **OpenAPI / Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

**Running Automated Tests**

Run the full pytest suite:

```bash
pytest -v
```

### Covered Test Scenarios:
- `test_valid_recipient_input` & `test_blank_recipient_name_fails`: Schema validation & error detection.
- `test_generate_certificate_files`: ReportLab PDF & Pillow PNG generation + SHA-256 checksums.
- `test_create_job_json_and_process`: JSON bulk request submission & background execution.
- `test_individual_recipient_failure_handling`: **Partial failure test** verifying 1 valid recipient succeeds while 1 invalid recipient fails without crashing the job.
- `test_create_job_csv_upload`: Uploading CSV recipient file.
- `test_certificate_retrieval_and_verification`: Metadata retrieval, PDF/PNG download, public verifier, and ZIP archive download.

---

**API Reference & Examples**

**Submit Bulk Job (JSON Payload)**
**`POST /api/v1/jobs`**

#### Request Body:
```json
{
  "title": "Python Developer Certification 2026",
  "event_name": "FastAPI & Asynchronous Architecture",
  "issuer": "Global Tech Institute",
  "issue_date": "October 10, 2026",
  "recipients": [
    { "name": "Eleanor Vance", "email": "eleanor.vance@example.com" },
    { "name": "Marcus Brody", "email": "marcus.b@example.org" },
    { "name": "   ", "email": "invalid-email" }
  ]
}
```

#### Response (`202 Accepted`):
```json
{
  "job_id": "5af6d4dd-75ce-4bc0-af6f-94ab4e2aef52",
  "title": "Python Developer Certification 2026",
  "event_name": "FastAPI & Asynchronous Architecture",
  "issuer": "Global Tech Institute",
  "issue_date": "October 10, 2026",
  "status": "PENDING",
  "total_count": 3,
  "processed_count": 0,
  "success_count": 0,
  "failed_count": 0,
  "progress_percentage": 0.0,
  "created_at": "2026-10-10T10:37:57.497352",
  "completed_at": null
}
```

---

### 2. Check Job Progress & Details
**`GET /api/v1/jobs/{job_id}`**

#### Response (`200 OK`):
```json
{
  "job_id": "5af6d4dd-75ce-4bc0-af6f-94ab4e2aef52",
  "title": "Python Developer Certification 2026",
  "event_name": "FastAPI & Asynchronous Architecture",
  "status": "PARTIALLY_FAILED",
  "total_count": 3,
  "processed_count": 3,
  "success_count": 2,
  "failed_count": 1,
  "progress_percentage": 100.0,
  "created_at": "2026-10-10T10:37:57.497352",
  "completed_at": "2026-10-10T10:37:58.120410",
  "recipients": [
    {
      "id": "rec-1",
      "name": "Eleanor Vance",
      "email": "eleanor.vance@example.com",
      "status": "SUCCESS",
      "error_message": null,
      "certificate_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
    },
    {
      "id": "rec-3",
      "name": "   ",
      "email": "invalid-email",
      "status": "FAILED",
      "error_message": "Recipient name is blank or missing.",
      "certificate_id": null
    }
  ]
}
```

---

### 3. Retrieve & Download Single Certificate
- **Get Certificate Metadata**: `GET /api/v1/certificates/{certificate_id}`
- **Download PDF**: `GET /api/v1/certificates/{certificate_id}/download?format=pdf`
- **Download PNG Image**: `GET /api/v1/certificates/{certificate_id}/download?format=png`

---

### 4. Download All Certificates as ZIP Archive
**`GET /api/v1/jobs/{job_id}/download-all`**
Returns a `.zip` file containing all successfully generated PDF certificates for the specified job.

---

### 5. Public Certificate Verification
**`GET /api/v1/certificates/verify/{certificate_id_or_verification_code}`**

#### Response (`200 OK`):
```json
{
  "valid": true,
  "message": "Certificate is authentic and valid.",
  "certificate_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "recipient_name": "Eleanor Vance",
  "event_name": "FastAPI & Asynchronous Architecture",
  "issuer": "Global Tech Institute",
  "issue_date": "October 10, 2026",
  "verification_code": "4F9A2B81E7C3D5A0",
  "checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

---

**Important Design & Architecture Decisions**

1. **FastAPI Background Processing**:
   - Rather than blocking HTTP client requests during heavy bulk generation tasks, jobs return `202 Accepted` immediately. Background tasks process recipients sequentially or concurrently without clogging main API event loops.

2. **Isolated Recipient Error Handling**:
   - Standard bulk processing loops often crash entirely if a single record fails. In our implementation, each recipient record is wrapped in an isolated `try/except` block. If recipient input validation fails or rendering throws an exception, that specific record is marked `FAILED` with an explanatory error message, while remaining recipients continue processing.

3. **Dual PDF/PNG Output**:
   - PDF provides a vector-based, printable document suitable for distribution. PNG provides an instant preview rendered directly on web frontends without requiring browser PDF plugin extensions.

4. **Cryptographic Verification**:
   - Verification codes are generated using SHA-256 hashes of recipient metadata + UUIDs. File contents are hashed using SHA-256 to ensure certificates cannot be tampered with.

5. **Relational Database Design**:
   - Separate normalized tables for `certificate_jobs`, `recipient_records`, and `certificate_records` enable detailed statistical reporting, progress tracking, and audit history.
