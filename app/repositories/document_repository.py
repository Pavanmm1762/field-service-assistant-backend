from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models.document import Document


class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: UUID):
        return (
            self.db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

    def get_by_checksum(self, checksum: str):
        return (
            self.db.query(Document)
            .filter(Document.checksum == checksum)
            .first()
        )
    
    def get_by_file_path(
        self,
        file_path: str,
    ):
        return (
            self.db.query(Document)
            .filter(
                Document.file_path == file_path
            )
            .first()
        )
    
    def update(self, document: Document):
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, document: Document):
        self.db.delete(document)
        self.db.commit()

    def delete_by_id(self, document_id: UUID):
        document = (
            self.db.query(Document)
            .filter(
                Document.id == document_id
            )
            .first()
        )

        if not document:
            return None

        self.db.delete(document)

        self.db.commit()

        return document

    def list_all(self):
        return (
            self.db.query(Document)
            .order_by(Document.created_at.desc())
            .all()
        )
    
    def get_all(self):
        return (
            self.db.query(Document)
            .all()
        )

    def get_status(self):

        total_documents = (
            self.db.query(Document)
            .count()
        )

        indexed_documents = (
            self.db.query(Document)
            .filter(
                Document.status == "indexed"
            )
            .count()
        )

        pending_documents = (
            self.db.query(Document)
            .filter(
                Document.status == "pending"
            )
            .count()
        )

        failed_documents = (
            self.db.query(Document)
            .filter(
                Document.status == "failed"
            )
            .count()
        )

        total_chunks = (
            self.db.query(
                func.coalesce(
                    func.sum(
                        Document.chunk_count
                    ),
                    0
                )
            )
            .scalar()
        )

        return {
            "documents": total_documents,
            "indexed": indexed_documents,
            "pending": pending_documents,
            "failed": failed_documents,
            "chunks": total_chunks,
        }