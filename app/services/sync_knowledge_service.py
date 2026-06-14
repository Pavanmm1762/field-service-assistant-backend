import logging
from pathlib import Path

from app.utils.checksum import (
    generate_checksum,
)

logger = logging.getLogger(__name__)

class SyncKnowledgeService:

    def __init__(
        self,
        document_repository,
        document_management_service,
        document_ingestion_service,
    ):
        self.document_repository = (
            document_repository
        )

        self.document_management_service = (
            document_management_service
        )

        self.document_ingestion_service = (
            document_ingestion_service
        )

    def sync(
        self,
        knowledge_path: str,
    ):
        new_count = 0
        updated_count = 0
        unchanged_count = 0
        removed_count = 0
        
        knowledge_dir = Path(
            knowledge_path
        )

        existing_documents = {
            document.file_path: document
            for document in (
                self.document_repository
                .get_all()
            )
        }

        discovered_files = set()

        for pdf_file in knowledge_dir.rglob(
            "*.pdf"
        ):
            # for jupyter notebook checkpoints, skip them
            if ".ipynb_checkpoints" in pdf_file.parts:
                continue

            file_path = str(pdf_file)

            discovered_files.add(
                file_path
            )

            checksum = (
                generate_checksum(
                    file_path
                )
            )

            existing_document = (
                existing_documents.get(
                    file_path
                )
            )

            if not existing_document:

                logger.info(
                    f"[NEW] {pdf_file.name}"
                )

                self.document_ingestion_service.ingest_document(
                    pdf_path=file_path,
                    equipment=pdf_file.parent.name,
                )

                new_count += 1
                continue

            if (
                existing_document.checksum
                != checksum
            ):
                updated_count += 1

                logger.info(
                    f"[UPDATED] {pdf_file.name}"
                )

                self.document_ingestion_service.reindex_document(
                    existing_document.id
                )

            else:
                unchanged_count += 1
                logger.info(
                    f"[UNCHANGED] {pdf_file.name}"
                )

        for (
            file_path,
            document,
        ) in existing_documents.items():

            if (
                file_path
                not in discovered_files
            ):

                logger.info(
                    f"[REMOVED] {document.filename}"
                )

                self.document_management_service.delete_document(
                    document.id
                )

                removed_count += 1

        summary = {
            "new": new_count,
            "updated": updated_count,
            "unchanged": unchanged_count,
            "removed": removed_count,
        }
        return summary
    