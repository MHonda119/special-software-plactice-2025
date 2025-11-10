from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import LLM, ChatSession, Message


class LLMSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLM
        fields = [
            "id",
            "name",
            "provider",
            "base_url",
            "model",
            "extra",
            "is_active",
        ]


class LLMCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLM
        fields = [
            "id",
            "name",
            "provider",
            "base_url",
            "model",
            "api_key",
            "extra",
            "is_active",
        ]

    def validate(self, attrs):
        provider = attrs.get("provider") or getattr(self.instance, "provider", None)
        api_key = attrs.get("api_key") or getattr(self.instance, "api_key", None)
        if provider in {"OPENAI", "GEMINI"} and not api_key:
            raise ValidationError(
                {"api_key": ("This field is required for the selected provider.")}
            )
        return attrs


class ChatSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ["uuid", "llm", "title"]
        read_only_fields = ["uuid"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at"]
