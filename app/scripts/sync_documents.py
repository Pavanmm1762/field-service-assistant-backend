from app.db.database import SessionLocal

from app.repositories.document_repository import (
    DocumentRepository,
)
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)

from app.services.document_ingestion_service import (
    DocumentIngestionService,
)
from app.services.document_management_service import (
    DocumentManagementService,
)
from app.services.sync_knowledge_service import (
    SyncKnowledgeService,
)

from app.services.pdf_loader import PDFLoader
from app.services.chunking_service import (
    ChunkingService,
)
from app.services.embedding_service import (
    EmbeddingService,
)


def main():

    db = SessionLocal()

    try:

        document_repository = (
            DocumentRepository(db)
        )

        document_chunk_repository = (
            DocumentChunkRepository(db)
        )

        ingestion_service = (
            DocumentIngestionService(
                document_repository=document_repository,
                document_chunk_repository=document_chunk_repository,
                pdf_loader=PDFLoader(),
                chunking_service=ChunkingService(),
                embedding_service=EmbeddingService(),
            )
        )

        management_service = (
            DocumentManagementService(
                document_repository=document_repository,
                document_chunk_repository=document_chunk_repository,
            )
        )

        sync_service = (
            SyncKnowledgeService(
                document_repository=document_repository,
                document_management_service=management_service,
                document_ingestion_service=ingestion_service,
            )
        )

        sync_service.sync(
            "data/knowledge"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()