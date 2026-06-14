# app/tests/test_search.py
from app.services.rag_service import (
    rag_service,
)

question = "How do I replace the UPS battery?"

print(
    rag_service.retrieve(
        question=question,
    )
)