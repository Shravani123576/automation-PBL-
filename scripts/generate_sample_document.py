"""
Generates a minimal valid PDF document without external libraries.
This produces a strictly conforming, small PDF under 2 KB with visible test text:
'SAMPLE - TEST DOCUMENT - NOT A REAL CERTIFICATE'
"""

from pathlib import Path


def create_minimal_pdf(output_path: Path, title: str = "SAMPLE - TEST DOCUMENT - NOT A REAL CERTIFICATE") -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Minimal 1-page valid PDF content (stream text object)
    stream_content = f"BT /F1 16 Tf 50 720 Td ({title}) Tj ET\n"
    stream_len = len(stream_content.encode("latin-1"))
    
    pdf_template = (
        "%PDF-1.4\n"
        "1 0 obj\n"
        "<< /Type /Catalog /Pages 2 0 R >>\n"
        "endobj\n"
        "2 0 obj\n"
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        "endobj\n"
        "3 0 obj\n"
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\n"
        "endobj\n"
        "4 0 obj\n"
        f"<< /Length {stream_len} >>\n"
        "stream\n"
        f"{stream_content}"
        "endstream\n"
        "endobj\n"
        "5 0 obj\n"
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\n"
        "endobj\n"
        "xref\n"
        "0 6\n"
        "0000000000 65535 f \n"
        "0000000009 00000 n \n"
        "0000000058 00000 n \n"
        "0000000115 00000 n \n"
        "0000000227 00000 n \n"
        "0000000320 00000 n \n"
        "trailer\n"
        "<< /Size 6 /Root 1 0 R >>\n"
        "startxref\n"
        "395\n"
        "%%EOF\n"
    )

    with open(output_path, "wb") as f:
        f.write(pdf_template.encode("latin-1"))
    print(f"Generated sample document: {output_path} ({output_path.stat().st_size} bytes)")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    target_pdf = base_dir / "sample_data" / "documents" / "sample_income_certificate.pdf"
    create_minimal_pdf(target_pdf)
