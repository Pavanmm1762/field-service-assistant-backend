from app.db.database import SessionLocal
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.services.embedding_service import (
    EmbeddingService,
)

SIMILARITY_THRESHOLD = 0.8

class RAGService:

    def __init__(self):
        self.embedder = EmbeddingService()

    def retrieve(
        self,
        question: str,
    ):

        embedding = self.embedder.embed(
            question
        )

        db = SessionLocal()

        try:

            repository = (
                DocumentChunkRepository(db)
            )

            results =  repository.search(
                embedding=embedding,
                limit=3,
            )

            if not results:
                return ""

            context_parts = []

            for result in results:

                if result["distance"] > SIMILARITY_THRESHOLD:
                    continue

                metadata = (
                    result.get("metadata")
                    or {}
                )

                equipment = metadata.get(
                    "equipment",
                    "Unknown",
                )

                filename = metadata.get(
                    "filename",
                    "Unknown",
                )

                context_parts.append(
                    f"""
                    Source: {filename}
                    Equipment: {equipment}

                    {result['chunk_text']}
                    """
                )

            return "\n\n".join(
                context_parts
            )


        finally:
            db.close()

    # 
    async def retrieve_async(
        self,
        question: str,
        equipment: str | None = None,
    ):

        embedding = await self.embedder.embed_async(
            question
        )

        db = SessionLocal()

        try:

            repository = (
                DocumentChunkRepository(db)
            )

            results = repository.search(
                embedding=embedding,
                limit=3,
                equipment=equipment,
            )

            if not results:
                 return {
                    "context": "",
                    "sources": [],
                    "manual_found": False,
                }

            context_parts = []
            sources = []

            for result in results:

                if result["distance"] > SIMILARITY_THRESHOLD:
                    continue

                metadata = (
                    result.get("metadata")
                    or {}
                )

                chunk_equipment  = metadata.get(
                    "equipment",
                    "Unknown",
                )

                filename = metadata.get(
                    "filename",
                    "Unknown",
                )

                source = {
                    "filename": filename,
                    "equipment": chunk_equipment,
                }

                if source not in sources:
                    sources.append(source)

                context_parts.append(
                    f"""
                    Source: {filename}
                    Equipment: {chunk_equipment }

                    {result['chunk_text']}
                    """
                )

            if not context_parts:
                return {
                    "context": "",
                    "sources": [],
                    "manual_found": False,
                }
            
            return {
                "context": "\n\n".join(context_parts),
                "sources": sources,
                "manual_found": True,
            }

        finally:
            db.close()

rag_service = RAGService()