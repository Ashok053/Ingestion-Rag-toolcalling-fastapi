# RAG Document System

A simple RAG (Retrieval-Augmented Generation) system with document ingestion, conversational AI, and interview booking capabilities.

## Features

### Part 1: Document Ingestion
- Upload PDF and TXT files
- Two chunking strategies (sentence-based and fixed-size)
- Generate embeddings using sentence-transformers
- Store vectors in Qdrant
- Save metadata in SQLite

### Part 2: Conversational RAG
- Custom RAG implementation (no RetrievalQAChain)
- Chat with uploaded documents
- Automatic tool calling (RAG or Booking)
- Redis for conversation memory
- Multi-turn conversation support
- Interview booking through chat

## Tech Stack

- **FastAPI** - REST API framework
- **SQLite** - Metadata storage
- **Qdrant** - Vector database
- **Redis** - Chat memory
- **Sentence-Transformers** - Text embeddings
- **Groq** - LLM for answer generation
- **SQLAlchemy** - ORM

## Project Structure

```
rag-system/
├── api/
│   ├── booking_api.py          # Booking endpoints
│   ├── conversationalRAG.py    # Chat endpoints
│   └── docIngestion.py         # Document upload endpoints
├── core/
│   ├── configuration.py        # Settings
│   ├── database.py             # SQLAlchemy setup
│   └── redis_manager.py        # Redis operations
├── models/
│   ├── booking.py              # Booking model
│   └── metadata.py             # Document models
├── schemas/
│   ├── booking_schema.py       # Booking schemas
│   ├── chat_schema.py          # Chat schemas
│   └── ingestion_schema.py     # Document schemas
├── services/
│   ├── booking.py              # Booking logic
│   ├── chunking.py             # Text chunking
│   ├── documentService.py      # Document operations
│   ├── embeddings.py           # Generate embeddings
│   ├── llm_service.py          # Groq LLM
│   ├── rag_service.py          # RAG logic
│   ├── tool_service.py         # Tool calling
│   └── vectorsStore.py         # Qdrant operations
├── main.py                     # FastAPI app
└── requirements.txt            # Dependencies
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Required Services

```bash
# Start Qdrant (vector database)
docker run -p 6333:6333 qdrant/qdrant

# Start Redis (chat memory)
docker run -p 6379:6379 redis
```

### 3. Configure API Key

Add your Groq API key in `core/configuration.py`:

```python
GROQ_API_KEY = "your-groq-api-key-here"
```

Get free API key from: https://console.groq.com

### 4. Run Application

```bash
uvicorn main:app --reload
```

API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Usage

### 1. Upload Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@document.pdf" \
  -F "strategy=sentence" \
  -F "chunk_size=500"
```

**Strategies:**
- `sentence` - Splits by sentences (better for Q&A)
- `fixed` - Fixed-size chunks with overlap

### 2. Chat with Documents

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the document about?"
  }'
```

### 3. Book Interview via Chat

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Book interview for John Doe, john@email.com, 2025-11-15, 10:00"
  }'
```

### 4. List All Bookings

```bash
curl http://localhost:8000/api/v1/bookings/
```

## API Endpoints

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/` - List all documents
- `GET /api/v1/documents/{id}` - Get document details

### Chat (RAG)
- `POST /api/v1/chat/` - Chat with documents or book interview
- `GET /api/v1/chat/history/{session_id}` - Get chat history
- `DELETE /api/v1/chat/history/{session_id}` - Clear history

### Bookings
- `POST /api/v1/bookings/` - Create booking (direct)
- `GET /api/v1/bookings/` - List all bookings
- `GET /api/v1/bookings/{id}` - Get booking details
- `GET /api/v1/bookings/email/{email}` - Get bookings by email

## How It Works

### Document Ingestion Pipeline
```
Upload File → Extract Text → Chunk Text → Generate Embeddings → Store in Qdrant → Save Metadata in SQLite
```

### Conversational RAG Pipeline
```
User Query → Detect Intent (RAG or Booking) → 
  If Booking: Extract Info → Create Booking
  If Question: Search Qdrant → Generate Answer with LLM
→ Save to Redis → Return Response
```

### Tool Calling
The system automatically detects user intent:
- Questions about documents → Uses RAG (searches Qdrant, generates answer)
- Booking requests → Extracts info and creates booking

## Example Conversations

**Question:**
```
User: "What is Python?"
Bot: "Based on the documents, Python is a high-level programming language..."
```

**Booking:**
```
User: "Book interview for Ram, ram@example.com, 2025-11-15, 10:00"
Bot: "Interview booked! Name: Ram sharma, Email: ram@example.com..."
```

**Multi-turn:**
```
User: "What is the main topic?"
Bot: "The document discusses machine learning..."
User: "Can you explain more about that?"
Bot: "Sure! Machine learning involves..." [Uses context from previous message]
```

## Database Schema

### SQLite Tables

**documents**
- id, filename, file_type, chunk_count, chunking_strategy, chunk_size, upload_time

**chunks**
- id, chunk_id, document_id, chunk_index, text, char_count

**bookings**
- id, name, email, date, time, created_at

### Qdrant Collection
- Collection: `documents`
- Vector size: 384 (from all-MiniLM-L6-v2)
- Distance: Cosine similarity

### Redis Keys
- Pattern: `chat:{session_id}`
- TTL: 1 hour
- Max messages: 10 per session

## Troubleshooting

**Qdrant connection error:**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Redis connection error:**
```bash
docker run -p 6379:6379 redis
```

**LLM not working:**
- Check GROQ_API_KEY in configuration.py
- Get free key from console.groq.com

**No text extracted from PDF:**
- Ensure PDF has selectable text (not scanned image)
- Try with .txt file first



