from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models.document_chunk import DocumentChunk


class DocumentChunkRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, chunk: DocumentChunk):
        self.db.add(chunk)

    def bulk_create(self, chunks: list[DocumentChunk]):
        self.db.add_all(chunks)

    def commit(self):
        self.db.commit()

    def delete_by_document_id(
        self,
        document_id: UUID,
    ):
        (
            self.db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id
            )
            .delete()
        )

        self.db.commit()

    def get_count_by_document_id(
        self,
        document_id: UUID,
    ):
        return (
            self.db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id
            )
            .count()
        )
    
    def search(
        self,
        embedding: list[float],
        equipment: str | None = None,
        limit: int = 5,
    ):

        vector = "[" + ",".join(map(str, embedding)) + "]"

        if equipment:

            result = self.db.execute(
                text(
                    """
                    SELECT
                        chunk_text,
                        chunk_metadata,
                        embedding <=> CAST(:embedding AS vector) AS distance
                    FROM document_chunks
                    WHERE chunk_metadata->>'equipment' = :equipment
                    ORDER BY distance
                    LIMIT :limit
                    """
                ),
                {
                    "embedding": vector,
                    "equipment": equipment,
                    "limit": limit,
                },
            )

            rows = result.fetchall()

            if rows:
                return [
                    {
                        "chunk_text": row.chunk_text,
                        "metadata": row.chunk_metadata,
                        "distance": float(row.distance),
                    }
                    for row in rows
                ]

        result = self.db.execute(
            text(
                """
                SELECT
                    chunk_text,
                    chunk_metadata,
                    embedding <=> CAST(:embedding AS vector) AS distance
                FROM document_chunks
                ORDER BY distance
                LIMIT :limit
                """
            ),
            {
                "embedding": vector,
                "limit": limit,
            },
        )

        return [
            {
                "chunk_text": row.chunk_text,
                "metadata": row.chunk_metadata,
                "distance": float(row.distance),
            }
            for row in result.fetchall()
        ]