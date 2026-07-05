"""Document Ingester — Processes uploaded files into Mental Models.

Extracts text from PDFs, text files, and markdown documents,
chunks them intelligently, and stores them in the Mental Models tier
as canonical knowledge for the agent.
"""

import os
import re
from typing import BinaryIO, Optional
from qwentree.memory.mental_models import MentalModels


class DocumentIngester:
    """Ingests documents into the Mental Models knowledge base."""

    SUPPORTED_EXTENSIONS = {
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".csv": "text/csv",
        ".json": "application/json",
        ".yaml": "application/x-yaml",
        ".yml": "application/x-yaml",
    }

    # Try to import optional PDF support
    try:
        import PyPDF2
        SUPPORTED_EXTENSIONS[".pdf"] = "application/pdf"
        HAS_PDF = True
    except ImportError:
        HAS_PDF = False

    try:
        import docx
        SUPPORTED_EXTENSIONS[".docx"] = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        HAS_DOCX = True
    except ImportError:
        HAS_DOCX = False

    def __init__(self):
        self.mm = MentalModels()

    def ingest(self, file_name: str, file_content: bytes,
               source_label: Optional[str] = None) -> dict:
        """Ingest a file into Mental Models. Returns ingestion report."""
        ext = os.path.splitext(file_name)[1].lower()
        source = source_label or file_name

        if ext not in self.SUPPORTED_EXTENSIONS:
            return {
                "success": False,
                "error": f"Unsupported format: {ext}. Supported: {', '.join(self.SUPPORTED_EXTENSIONS.keys())}",
                "chunks": 0,
            }

        # Extract text
        text = self._extract_text(file_name, file_content, ext)
        if not text or not text.strip():
            return {
                "success": False,
                "error": "No extractable text found in the file",
                "chunks": 0,
            }

        # Chunk and store
        chunks = self._chunk_text(text, file_name)
        stored = 0
        for i, chunk in enumerate(chunks):
            doc_id = self.mm.add_knowledge(
                content=chunk,
                source=source,
                tags=[f"document", ext[1:], f"chunk_{i}"],
            )
            stored += 1

        return {
            "success": True,
            "file": file_name,
            "source": source,
            "total_chars": len(text),
            "chunks": stored,
            "error": None,
        }

    def ingest_text(self, title: str, content: str,
                    source: Optional[str] = None) -> dict:
        """Directly ingest a text blob as a Mental Model."""
        chunks = self._chunk_text(content, title)
        stored = 0
        for i, chunk in enumerate(chunks):
            self.mm.add_knowledge(
                content=chunk,
                source=source or f"manual: {title}",
                tags=["manual", f"chunk_{i}"],
            )
            stored += 1
        return {
            "success": True,
            "title": title,
            "chunks": stored,
            "total_chars": len(content),
        }

    def _extract_text(self, file_name: str, content: bytes, ext: str) -> str:
        """Extract text from a file based on its extension."""
        if ext == ".pdf" and self.HAS_PDF:
            return self._extract_pdf(content)
        elif ext == ".docx" and self.HAS_DOCX:
            return self._extract_docx(content)
        else:
            # TXT, MD, CSV, JSON, YAML — read as text
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return content.decode("latin-1")

    def _extract_pdf(self, content: bytes) -> str:
        """Extract text from a PDF file."""
        import PyPDF2
        import io
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    def _extract_docx(self, content: bytes) -> str:
        """Extract text from a DOCX file."""
        import docx
        import io
        doc = docx.Document(io.BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs if p.text])

    def _chunk_text(self, text: str, source: str,
                    max_chunk_size: int = 1500,
                    overlap: int = 100) -> list[str]:
        """Split text into semantic chunks of roughly equal size."""
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        if not text:
            return []

        # Try to split by paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)
            if current_size + para_size <= max_chunk_size:
                current_chunk.append(para)
                current_size += para_size
            else:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                # If a single paragraph is too big, split by sentences
                if para_size > max_chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    temp = []
                    temp_size = 0
                    for sent in sentences:
                        if temp_size + len(sent) <= max_chunk_size:
                            temp.append(sent)
                            temp_size += len(sent)
                        else:
                            if temp:
                                chunks.append(" ".join(temp))
                            temp = [sent]
                            temp_size = len(sent)
                    if temp:
                        chunks.append(" ".join(temp))
                else:
                    current_chunk = [para]
                    current_size = para_size

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks if chunks else [text[:max_chunk_size]]

    @classmethod
    def get_supported_formats(cls) -> str:
        """Return a human-readable list of supported formats."""
        formats = [".txt", ".md", ".csv", ".json"]
        if cls.HAS_PDF:
            formats.append(".pdf")
        if cls.HAS_DOCX:
            formats.append(".docx")
        return ", ".join(formats)
