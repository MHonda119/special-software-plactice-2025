from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import LLM, ChatSession
from .serializers import (
    LLMSerializer,
    LLMCreateUpdateSerializer,
    ChatSessionCreateSerializer,
    MessageSerializer,
)
from .usecases import ChatInSessionUsecase
from django.middleware.csrf import get_token


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def csrf_token(request):
    """Issue and return CSRF token; also sets csrftoken cookie via middleware."""
    token = get_token(request)
    return Response({"csrftoken": token})


class LLMViewSet(viewsets.ModelViewSet):
    queryset = LLM.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return LLMCreateUpdateSerializer
        return LLMSerializer


class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.filter(is_active=True)
    serializer_class = ChatSessionCreateSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["get"], url_path="messages")
    def messages(self, request, pk=None):
        session = self.get_object()
        qs = session.messages.all()
        return Response(MessageSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"], url_path="chat")
    def chat(self, request, pk=None):
        message = request.data.get("message", "").strip()
        if not message:
            return Response(
                {"detail": "message is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        options = request.data.get("options", None)
        uc = ChatInSessionUsecase(pk)
        result = uc.run(user_text=message, options=options)
        return Response(result, status=status.HTTP_200_OK)
