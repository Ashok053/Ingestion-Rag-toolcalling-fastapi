from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database import init_db
from core.configuration import settings

from services.vectorsStore import init_qdrant_collection
from services.embeddings import get_embedding_dim

from api.docIngestion import router  as doc_ingestion_router

from api.conversationalRAG import router as chat_router
from api.booking_api import router as booking_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None,None]:
    print("\n1. initializing sqlite database")
    init_db()
    print("\n2. initializing qdrant vector database")
    embedding_dim = get_embedding_dim()
    print(f"embedding dimension : {embedding_dim}")

    init_qdrant_collection(
        collection_name = settings.QDRANT_COLLECTION,
        vector_size = embedding_dim,
        qdrant_host = settings.QDRANT_HOST,
        qdrant_port = settings.QDRANT_PORT
    )
    yield

app = FastAPI()

app.include_router(doc_ingestion_router)
app.include_router(chat_router)
app.include_router(booking_router)

@app.get('/health')
async def health_check():
    health_status = {
        "status" : "healthy",
        "services": {
            "api":"running",
            "database":"sqlite",
            "vector_db":"qdrant",
            "cache": "redis"
        },
        "config":{
            "qdrant_host": settings.QDRANT_HOST,
            "qdrant_port":settings.QDRANT_PORT,
            "collection":settings.QDRANT_COLLECTION
        }
    }
    return health_status


@app.get("/")
def read_root():
    return {"message": "welcome to the document ingestion and RAG API",
            "version": "1.0.0",
            "status":"running",
            "docs":"/docs",
            "endpoints":{
                "document_ingestion":"/api/docIngestion",
                "chat": "/api/chat",
                "booking": "/api/bookings"
            }
    }


@app.on_event("startup")
def on_startup():
    init_db()



