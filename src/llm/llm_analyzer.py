from typing import Dict, Any, List, Optional
from src.llm.ollama_client import OllamaClient
from src.llm.prompts import CLICKBAIT_PROMPT_TEMPLATE, CLAIM_EXTRACTION_PROMPT, AUTHENTICITY_PROMPT

class LLMAnalyzer:
    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient()

    def analyze_clickbait(self, title: str, text: str) -> Dict[str, Any]:
        prompt = CLICKBAIT_PROMPT_TEMPLATE.format(title=title, text_excerpt=text[:500])
        result = self.client.generate_json(prompt)
        if "clickbait_score" not in result:
            result["clickbait_score"] = 0.3  # fallback baseline
            result["reasons"] = result.get("reasons", ["Baseline automated assessment"])
        return result

    def extract_claims(self, text: str) -> List[Dict[str, str]]:
        prompt = CLAIM_EXTRACTION_PROMPT.format(text=text[:2000])
        result = self.client.generate_json(prompt)
        return result.get("claims", [])

    def analyze_authenticity(self, title: str, text: str) -> Dict[str, Any]:
        prompt = AUTHENTICITY_PROMPT.format(title=title, text_excerpt=text[:1000])
        result = self.client.generate_json(prompt)
        if "ai_generated_likelihood" not in result:
            result["ai_generated_likelihood"] = 0.2
            result["reasoning"] = "Standard human structure detected"
        return result
