from rest_framework import serializers
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


class ChatSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ["uuid", "llm", "title"]
        read_only_fields = ["uuid"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at"]
