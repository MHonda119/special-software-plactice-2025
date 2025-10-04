import uuid
from django.db import models


class LLM(models.Model):
    PROVIDER_CHOICES = [
        ("OLLAMA", "Ollama"),
        ("OPENAI", "OpenAI"),
        ("GEMINI", "Gemini"),
        ("CUSTOM", "Custom"),
    ]

    name = models.CharField(max_length=100)
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default="OLLAMA",
    )
    # Allow Compose hostnames (e.g., http://ollama:11434), so do not perform URL validation
    base_url = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=100)
    api_key = models.TextField(null=True, blank=True)
    extra = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.provider}:{self.model})"


class ChatSession(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    llm = models.ForeignKey(
        LLM,
        on_delete=models.PROTECT,
        related_name="chat_sessions",
    )
    title = models.CharField(max_length=200, default="New Session")
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.title} ({self.uuid})"


class Message(models.Model):
    ROLE_CHOICES = [
        ("system", "system"),
        ("user", "user"),
        ("assistant", "assistant"),
        ("tool", "tool"),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    name = models.CharField(max_length=100, null=True, blank=True)
    usage = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["session", "created_at"])]
        ordering = ["created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.role}: {self.content[:30]}"
