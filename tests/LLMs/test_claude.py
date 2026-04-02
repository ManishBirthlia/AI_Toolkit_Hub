import pytest
from unittest.mock import MagicMock, patch


class TestClaudeChat:

    @patch("modules.LLMs.ClaudeAI.anthropic.Anthropic")
    @patch("modules.LLMs.ClaudeAI.get_api_key", return_value="sk-ant-test")
    def setup_method(self, method, mock_key, mock_cls):
        from modules.LLMs.ClaudeAI import ClaudeChat
        self.mock_client = MagicMock()
        mock_cls.return_value = self.mock_client
        self.chat = ClaudeChat()

    def _mock_response(self, text: str):
        response = MagicMock()
        response.content[0].text = text
        response.stop_reason = "end_turn"
        return response

    def test_chat_returns_string(self):
        self.mock_client.messages.create.return_value = self._mock_response("Hello from Claude!")
        assert self.chat.chat("Say hello.") == "Hello from Claude!"

    def test_chat_system_passed_as_kwarg(self):
        self.mock_client.messages.create.return_value = self._mock_response("ok")
        self.chat.chat("Hi", system="Be concise.")
        call_kwargs = self.mock_client.messages.create.call_args.kwargs
        assert call_kwargs.get("system") == "Be concise."

    def test_chat_raises_on_empty_prompt(self):
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            self.chat.chat("")

    def test_default_model_contains_claude(self):
        assert "claude" in self.chat.model.lower()
