from pathlib import Path
import time

from app.services.pdf_loader import PDFLoader
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import vector_store

loader = PDFLoader()
chunker = ChunkingService()
embedder = EmbeddingService()

pdf_path = "data/knowledge/wnr854t_setup_manual.pdf"

text = loader.load(pdf_path)

chunks = chunker.chunk_text(text)

existing_count = vector_store.collection.count()

print(f"Already Stored: {existing_count}")
print(f"Total Chunks: {len(chunks)}")

for i, chunk in enumerate(chunks):

    if i < existing_count:
        print(f"Skipping chunk {i}")
        continue

    while True:

        try:

            embedding = embedder.embed(chunk)

            vector_store.add_document(
                chunk_id=f"router-{i}",
                chunk=chunk,
                embedding=embedding,
                metadata={
                    "equipment": "Router",
                    "source": Path(pdf_path).name
                }
            )

            print(f"Stored chunk {i}")

            # Stay below rate limits
            time.sleep(5)

            break

        except Exception as e:

            error = str(e)

            if "429" in error:

                for remaining in range(60, 0, -1):
                    print(f"\rRate limit hit on chunk {i}. Waiting {remaining} seconds...", end="", flush=True)

                    time.sleep(1)

                print() 
                continue

            print(f"Failed chunk {i}: {error}")
            break

print("Ingestion Complete")