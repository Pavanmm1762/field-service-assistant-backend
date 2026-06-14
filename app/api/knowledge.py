from http.client import HTTPException
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.sync_knowledge_service import SyncKnowledgeService
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
from app.repositories.document_repository import document_repository

router = APIRouter(
    prefix="/api/knowledge",
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

# Endpoint to retrieve all documents and their metadata
@router.get("/documents")
def get_documents(
    db: Session = Depends(get_db),
):

    service = get_document_management_service(db)
    documents = service.list_documents()

    return [
        {
            "id": str(document.id),
            "filename": document.filename,
            "equipment": document.equipment,
            "status": document.status,
            "chunk_count": document.chunk_count,
            "created_at": document.created_at,
        }
        for document in documents
    ]

# Endpoint to retrieve document status summary
@router.get("/documents/status")
def get_document_status(
    db: Session = Depends(get_db),
):
    service = get_document_management_service(db)
    return service.get_document_status()

# Endpoint to delete a document by its ID
@router.delete("/documents/{document_id}")
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):

    service = get_document_management_service(db)
    document = service.delete_document(
        document_id
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "message": (
            "Document deleted successfully"
        ),
        "filename": document.filename,
    }

# Endpoint to reindex a document by its ID
@router.post("/documents/{document_id}/reindex")
def reindex_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    service = get_document_management_service(db)
    document = (
        service.reindex_document(
            document_id
        )
    )
    return {
        "message": "Reindex started",
        "filename": document.filename,
    }

@router.post("/documents/reindex-all")
def reindex_all_documents(
    db: Session = Depends(get_db),
):
    service = get_document_management_service(db)
    count = service.reindex_all_documents()
    return {
        "message": f"Reindex started for {count} documents",
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

# Factory method to create a document management service instance
def get_document_management_service(
    db: Session,
) -> DocumentManagementService:

    document_repository = (
        DocumentRepository(db)
    )

    document_chunk_repository = (
        DocumentChunkRepository(db)
    )

    return DocumentManagementService(
        document_repository=document_repository,
        document_chunk_repository=document_chunk_repository,
    )