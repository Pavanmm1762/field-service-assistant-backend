from app.services.pdf_loader import PDFLoader
from app.services.chunking_service import ChunkingService

loader = PDFLoader()
chunker = ChunkingService()

text = loader.load(
    "data/knowledge/wnr854t_setup_manual.pdf"
)

chunks = chunker.chunk_text(text)

print(f"Chunks: {len(chunks)}")

print(chunks[0])