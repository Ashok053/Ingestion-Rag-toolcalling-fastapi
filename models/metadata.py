from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class DocMetaData(Base):
    __tablename__= "documentsInfo"

    id = Column(Integer, primary_key=True, index = True)
    document_id = Column(String,unique=True, index = True)
    file_name = Column(String, nullable = False)
    file_type = Column(String, nullable=False)
    upload_time = Column(DateTime,default=datetime.now)
    chunk_count = Column(Integer, nullable=False)
    chunking_strategy = Column(String, nullable = False)
    chunk_size = Column(Integer,nullable = False)
    chunks = relationship("ChunkMetadata",back_populates="document")

class ChunkMetadata(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index = True)
    chunk_id = Column(String, unique=True, index = True)
    document_id = Column(String, ForeignKey('documentsInfo.document_id'))
    chunk_index = Column(Integer,nullable=False)
    text = Column(Text, nullable = False)
    char_count = Column(Integer, nullable = False)
    document = relationship("DocMetaData",back_populates="chunks")
