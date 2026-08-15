from typing import List, Dict, Any
from src.rag.embeddings import SimpleEmbeddingModel

class DocumentRetriever:
    def __init__(self):
        self.embedding_model = SimpleEmbeddingModel()
        self.documents: List[Dict[str, Any]] = []

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None):
        vector = self.embedding_model.embed_text(text)
        self.documents.append({
            "id": doc_id,
            "text": text,
            "vector": vector,
            "metadata": metadata or {}
        })

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.documents:
            return []
        query_vec = self.embedding_model.embed_text(query)
        scored_docs = []
        for doc in self.documents:
            sim = self.embedding_model.cosine_similarity(query_vec, doc["vector"])
            scored_docs.append((sim, doc))
        
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for sim, doc in scored_docs[:top_k]]
