from app.db.database import SessionLocal

from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.document_ingestion_service import (
    DocumentIngestionService,
)


db = SessionLocal()

repo = DocumentRepository(db)

service = DocumentIngestionService(repo)

document = service.ingest_document(
    pdf_path="data/knowledge/wnr854t_setup_manual.pdf",
    equipment="Router",
)

print(document.id)
print(document.filename)