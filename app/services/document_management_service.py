
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
    
    def get_document_status(self):
        return (
            self.document_repository
            .get_status()
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

        self.document_repository.delete_by_id(
            document.id
        )

        return document
    
    def reindex_document(
        self,
        document_id,
    ):

        document = (
            self.document_repository.get_by_id(
                document_id
            )
        )

        if not document:
            return None

        return self.ingestion_service.reindex_document(
                document=document,
            )

    def reindex_all_documents(self):

        documents = (
            self.document_repository.get_all()
        )

        count = 0
        for document in documents:

            document = self.ingestion_service.reindex_document(
                document=document,
            )
            count += 1

        return count