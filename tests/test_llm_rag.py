from src.llm.ollama_client import OllamaClient
from src.llm.llm_analyzer import LLMAnalyzer
from src.rag.embeddings import SimpleEmbeddingModel
from src.rag.retriever import DocumentRetriever
from src.rag.rag_pipeline import RAGPipeline

def test_ollama_client_fallback():
    client = OllamaClient(base_url="http://localhost:99999")  # Intentional offline port
    res = client.generate("Hello test")
    assert "[Ollama Unavailable]" in res

def test_llm_analyzer_fallback():
    analyzer = LLMAnalyzer(client=OllamaClient(base_url="http://localhost:99999"))
    res = analyzer.analyze_clickbait("SHOCKING NEWS YOU MUST SEE", "Content goes here...")
    assert "clickbait_score" in res
    assert isinstance(res["clickbait_score"], float)

def test_embeddings_and_retriever():
    retriever = DocumentRetriever()
    retriever.add_document("doc1", "Artificial intelligence in healthcare improves diagnosis.")
    retriever.add_document("doc2", "Delicious recipes for home cooking and baking.")
    
    results = retriever.retrieve("AI health medical", top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == "doc1"

def test_rag_pipeline_query():
    pipeline = RAGPipeline()
    pipeline.index_knowledge_base([
        {"id": "fact1", "text": "NASA launched the James Webb Space Telescope in December 2021."}
    ])
    response = pipeline.query("James Webb Space Telescope was launched by NASA")
    assert "verdict" in response
