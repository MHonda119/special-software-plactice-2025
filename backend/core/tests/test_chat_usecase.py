from unittest.mock import patch

from django.test import TestCase

from core.models import LLM, ChatSession, Message
from core.usecases import ChatInSessionUsecase
from core.llm_clients import ChatResult


class ChatUsecaseTests(TestCase):
    def setUp(self):
        self.llm = LLM.objects.create(
            name="Local",
            provider="OLLAMA",
            model="llama3",
        )
        self.session = ChatSession.objects.create(llm=self.llm, title="Test")

    def test_run_creates_assistant_message(self):
        def fake_client(*args, **kwargs):  # noqa: D401 - simple factory
            class Dummy:
                def chat(self_inner, messages, options=None):  # noqa: D401
                    return ChatResult(
                        content="Hello from mock", usage={"prompt_tokens": 1}
                    )

            return Dummy()

        with patch("core.usecases.build_llm_client", fake_client):
            uc = ChatInSessionUsecase(self.session.uuid)
            result = uc.run("Hi")

        self.assertEqual(
            result["assistant_message"]["content"],
            "Hello from mock",
        )
        # DB に assistant が作成されているか
        msgs = list(Message.objects.filter(session=self.session))
        self.assertEqual(len(msgs), 2)  # user + assistant
        self.assertEqual(msgs[-1].role, "assistant")
        self.assertEqual(msgs[-1].content, "Hello from mock")
