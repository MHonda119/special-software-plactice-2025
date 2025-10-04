from django.contrib import admin

from .models import ChatSession, LLM, Message


@admin.register(LLM)
class LLMAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "model", "is_active")
    list_filter = ("provider", "is_active")
    search_fields = ("name", "model")


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ("created_at", "role", "name", "content")
    readonly_fields = ("created_at",)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("uuid", "llm", "title", "is_active", "created_at")
    list_filter = ("is_active", "llm")
    search_fields = ("uuid", "title")
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "name", "created_at")
    list_filter = ("role",)
    search_fields = ("content", "name")
    autocomplete_fields = ("session",)
