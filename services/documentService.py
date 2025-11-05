from sqlalchemy.orm import Session
from models.metadata import DocMetaData, ChunkMetadata
from typing import List, Dict
import uuid
import io
import PyPDF2


class DocumentService:
    """Handles document ingestion logic."""

    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            return "\n".join(page.extract_text() or "" for page in pdf_reader.pages).strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")

    @staticmethod
    def extract_text_from_txt(file_bytes: bytes) -> str:
        """Extract text from TXT file."""
        for encoding in ("utf-8", "latin-1"):
            try:
                return file_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError("Failed to decode TXT file")

    @staticmethod
    def extract_text(filename: str, file_bytes: bytes) -> str:
        """Extract text from file based on extension."""
        ext = filename.lower().split(".")[-1]
        if ext == "pdf":
            return DocumentService.extract_text_from_pdf(file_bytes)
        elif ext == "txt":
            return DocumentService.extract_text_from_txt(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {ext}. Only .pdf and .txt allowed.")

    @staticmethod
    def save_document_metadata(
        db: Session, file_name: str, file_type: str, chunk_count: int, strategy: str, chunk_size: int
    ) -> str:
        """Save document metadata and return document ID."""
        doc_id = str(uuid.uuid4())[:12]
        doc = DocMetaData(
            document_id=doc_id,
            file_name=file_name,
            file_type=file_type,
            chunk_count=chunk_count,
            chunking_strategy=strategy,
            chunk_size=chunk_size
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc_id

    @staticmethod
    def save_chunk_metadata(db: Session, document_id: str, chunks: List[Dict]):
        """Save all chunk metadata for a document."""
        for i, chunk in enumerate(chunks):
            db.add(
                ChunkMetadata(
                    chunk_id=f"{document_id}_chunk_{i}",
                    document_id=document_id,
                    chunk_index=i,
                    text=chunk["text"],
                    char_count=chunk["char_count"]
                )
            )
        db.commit()

    @staticmethod
    def get_all_documents(db: Session):
        """Get all documents from database."""
        return db.query(DocMetaData).order_by(DocMetaData.upload_time.desc()).all()

    @staticmethod
    def get_document_by_id(db: Session, doc_id: str):
        """Get a document by ID."""
        return db.query(DocMetaData).filter(DocMetaData.document_id == doc_id).first()
