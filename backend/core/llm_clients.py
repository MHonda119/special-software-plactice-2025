import os
import requests
from dataclasses import dataclass


@dataclass
class ChatResult:
    content: str
    usage: dict


class OllamaClient:
    def __init__(
        self,
        base_url: str | None,
        model: str,
        default_params: dict | None = None,
    ):
        default_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.base_url = base_url or default_url
        self.model = model
        self.default_params = default_params or {}

    def chat(
        self,
        messages: list[dict],
        options: dict | None = None,
    ) -> ChatResult:
        url = self.base_url.rstrip("/") + "/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {**self.default_params, **(options or {})},
            "stream": False,
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        content = data.get("message", {}).get("content", "")
        usage = {"eval_count": data.get("eval_count")}
        return ChatResult(content=content, usage=usage)


class OpenAIClient:
    def __init__(
        self,
        base_url: str | None,
        model: str,
        api_key: str,
        default_params: dict | None = None,
    ):
        self.base_url = base_url or "https://api.openai.com/v1"
        self.model = model
        self.api_key = api_key
        self.default_params = default_params or {}

    def chat(
        self,
        messages: list[dict],
        options: dict | None = None,
    ) -> ChatResult:
        url = self.base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            **self.default_params,
            **(options or {}),
        }
        r = requests.post(url, json=payload, headers=headers, timeout=120)
        r.raise_for_status()
        data = r.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})
        return ChatResult(content=content, usage=usage)


class GeminiClient:
    def __init__(
        self,
        base_url: str | None,
        model: str,
        api_key: str,
        default_params: dict | None = None,
    ):
        self.base_url = base_url or "https://generativelanguage.googleapis.com/v1beta"
        self.model = model
        self.api_key = api_key
        self.default_params = default_params or {}

    def chat(
        self,
        messages: list[dict],
        options: dict | None = None,
    ) -> ChatResult:
        url = f"{self.base_url.rstrip('/')}/models/{self.model}:generateContent"
        params = {"key": self.api_key}
        
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {
            "contents": contents,
            **self.default_params,
            **(options or {}),
        }
        r = requests.post(url, json=payload, params=params, timeout=120)
        r.raise_for_status()
        data = r.json()
        
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        else:
            content = ""
        
        usage_metadata = data.get("usageMetadata", {})
        usage = {
            "prompt_token_count": usage_metadata.get("promptTokenCount", 0),
            "candidates_token_count": usage_metadata.get("candidatesTokenCount", 0),
            "total_token_count": usage_metadata.get("totalTokenCount", 0),
        }
        return ChatResult(content=content, usage=usage)


def build_llm_client(llm):
    if llm.provider == "OPENAI":
        if not llm.api_key:
            raise ValueError("OpenAI provider requires an API key")
        return OpenAIClient(llm.base_url, llm.model, llm.api_key, llm.extra)
    elif llm.provider == "GEMINI":
        if not llm.api_key:
            raise ValueError("Gemini provider requires an API key")
        return GeminiClient(llm.base_url, llm.model, llm.api_key, llm.extra)
    elif llm.provider == "CUSTOM":
        # For CUSTOM provider, assume OpenAI-compatible API
        if not llm.base_url:
            raise ValueError("CUSTOM provider requires a base_url")
        return OpenAIClient(llm.base_url, llm.model, llm.api_key or "", llm.extra)
    else:  # Default to OLLAMA
        return OllamaClient(llm.base_url, llm.model, llm.extra)
