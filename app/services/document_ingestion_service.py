from pathlib import Path
import time
import logging

from app.db.models.document import Document
from app.db.models.document_chunk import DocumentChunk
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.services.embedding_service import EmbeddingService
from app.services.pdf_loader import PDFLoader
from app.services.chunking_service import ChunkingService
from app.utils.checksum import generate_checksum

logger = logging.getLogger(__name__)

class DocumentIngestionService:

    MAX_RETRIES = 5
    BATCH_SIZE = 25

    TRANSIENT_ERRORS = [
        "429",
        "500",
        "502",
        "503",
        "504",
        "timeout",
        "connection",
        "rate limit",
    ]

    # constructor with dependency injection for repositories and services
    def __init__(
        self,
        document_repository: DocumentRepository,
        document_chunk_repository: DocumentChunkRepository,
        pdf_loader: PDFLoader,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
    ):
        self.document_repository = document_repository
        self.document_chunk_repository = (
            document_chunk_repository
        )
        self.pdf_loader = pdf_loader
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service

    # Main method to ingest a document: load, chunk, embed, and store
    def ingest_document(
        self,
        pdf_path: str,
        equipment: str,
    ):

        checksum = generate_checksum(pdf_path)

        existing_document = (
            self.document_repository.get_by_checksum(
                checksum
            )
        )

        if existing_document:
            logger.info("Document already exists")
            return existing_document

        document = Document(
            filename=Path(pdf_path).name,
            checksum=checksum,
            equipment=equipment,
            file_path=pdf_path,
            status="pending",
            chunk_count=0,
        )

        document = self.document_repository.create(
            document
        )

        try:
            
            self._index_document(
                document 
            )

            return document

        except Exception as e:

            self.document_repository.db.rollback()

            document.status = "failed"

            # Optional if model has column
            # if hasattr(
            #     document,
            #     "error_message",
            # ):
            #     document.error_message = str(e)

            self.document_repository.update(
                document
            )

            logger.error(
                f"Document ingestion failed: {e}"
            )

            raise

    # This method can be used for reindexing if needed 
    def reindex_document(
        self,
        document: Document,
    ):

        self.document_chunk_repository.delete_by_document_id(
            document.id
        )

        document.status = "pending"
        document.chunk_count = 0

        self.document_repository.update(
            document
        )

        return self._index_document(
            document
        )

    # Indexing logic is separated for better readability and potential reuse in other contexts (e.g. reindexing)
    def _index_document(
        self,
        document: Document,
    ):

        equipment = document.equipment
        pdf_path = document.file_path

        # document.status = "indexing"

        # self.document_repository.update(
        #     document
        # )

        text = self.pdf_loader.load(
            pdf_path
        )

        chunks = self.chunking_service.chunk_text(
            text
        )

        document.chunk_count = len(chunks)

        self.document_repository.update(
            document
        )

        # Optional:
        # Add this method in repository if you want
        # resume support after crash.
        existing_chunk_count = 0

        if hasattr(
            self.document_chunk_repository,
            "get_count_by_document_id",
        ):
            existing_chunk_count = (
                self.document_chunk_repository
                .get_count_by_document_id(
                    document.id
                )
            )
        logger.info(
            f"Processing {len(chunks)} chunks "
            f"(already stored: {existing_chunk_count})"
        )

        for index, chunk in enumerate(chunks):
            # Resume support
            if index < existing_chunk_count:
                continue

            embedding = None

            for attempt in range(
                self.MAX_RETRIES
            ):

                try:

                    embedding = (
                        self.embedding_service.embed(
                            chunk
                        )
                    )

                    break

                except Exception as e:

                    error = str(e).lower()

                    if any(
                        transient_error in error
                        for transient_error
                        in self.TRANSIENT_ERRORS
                    ):

                        wait_time = (
                            2 ** attempt
                        )

                        logger.info(
                            f"Chunk {index} failed. "
                            f"Retrying in "
                            f"{wait_time}s "
                            f"(attempt "
                            f"{attempt + 1}/"
                            f"{self.MAX_RETRIES})"
                        )

                        time.sleep(
                            wait_time
                        )

                        continue

                    raise

            if embedding is None:
                raise Exception(
                    f"Embedding generation "
                    f"failed for chunk "
                    f"{index}"
                )

            document_chunk = (
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    chunk_text=chunk,
                    embedding=embedding,
                    chunk_metadata={
                        "document_id": str(
                            document.id
                        ),
                        "filename": (
                            document.filename
                        ),
                        "equipment": equipment,
                        "chunk_index": index,
                    },
                )
            )

            self.document_chunk_repository.create(
                document_chunk
            )

            if (
                (index + 1)
                % self.BATCH_SIZE
                == 0
            ):
                self.document_chunk_repository.commit()
                logger.info(
                    f"Committed "
                    f"{index + 1} chunks"
                )

        self.document_chunk_repository.commit()

        document.status = "indexed"

        self.document_repository.update(
            document
        )

        return document