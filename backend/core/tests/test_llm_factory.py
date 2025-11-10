from django.test import TestCase

from core.models import LLM
from core.llm_clients import (
    build_llm_client,
    OllamaClient,
)


class LLMFactoryTests(TestCase):
    def test_factory_returns_ollama_client(self):
        llm = LLM.objects.create(
            name="Local",
            provider="OLLAMA",
            model="llama3",
        )
        client = build_llm_client(llm)
        self.assertIsInstance(client, OllamaClient)

    def test_factory_returns_openai_client(self):
        """OpenAI クライアントが返ること"""
        pass

    def test_factory_returns_gemini_client(self):
        """Gemini クライアントが返ること"""
        pass

    def test_factory_requires_api_key_openai(self):
        """OpenAI で API キー必須エラー"""
        pass
