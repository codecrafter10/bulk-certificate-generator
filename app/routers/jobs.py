
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import GenerationJob, Certificate
from app.schemas import JobCreateRequest, JobResponse, CertificateResponse
from app.services.job_processor import process_job

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=JobResponse, status_code=202)
def create_job(
    request: JobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = GenerationJob(
        status="pending",
        total_count=len(request.recipients),
        success_count=0,
        failed_count=0,
    )

    db.add(job)
    db.flush()

    for recipient in request.recipients:
        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name.strip(),
            recipient_email=str(recipient.email),
            status="pending",
        )
        db.add(certificate)

    db.commit()
    db.refresh(job)

    background_tasks.add_task(process_job, job.id)

    return job

@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(GenerationJob)
        .filter(GenerationJob.id == job_id)
        .first()
    )

    if job is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job

@router.get("/{job_id}/certificates", response_model=list[CertificateResponse])
def list_job_certificates(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(GenerationJob)
        .filter(GenerationJob.id == job_id)
        .first()
    )

    if job is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .all()
    )


