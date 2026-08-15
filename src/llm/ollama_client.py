import requests
import json
from typing import Dict, Any, Optional

from src.config.settings import settings

class OllamaClient:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout: int = 900):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        """Send prompt to local Ollama server and return text response."""
        url = f"{self.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 2048,  # cap output to prevent runaway generation
            }
        }
        # For qwen3 models: disable chain-of-thought thinking (massive speedup)
        # This is passed at top-level for newer Ollama versions
        if "qwen3" in self.model.lower():
            payload["think"] = False
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except Exception as e:
            # Return fallback string if Ollama is not running locally
            return f"[Ollama Unavailable] Simulation response for prompt analysis: {e}"

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate response and parse JSON output."""
        raw_response = self.generate(prompt, system_prompt=system_prompt, temperature=0.1)
        try:
            # Extract JSON block if wrapped in codeblocks
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_response:
                raw_response = raw_response.split("```")[1].split("```")[0].strip()
            return json.loads(raw_response)
        except json.JSONDecodeError:
            return {"raw_response": raw_response, "error": "Failed to parse JSON response"}
