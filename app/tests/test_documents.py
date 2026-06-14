from app.db.database import SessionLocal

from app.repositories.document_repository import (
    DocumentRepository,
)
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.services.document_management_service import (
    DocumentManagementService,
)

db = SessionLocal()

service = (
    DocumentManagementService(
        document_repository=DocumentRepository(
            db
        ),
        document_chunk_repository=DocumentChunkRepository(
            db
        ),
    )
)

documents = (
    service.list_documents()
)

for document in documents:

    print(
        document.id,
        document.filename,
        document.status,
        document.chunk_count,
    )

db.close()