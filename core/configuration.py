import os
from dotenv import load_dotenv

load_dotenv()

from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    """Application settings"""


    #Database
    DATABASE_URL : str = "sqlite:///./app_data.db"

    #redis
    REDIS_URL : str = "redis://localhost:6379"

    #Qdrant
    QDRANT_HOST : str = "localhost"
    QDRANT_PORT : int = 6333
    QDRANT_COLLECTION : str = "documents"
    QDRANT_URL : str = "http://localhost:6333"

    #embedding
    EMBEDDING_MODEL : str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION : int = 384



    #llm configuration
    GROQ_API_KEY : str =os.getenv("GROQ_API_KEY")
    LLM_MODEL : str = os.getenv("LLM_MODEL")

    class Config:
        env_file = ".env"

settings = Settings()
