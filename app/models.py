
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)

    status = Column(
        String(30),
        default="pending",
        nullable=False,
    )

    total_count = Column(
        Integer,
        default=0,
        nullable=False,
    )

    success_count = Column(
        Integer,
        default=0,
        nullable=False,
    )

    failed_count = Column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("generation_jobs.id"),
        nullable=False,
    )

    recipient_name = Column(
        String(150),
        nullable=False,
    )

    recipient_email = Column(
        String(255),
        nullable=False,
    )

    status = Column(
        String(30),
        default="pending",
        nullable=False,
    )

    file_path = Column(
        String(500),
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    job = relationship(
        "GenerationJob",
        back_populates="certificates",
    )
