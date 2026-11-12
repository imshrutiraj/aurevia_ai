import os
import re
import pdfplumber
import docx
from werkzeug.utils import secure_filename
from backend.text_preprocessing import clean_text

class ResumeParser:
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

    @classmethod
    def is_allowed_file(cls, filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in cls.ALLOWED_EXTENSIONS

    @classmethod
    def validate_file(cls, file_storage) -> tuple[bool, str]:
        if not file_storage or not file_storage.filename:
            return False, "No file provided or filename is empty."
        
        filename = secure_filename(file_storage.filename)
        if not cls.is_allowed_file(filename):
            return False, f"File type not supported. Please upload a .pdf or .docx file."

        # Check file content header / magic bytes
        file_storage.seek(0, os.SEEK_END)
        size = file_storage.tell()
        file_storage.seek(0)
        
        if size == 0:
            return False, "The uploaded file is empty (0 bytes)."
        if size > cls.MAX_FILE_SIZE:
            return False, f"File size ({size / (1024*1024):.1f}MB) exceeds the 16MB limit."

        header = file_storage.read(4)
        file_storage.seek(0)

        ext = filename.rsplit(".", 1)[1].lower()
        if ext == "pdf" and not header.startswith(b"%PDF"):
            return False, "Invalid PDF header. The file appears corrupted or is not a valid PDF."
        elif ext == "docx" and not header.startswith(b"PK"):
            return False, "Invalid DOCX format. The file appears corrupted or is not a valid DOCX document."

        return True, ""

    @classmethod
    def extract_text_from_pdf(cls, file_path_or_stream) -> str:
        text_parts = []
        try:
            with pdfplumber.open(file_path_or_stream) as pdf:
                if len(pdf.pages) == 0:
                    raise ValueError("The PDF contains no pages.")
                for page_idx, page in enumerate(pdf.pages):
                    extracted = page.extract_text()
                    if extracted:
                        text_parts.append(extracted)
        except Exception as e:
            raise ValueError(f"Failed to read PDF document: {str(e)}")

        full_text = "\n\n".join(text_parts).strip()
        if not full_text:
            raise ValueError("Could not extract readable text from this PDF. It may be an image-only scanned document or password protected.")
        return clean_text(full_text)

    @classmethod
    def extract_text_from_docx(cls, file_path_or_stream) -> str:
        try:
            doc = docx.Document(file_path_or_stream)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            # Also extract text from tables if any
            table_texts = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                    if row_text:
                        table_texts.append(row_text)

            combined = "\n".join(paragraphs)
            if table_texts:
                combined += "\n\n" + "\n".join(table_texts)

            if not combined.strip():
                raise ValueError("The DOCX document is empty or contains no readable text.")
            return clean_text(combined)
        except Exception as e:
            raise ValueError(f"Failed to read DOCX document: {str(e)}")

    @classmethod
    def parse_file(cls, file_storage, save_dir: str) -> dict:
        is_valid, msg = cls.validate_file(file_storage)
        if not is_valid:
            raise ValueError(msg)

        filename = secure_filename(file_storage.filename)
        ext = filename.rsplit(".", 1)[1].lower()
        
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        file_storage.save(file_path)

        if ext == "pdf":
            raw_text = cls.extract_text_from_pdf(file_path)
        else:
            raw_text = cls.extract_text_from_docx(file_path)

        return {
            "filename": filename,
            "file_type": ext,
            "file_path": file_path,
            "raw_text": raw_text
        }
