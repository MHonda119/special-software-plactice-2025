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


def build_llm_client(llm) -> OllamaClient:
    # 今回はOllamaのみ対応（拡張余地あり）
    return OllamaClient(llm.base_url, llm.model, llm.extra)
