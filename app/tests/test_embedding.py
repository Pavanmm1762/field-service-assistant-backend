from app.services.embedding_service import EmbeddingService

embedding_service = EmbeddingService()

embedding = embedding_service.embed(
    "How do I configure wireless settings?"
)

print(len(embedding))
print(embedding[:5])