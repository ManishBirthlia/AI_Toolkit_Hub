import pytest
from unittest.mock import MagicMock, patch


class TestOpenAIChat:

    @patch("modules.LLMs.OpenAI.OpenAI")
    @patch("modules.LLMs.OpenAI.get_api_key", return_value="sk-test")
    def setup_method(self, method, mock_key, mock_openai_cls):
        from modules.LLMs.OpenAI import OpenAIChat
        self.mock_client = MagicMock()
        mock_openai_cls.return_value = self.mock_client
        self.chat = OpenAIChat(model="gpt-4o")

    def _mock_response(self, content: str):
        response = MagicMock()
        response.choices[0].message.content = content
        response.usage.total_tokens = 42
        return response

    def test_chat_returns_string(self):
        self.mock_client.chat.completions.create.return_value = self._mock_response("Hello!")
        result = self.chat.chat("Say hello.")
        assert isinstance(result, str)
        assert result == "Hello!"

    def test_chat_with_system_prompt(self):
        self.mock_client.chat.completions.create.return_value = self._mock_response("ok")
        self.chat.chat("Who are you?", system="You are a pirate.")
        messages = self.mock_client.chat.completions.create.call_args.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_chat_raises_on_empty_prompt(self):
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            self.chat.chat("")

    def test_chat_raises_on_whitespace_prompt(self):
        with pytest.raises(ValueError):
            self.chat.chat("   ")

    def test_chat_raises_on_api_error(self):
        from openai import APIError
        self.mock_client.chat.completions.create.side_effect = APIError(
            "error", request=MagicMock(), body=None)
        with pytest.raises(RuntimeError):
            self.chat.chat("Hello")

    def test_default_model(self):
        assert self.chat.model == "gpt-4o"
