import pytest
from unittest.mock import MagicMock, patch


class TestGroqChat:

    @patch("modules.LLMs.GroqAI.Groq")
    @patch("modules.LLMs.GroqAI.get_api_key", return_value="gsk_test")
    def setup_method(self, method, mock_key, mock_cls):
        from modules.LLMs.GroqAI import GroqChat
        self.mock_client = MagicMock()
        mock_cls.return_value = self.mock_client
        self.chat = GroqChat()

    def _mock_response(self, content: str):
        response = MagicMock()
        response.choices[0].message.content = content
        response.usage.total_tokens = 20
        return response

    def test_chat_returns_string(self):
        self.mock_client.chat.completions.create.return_value = self._mock_response("Fast!")
        assert self.chat.chat("Hello") == "Fast!"

    def test_chat_raises_on_empty_prompt(self):
        with pytest.raises(ValueError):
            self.chat.chat("")

    def test_system_message_prepended(self):
        self.mock_client.chat.completions.create.return_value = self._mock_response("ok")
        self.chat.chat("Hi", system="Be a tutor.")
        messages = self.mock_client.chat.completions.create.call_args.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_default_model_is_llama(self):
        assert "llama" in self.chat.model.lower()
