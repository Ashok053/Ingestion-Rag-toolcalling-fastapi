from pydantic import BaseModel, Field
from typing import List

class ChunkMetaData(BaseModel):
    chunk_text: str = Field(..., min_length=1, description="Content of the data chunk")
    chunk_index: int = Field(..., ge=0, description="Zero-based index of chunk in file")
    chunk_strategy: str = Field(..., min_length=2, description="Strategy used to chunk the file")

    class Config:
        from_attributes = True

class IngestResponse(BaseModel):
    file_name: str = Field(..., description="Name of ingested file")
    file_type: str = Field(..., min_length=1, description="Type of ingested file")
    item_id: str = Field(..., description="Unique identifier for ingested document")
    message: str = Field(..., description="Detailed message about document/text ingestion")
    total_chunks: List[ChunkMetaData] = Field(..., description="List of all chunk metadata")

    @property
    def chunks(self) -> int:
        """Return the number of chunks"""
        return len(self.total_chunks)

    class Config:
        from_attributes = True
