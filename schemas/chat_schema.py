from pydantic import BaseModel,Field
from typing import Optional, List

class ChatRequest(BaseModel):
    session_id : Optional[str] = None
    query : str

class ChatResponse(BaseModel):
    session_id : str
    query : str
    answer : str
    sources : List[str] = Field(default_factory=list)
