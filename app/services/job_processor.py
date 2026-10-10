
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import GenerationJob, Certificate
from app.services.certificate_generator import generate_certificate


def process_job(job_id: int) -> None:
    db = SessionLocal()

    try:
        job = db.query(GenerationJob).filter(
            GenerationJob.id == job_id
        ).first()

        if job is None:
            return

        job.status = "processing"
        db.commit()

        certificates = (
            db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .all()
        )

        for certificate in certificates:
            try:
                file_path = generate_certificate(
                    recipient_name=certificate.recipient_name,
                    certificate_id=certificate.id,
                )

                certificate.file_path = file_path
                certificate.status = "completed"
                certificate.error_message = None

            except Exception as exc:
                certificate.status = "failed"
                certificate.error_message = str(exc)[:1000]

            # Save each result independently so one failure
            # does not prevent other recipients from processing.
            db.commit()

        job = db.query(GenerationJob).filter(
            GenerationJob.id == job_id
        ).first()

        job.success_count = (
            db.query(Certificate)
            .filter(
                Certificate.job_id == job_id,
                Certificate.status == "completed",
            )
            .count()
        )

        job.failed_count = (
            db.query(Certificate)
            .filter(
                Certificate.job_id == job_id,
                Certificate.status == "failed",
            )
            .count()
        )

        job.status = (
            "completed_with_errors"
            if job.failed_count > 0
            else "completed"
        )
        job.completed_at = datetime.now(timezone.utc)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
