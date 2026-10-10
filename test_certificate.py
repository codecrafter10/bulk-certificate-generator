
from app.services.certificate_generator import generate_certificate

file_path = generate_certificate(
    recipient_name="Aisha Khan",
    certificate_id=1,
)

print("Certificate generated successfully!")
print("File location:", file_path)
