import os
import PyPDF2
import pdfplumber
from docx import Document
from typing import Optional
from app.core.config import settings


class ResumeParser:
    """Resume text extraction service"""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""

        # Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text
        except Exception as e:
            print(f"pdfplumber failed: {e}")

        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Failed to extract PDF text: {e}")

        return text

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"Failed to extract DOCX text: {e}")

    @staticmethod
    def extract_text_from_doc(file_path: str) -> str:
        """Extract text from DOC file"""
        # For .doc files, we'd need additional libraries like antiword or textract
        # For now, raise an error with instructions
        raise NotImplementedError(
            "DOC format requires conversion. Please upload DOCX or PDF format."
        )

    @staticmethod
    def extract_text(file_path: str, file_extension: str) -> str:
        """Extract text from resume file based on extension"""
        file_extension = file_extension.lower().strip('.')

        if file_extension == 'pdf':
            return ResumeParser.extract_text_from_pdf(file_path)
        elif file_extension == 'docx':
            return ResumeParser.extract_text_from_docx(file_path)
        elif file_extension == 'doc':
            return ResumeParser.extract_text_from_doc(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    @staticmethod
    def validate_file(file_path: str, file_size: int) -> tuple[bool, Optional[str]]:
        """Validate resume file"""
        # Check file exists
        if not os.path.exists(file_path):
            return False, "File does not exist"

        # Check file size
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
        if file_size > max_size:
            return False, f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"

        # Check extension
        extension = os.path.splitext(file_path)[1].lower().strip('.')
        if extension not in settings.ALLOWED_FILE_EXTENSIONS:
            return False, f"File type .{extension} not allowed. Allowed: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}"

        return True, None
