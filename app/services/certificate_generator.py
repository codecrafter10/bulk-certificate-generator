
from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path("generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_certificate(recipient_name: str, certificate_id: int) -> str:
    file_path = OUTPUT_DIR / f"certificate_{certificate_id}.pdf"

    page_size = landscape(A4)
    pdf = canvas.Canvas(str(file_path), pagesize=page_size)
    width, height = page_size

    # Certificate border
    pdf.setLineWidth(3)
    pdf.rect(
        0.4 * inch,
        0.4 * inch,
        width - 0.8 * inch,
        height - 0.8 * inch,
    )

    # Heading
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(
        width / 2, height - 1.5 * inch, "CERTIFICATE"
    )

    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        width / 2, height - 2.0 * inch, "OF ACHIEVEMENT"
    )

    # Recipient
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(
        width / 2, height - 2.9 * inch,
        "This certificate is proudly presented to",
    )

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(
        width / 2, height - 3.6 * inch, recipient_name
    )

    # Certificate ID
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(
        width / 2, height - 4.3 * inch,
        f"Certificate ID: {certificate_id}",
    )

    pdf.save()
    return str(file_path)
