
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Certificate

router = APIRouter(
    prefix="/api/certificates",
    tags=["Certificates"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{certificate_id}/download")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
):
    certificate = (
        db.query(Certificate)
        .filter(Certificate.id == certificate_id)
        .first()
    )

    if certificate is None:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found",
        )

    if certificate.status != "completed" or not certificate.file_path:
        raise HTTPException(
            status_code=409,
            detail="Certificate is not ready for download",
        )

    file_path = Path(certificate.file_path).resolve()
    generated_dir = Path("generated").resolve()

    if not file_path.is_relative_to(generated_dir):
        raise HTTPException(
            status_code=400,
            detail="Invalid certificate file path",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Certificate PDF file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name,
    )
