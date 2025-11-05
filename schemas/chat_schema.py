from pydantic import BaseModel,Field
from typing import Optional, List

class ChatRequest(BaseModel):
    """Request for chat"""
    session_id : Optional[str] = None
    query : str

class ChatResponse(BaseModel):
    """Response for chat"""
    session_id : str
    query : str
    answer : str
    sources : List[str] = Field(default_factory=list)
