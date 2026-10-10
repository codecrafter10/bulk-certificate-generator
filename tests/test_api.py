
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import GenerationJob, Certificate
from app.services.certificate_generator import generate_certificate

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Bulk Certificate Generator API is running"
    )


def test_create_job_with_valid_recipients():
    response = client.post(
        "/api/jobs/",
        json={
            "recipients": [
                {
                    "name": "Pytest User One",
                    "email": "pytest1@example.com",
                },
                {
                    "name": "Pytest User Two",
                    "email": "pytest2@example.com",
                },
            ]
        },
    )

    assert response.status_code == 202
    data = response.json()
    assert data["total_count"] == 2
    assert data["id"] > 0


def test_create_job_with_invalid_email():
    response = client.post(
        "/api/jobs/",
        json={
            "recipients": [
                {
                    "name": "Invalid User",
                    "email": "not-an-email",
                }
            ]
        },
    )

    assert response.status_code == 422


def test_job_not_found():
    response = client.get("/api/jobs/999999")

    assert response.status_code == 404


def test_certificate_not_found():
    response = client.get(
        "/api/certificates/999999/download"
    )

    assert response.status_code == 404


def test_certificate_generation(tmp_path, monkeypatch):
    import app.services.certificate_generator as generator

    monkeypatch.setattr(generator, "OUTPUT_DIR", tmp_path)

    file_path = generator.generate_certificate(
        recipient_name="Test Recipient",
        certificate_id=9999,
    )

    pdf_file = Path(file_path)

    assert pdf_file.exists()
    assert pdf_file.suffix == ".pdf"
    assert pdf_file.stat().st_size > 0


def test_job_status_and_progress():
    response = client.post(
        "/api/jobs/",
        json={
            "recipients": [
                {
                    "name": "Progress Test One",
                    "email": "progress1@example.com",
                },
                {
                    "name": "Progress Test Two",
                    "email": "progress2@example.com",
                },
            ]
        },
    )

    assert response.status_code == 202
    job_id = response.json()["id"]

    status_response = client.get(f"/api/jobs/{job_id}")

    assert status_response.status_code == 200

    data = status_response.json()
    assert data["id"] == job_id
    assert data["total_count"] == 2
    assert data["success_count"] + data["failed_count"] <= 2
    assert data["status"] in [
        "pending",
        "processing",
        "completed",
        "completed_with_errors",
    ]


def test_one_recipient_failure_does_not_stop_others():
    with patch(
        "app.services.job_processor.generate_certificate"
    ) as mock_generate:
        mock_generate.side_effect = [
            RuntimeError("Simulated PDF failure"),
            "generated/test_success.pdf",
        ]

        response = client.post(
            "/api/jobs/",
            json={
                "recipients": [
                    {
                        "name": "Failure Test",
                        "email": "failure@example.com",
                    },
                    {
                        "name": "Success Test",
                        "email": "success@example.com",
                    },
                ]
            },
        )

    assert response.status_code == 202

    job_id = response.json()["id"]
    status_response = client.get(f"/api/jobs/{job_id}")

    assert status_response.status_code == 200

    job_data = status_response.json()
    assert job_data["total_count"] == 2
    assert job_data["failed_count"] == 1
    assert job_data["success_count"] == 1
    assert job_data["status"] == "completed_with_errors"


def test_certificate_download_success():
    generated_dir = Path("generated").resolve()
    generated_dir.mkdir(parents=True, exist_ok=True)

    # Generate a PDF inside the directory allowed by the API.
    pdf_path = generate_certificate(
        recipient_name="Download Test",
        certificate_id=98765,
    )
    pdf_path = Path(pdf_path).resolve()

    db = SessionLocal()

    try:
        job = GenerationJob(
            status="completed",
            total_count=1,
            success_count=1,
            failed_count=0,
        )
        db.add(job)
        db.flush()

        certificate = Certificate(
            job_id=job.id,
            recipient_name="Download Test",
            recipient_email="download@example.com",
            status="completed",
            file_path=str(pdf_path),
        )
        db.add(certificate)
        db.commit()
        db.refresh(certificate)

        certificate_id = certificate.id
    finally:
        db.close()

    response = client.get(
        f"/api/certificates/{certificate_id}/download"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
