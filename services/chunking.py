from typing import List, Dict
import re

def chunk_by_sentence(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """
    Split text into chunks by sentences, preserving sentence boundaries.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_index": len(chunks),
                "strategy": "sentence",
                "char_count": len(current_chunk.strip())
            })
            # keep overlap
            words = current_chunk.split()
            overlap_text = " ".join(words[-overlap//5:]) if len(words) > 5 else ""
            current_chunk = (overlap_text + " " + sentence).strip() if overlap_text else sentence
        else:
            current_chunk += (" " if current_chunk else "") + sentence

    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "chunk_index": len(chunks),
            "strategy": "sentence",
            "char_count": len(current_chunk.strip())
        })

    return chunks


def chunk_by_fixed_size(text: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
    """
    Split text into fixed-size chunks with sliding window.
    """
    text = text.strip()
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        chunks.append({
            "text": chunk_text.strip(),
            "chunk_index": len(chunks),
            "strategy": "fixed",
            "char_count": len(chunk_text.strip())
        })
        start += chunk_size - overlap

    return chunks


def chunk_text(text: str, strategy: str = "sentence", chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
    """
    Chunk text using the selected strategy.
    """
    if not text or not text.strip():
        return []

    if strategy == "sentence":
        return chunk_by_sentence(text, chunk_size, overlap)
    elif strategy == "fixed":
        return chunk_by_fixed_size(text, chunk_size, overlap)
    else:
        raise ValueError(f"Unknown strategy: {strategy}. Use 'sentence' or 'fixed'.")
