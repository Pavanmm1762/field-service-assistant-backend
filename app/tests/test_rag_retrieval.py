from app.services.rag_service import rag_service

question = "How do I configure wireless security?"

context = rag_service.retrieve(question)

print(context)