import pypdf
 
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    รับ path ของไฟล์ PDF แล้วคืนข้อความทั้งหมดเป็น string
    """
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        text = f"[Error reading PDF: {e}]"
    return text.strip()
 