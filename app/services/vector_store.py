import chromadb


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="data/chroma"
        )

        self.collection = self.client.get_or_create_collection(
            name="knowledge_base"
        )

    def add_document(
        self,
        chunk_id: str,
        chunk: str,
        embedding: list[float],
        metadata: dict
    ):

        self.collection.add(
            ids=[chunk_id],
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def search(
        self,
        embedding: list[float],
        n_results: int = 3
    ):

        return self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )


vector_store = VectorStore()