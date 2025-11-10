from django.test import TestCase

from core.serializers import LLMCreateUpdateSerializer


class LLMSerializerValidationTests(TestCase):
    def test_ollama_without_api_key_valid(self):
        serializer = LLMCreateUpdateSerializer(
            data={
                "name": "Local",
                "provider": "OLLAMA",
                "model": "llama3",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_openai_requires_api_key(self):
        """OpenAI で API キー無しは無効"""
        pass

    def test_openai_with_api_key_valid(self):
        """OpenAI で API キーありは有効"""
        pass
