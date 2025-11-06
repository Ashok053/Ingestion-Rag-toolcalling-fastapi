from fastapi import APIRouter, HTTPException, UploadFile, Form, Depends, File
from sqlalchemy.orm import Session

import numpy as np

from core.database import get_db
from core.configuration import settings

from schemas.ingestion_schema import IngestResponse, ChunkMetaData

from services.documentService import DocumentService
from services.chunking import chunk_text
from services.embeddings import generate_embeddings
from services.vectorsStore import store_embeddings,init_qdrant_collection

router = APIRouter(prefix="/api/docIngestion", tags=['document ingestion'])


@router.post("/upload", response_model=IngestResponse)
async def upload_documents(
        file: UploadFile = File(..., description="pdf or txt file to upload"),
        strategy: str = Form(default="sentence", description="chunking strategy: 'sentence' or 'fixed'"),
        chunk_size: int = Form(default=500, ge=100, le=2000, description="size of chunks in character"),
        db: Session = Depends(get_db)
):
    """
    Upload and ingest a document: validate type, extract text, chunking, embedding and storing in qdrant and sqlite
    :param file: file to be uploaded
    :param strategy: chunking strategy
    :param chunk_size: target size of chunks
    :param db: database session
    :return: document id and ingestion details
    """
    try:
        # validate file type
        if not (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
            raise HTTPException(status_code=400, detail="invalid file type")

        if strategy not in ['sentence', 'fixed']:
            raise HTTPException(status_code=400, detail="invalid chunking strategy")

        print(f"processing file: {file.filename}")

        file_bytes = await file.read()
        try:
            text = DocumentService.extract_text(file.filename, file_bytes)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="no text found in file, check file")

        print(f"extracted {len(text)} characters")

        overlap = 100 if strategy == 'sentence' else 128
        chunks = chunk_text(
            text=text,
            strategy=strategy,
            chunk_size=chunk_size,
            overlap=overlap
        )

        if not chunks:
            raise HTTPException(status_code=400, detail="fail to generate chunk")

        print(f"created {len(chunks)} chunks")

        # generate embeddings - returns numpy array
        embeddings: np.ndarray = generate_embeddings(chunks)
        print(f"generated embeddings of shape {embeddings.shape}")

        file_type = file.filename.split('.')[-1]
        try:
            doc_id = DocumentService.save_document_metadata(
                db=db,
                file_name=file.filename,
                file_type=file_type,
                chunk_count=len(chunks),
                strategy=strategy,
                chunk_size=chunk_size
            )
        except TypeError as e:
            raise HTTPException(status_code=500, detail=f"internal error: invalid metadata argument {str(e)}")

        DocumentService.save_chunk_metadata(
            db=db,
            document_id=doc_id,
            chunks=chunks
        )

        print(f"saved metadata for document {doc_id}")
        print(f"Type of embeddings: {type(embeddings)}, Type of one embedding: {type(embeddings[0])}")

        store_embeddings(
            chunks=chunks,
            embeddings=embeddings.tolist(),
            doc_id=doc_id,
            collection_name=settings.QDRANT_COLLECTION
        )

        print(f"document {doc_id} ingested successfully")

        chunk_metadata_list = [
            ChunkMetaData(
                chunk_text=chunk['text'],
                chunk_index=chunk['chunk_index'],
                chunk_strategy=chunk['strategy']
            )
            for chunk in chunks
        ]

        return IngestResponse(
            file_name=file.filename,
            file_type=file_type,
            item_id=doc_id,
            message=f"Document {doc_id} ingested successfully",
            chunks=len(chunks),
            total_chunks=chunk_metadata_list
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"internal server error: {str(e)}")