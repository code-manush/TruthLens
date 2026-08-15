from typing import List, Dict, Any, Optional
from src.rag.retriever import DocumentRetriever
from src.llm.ollama_client import OllamaClient

class RAGPipeline:
    def __init__(self, retriever: Optional[DocumentRetriever] = None, llm_client: Optional[OllamaClient] = None):
        self.retriever = retriever or DocumentRetriever()
        self.llm_client = llm_client or OllamaClient()

    def index_knowledge_base(self, docs: List[Dict[str, str]]):
        for idx, doc in enumerate(docs):
            self.retriever.add_document(
                doc_id=doc.get("id", f"doc_{idx}"),
                text=doc.get("text", ""),
                metadata=doc.get("metadata", {})
            )

    def query(self, claim_statement: str) -> Dict[str, Any]:
        relevant_docs = self.retriever.retrieve(claim_statement, top_k=2)
        context_str = "\n".join([d["text"] for d in relevant_docs]) if relevant_docs else "No reference context found."
        
        prompt = f"""
Given the following context and claim statement, evaluate if the claim is SUPPORTED, CONTRADICTED, or UNVERIFIED.

Context:
{context_str}

Claim:
{claim_statement}

Respond strictly in JSON format with keys "verdict", "confidence" (0.0 to 1.0), and "evidence" (string).
"""
        response = self.llm_client.generate_json(prompt)
        if "verdict" not in response:
            response["verdict"] = "UNVERIFIED"
            response["confidence"] = 0.5
            response["evidence"] = context_str
        return response
