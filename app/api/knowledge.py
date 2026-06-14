from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.sync_knowledge_service import SyncKnowledgeService, get_sync_service
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

router = APIRouter(
    prefix="api/knowledge",
    tags=["Knowledge"],
)

@router.post("/sync")
def sync_knowledge(
    db: Session = Depends(get_db),
):

    sync_service = get_sync_service(db)

    result = sync_service.sync(
        "data/knowledge"
    )

    return {
        "success": True,
        "message": result,
    }

# Factory method to create a sync service instance
def get_sync_service(
    db: Session,
) -> SyncKnowledgeService:

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

    return SyncKnowledgeService(
        document_repository=document_repository,
        document_management_service=management_service,
        document_ingestion_service=ingestion_service,
    )