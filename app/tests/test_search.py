# app/tests/test_search.py

from app.services.embedding_service import EmbeddingService
from app.services.vector_store import vector_store

embedder = EmbeddingService()

question = "How do I configure wireless security?"

embedding = embedder.embed(question)

results = vector_store.search(
    embedding=embedding,
    n_results=3
)

for i, doc in enumerate(results["documents"][0], start=1):
    print(f"\n--- Result {i} ---\n")
    print(doc[:500])