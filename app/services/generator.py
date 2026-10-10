import os
import hashlib
import uuid
from pathlib import Path
from typing import Dict, Any

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont

from app.config import CERTIFICATES_DIR


def generate_verification_code(recipient_name: str, event_name: str, issue_date: str) -> str:
    """Generate a unique 16-character alphanumeric verification code."""
    raw = f"{recipient_name}-{event_name}-{issue_date}-{uuid.uuid4()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].upper()


def calculate_file_checksum(file_path: Path) -> str:
    """Calculate SHA-256 hash of a generated file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def generate_pdf_certificate(
    pdf_path: Path,
    recipient_name: str,
    event_name: str,
    issuer: str,
    issue_date: str,
    verification_code: str,
    cert_id: str
):
    """Generate a vector PDF certificate using ReportLab canvas."""
    width, height = landscape(A4)  # 841.89 x 595.27 pt
    c = canvas.Canvas(str(pdf_path), pagesize=landscape(A4))

    # Colors
    navy_blue = colors.HexColor("#0f172a")
    gold = colors.HexColor("#d97706")
    slate = colors.HexColor("#475569")
    light_bg = colors.HexColor("#f8fafc")

    # Background Fill
    c.setFillColor(light_bg)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Outer Border (Gold)
    c.setStrokeColor(gold)
    c.setLineWidth(4)
    c.rect(20, 20, width - 40, height - 40)

    # Inner Border (Navy)
    c.setStrokeColor(navy_blue)
    c.setLineWidth(1.5)
    c.rect(26, 26, width - 52, height - 52)

    # Decorative Corner Accents
    c.setFillColor(gold)
    corner_size = 12
    # Top-Left
    c.rect(20, height - 20 - corner_size, corner_size, corner_size, fill=1, stroke=0)
    # Top-Right
    c.rect(width - 20 - corner_size, height - 20 - corner_size, corner_size, corner_size, fill=1, stroke=0)
    # Bottom-Left
    c.rect(20, 20, corner_size, corner_size, fill=1, stroke=0)
    # Bottom-Right
    c.rect(width - 20 - corner_size, 20, corner_size, corner_size, fill=1, stroke=0)

    # Header Ribbon Text
    c.setFillColor(gold)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2.0, height - 70, "OFFICIAL CERTIFICATION OF ACHIEVEMENT")

    # Main Title
    c.setFillColor(navy_blue)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width / 2.0, height - 120, "CERTIFICATE")
    c.drawCentredString(width / 2.0, height - 155, "OF COMPLETION")

    # Subtitle Line
    c.setFillColor(slate)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 200, "THIS CERTIFICATE IS PROUDLY PRESENTED TO")

    # Recipient Name
    c.setFillColor(navy_blue)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2.0, height - 250, recipient_name)

    # Decorative Line under name
    c.setStrokeColor(gold)
    c.setLineWidth(2)
    c.line(width / 2.0 - 150, height - 262, width / 2.0 + 150, height - 262)

    # Description Text
    c.setFillColor(slate)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 300, "for successfully completing the course and demonstrating excellence in")

    # Event / Course Name
    c.setFillColor(navy_blue)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2.0, height - 340, event_name)

    # Footer Section: Issuer Sign & Date
    # Date
    c.setFillColor(navy_blue)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 4.0, height - 430, issue_date)
    c.setStrokeColor(slate)
    c.setLineWidth(1)
    c.line(width / 4.0 - 75, height - 440, width / 4.0 + 75, height - 440)
    c.setFillColor(slate)
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 4.0, height - 455, "DATE ISSUED")

    # Badge Seal (Center Footer)
    c.setFillColor(gold)
    c.circle(width / 2.0, height - 435, 24, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(width / 2.0, height - 438, "VERIFIED")

    # Issuer Signature Line
    c.setFillColor(navy_blue)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(3 * width / 4.0, height - 430, issuer)
    c.setStrokeColor(slate)
    c.setLineWidth(1)
    c.line(3 * width / 4.0 - 75, height - 440, 3 * width / 4.0 + 75, height - 440)
    c.setFillColor(slate)
    c.setFont("Helvetica", 10)
    c.drawCentredString(3 * width / 4.0, height - 455, "AUTHORIZED ISSUER")

    # Bottom Verification Bar
    c.setFillColor(slate)
    c.setFont("Helvetica", 9)
    footer_str = f"Certificate ID: {cert_id}   |   Verification Code: {verification_code}"
    c.drawCentredString(width / 2.0, 38, footer_str)

    c.save()


def generate_png_certificate(
    png_path: Path,
    recipient_name: str,
    event_name: str,
    issuer: str,
    issue_date: str,
    verification_code: str,
    cert_id: str
):
    """Generate high-res PNG preview certificate using Pillow."""
    img_width, img_height = 1200, 848
    bg_color = (248, 250, 252)
    navy = (15, 23, 42)
    gold = (217, 119, 6)
    slate = (71, 85, 105)
    white = (255, 255, 255)

    img = Image.new("RGB", (img_width, img_height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Outer Gold Border
    draw.rectangle([30, 30, img_width - 30, img_height - 30], outline=gold, width=6)
    # Inner Navy Border
    draw.rectangle([40, 40, img_width - 40, img_height - 40], outline=navy, width=3)

    # Use default bitmap font with clean positioning
    try:
        font_large = ImageFont.truetype("arial.ttf", 44)
        font_medium = ImageFont.truetype("arial.ttf", 34)
        font_sub = ImageFont.truetype("arial.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font_large = font_medium = font_sub = font_small = ImageFont.load_default()

    # Draw Centered Text helper
    def draw_center(text, y, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (img_width - text_w) / 2
        draw.text((x, y), text, font=font, fill=fill)

    draw_center("OFFICIAL CERTIFICATION OF ACHIEVEMENT", 90, font_small, gold)
    draw_center("CERTIFICATE OF COMPLETION", 140, font_large, navy)
    draw_center("THIS CERTIFICATE IS PROUDLY PRESENTED TO", 230, font_sub, slate)
    draw_center(recipient_name, 290, font_medium, navy)
    
    # Underline name
    draw.line([(img_width // 2 - 200, 345), (img_width // 2 + 200, 345)], fill=gold, width=3)

    draw_center("for successfully completing the course and demonstrating excellence in", 390, font_sub, slate)
    draw_center(event_name, 440, font_large, navy)

    # Date & Issuer
    draw_center(f"Date: {issue_date}          Issuer: {issuer}", 600, font_sub, navy)

    # Gold Seal
    seal_x, seal_y = img_width // 2, 630
    draw.ellipse([seal_x - 45, seal_y - 45, seal_x + 45, seal_y + 45], fill=gold)
    draw_center("VERIFIED", seal_y - 10, font_small, white)

    # Footer verification info
    footer_text = f"Certificate ID: {cert_id}  |  Verification Code: {verification_code}"
    draw_center(footer_text, 770, font_small, slate)

    img.save(png_path, "PNG")


def generate_certificate(
    recipient_name: str,
    event_name: str,
    issuer: str,
    issue_date: str,
    job_id: str,
    recipient_id: str
) -> Dict[str, Any]:
    """Generate both PDF and PNG certificates for a recipient."""
    cert_id = str(uuid.uuid4())
    verification_code = generate_verification_code(recipient_name, event_name, issue_date)

    job_dir = CERTIFICATES_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    pdf_filename = f"cert_{cert_id}.pdf"
    png_filename = f"cert_{cert_id}.png"

    pdf_path = job_dir / pdf_filename
    png_path = job_dir / png_filename

    # Generate PDF
    generate_pdf_certificate(
        pdf_path=pdf_path,
        recipient_name=recipient_name,
        event_name=event_name,
        issuer=issuer,
        issue_date=issue_date,
        verification_code=verification_code,
        cert_id=cert_id
    )

    # Generate PNG preview
    generate_png_certificate(
        png_path=png_path,
        recipient_name=recipient_name,
        event_name=event_name,
        issuer=issuer,
        issue_date=issue_date,
        verification_code=verification_code,
        cert_id=cert_id
    )

    checksum = calculate_file_checksum(pdf_path)

    return {
        "certificate_id": cert_id,
        "verification_code": verification_code,
        "file_path_pdf": str(pdf_path),
        "file_path_png": str(png_path),
        "checksum": checksum,
    }
