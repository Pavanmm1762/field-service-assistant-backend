from app.services.embedding_service import EmbeddingService
from app.services.vector_store import vector_store


class RAGService:

    def __init__(self):
        self.embedder = EmbeddingService()

    def retrieve(self, question: str):

        embedding = self.embedder.embed(question)

        results = vector_store.search(
            embedding=embedding,
            n_results=3
        )

        docs = results["documents"][0]

        return "\n\n".join(docs)


rag_service = RAGService()