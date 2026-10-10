
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RecipientInput(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr


class JobCreateRequest(BaseModel):
    recipients: list[RecipientInput] = Field(min_length=1, max_length=500)


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_name: str
    recipient_email: str
    status: str
    error_message: str | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    total_count: int
    success_count: int
    failed_count: int
