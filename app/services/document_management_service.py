from app.repositories.document_repository import (
    DocumentRepository,
)
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)


class DocumentManagementService:

    def __init__(
        self,
        document_repository,
        document_chunk_repository,
    ):
        self.document_repository = (
            document_repository
        )

        self.document_chunk_repository = (
            document_chunk_repository
        )

    def list_documents(self):
        return (
            self.document_repository
            .list_all()
        )

    def delete_document(
        self,
        document_id,
    ):

        document = (
            self.document_repository
            .get_by_id(
                document_id
            )
        )

        if not document:
            return False

        self.document_chunk_repository.delete_by_document_id(
            document.id
        )

        self.document_repository.delete(
            document
        )

        return True