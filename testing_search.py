import numpy as np
from services.embeddings import generate_embeddings
from services.vectorsStore import search_similar_chunks

# Example query
query = "explain about the mission vission and what codeforchange is doing with codefest"

# Generate embedding for the query
query_embedding = generate_embeddings([{"text": query}])[0]

# Search top 5 similar chunks
results = search_similar_chunks(query_embedding, top_k=5)

# Print results
for r in results:
    print(f"Score: {r['score']:.4f}, Text: {r['text'][:200]}...\n")
