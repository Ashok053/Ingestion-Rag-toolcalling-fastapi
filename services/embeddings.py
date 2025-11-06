from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np

embedding_model = SentenceTransformer("all-MiniLM-l6-v2")

def generate_embeddings(chunks: List[Dict]) -> np.ndarray :
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedding_model.encode(texts, show_progress_bar=True)
    return embeddings

def get_embedding_dim() -> int:
    return embedding_model.get_sentence_embedding_dimension()

