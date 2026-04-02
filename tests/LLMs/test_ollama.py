import pytest
from unittest.mock import MagicMock, patch


class TestOllamaChat:

    @patch("modules.LLMs.OllamaAI.requests.get")
    def setup_method(self, method, mock_get):
        mock_get.return_value.status_code = 200
        from modules.LLMs.OllamaAI import OllamaChat
        self.chat = OllamaChat(model="llama3.2")

    @patch("modules.LLMs.OllamaAI.requests.get")
    @patch("modules.LLMs.OllamaAI.requests.post")
    def test_chat_returns_string(self, mock_post, mock_get):
        mock_get.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"message": {"content": "Local reply!"}}
        mock_post.return_value.raise_for_status = MagicMock()
        assert self.chat.chat("Hello") == "Local reply!"

    def test_chat_raises_on_empty_prompt(self):
        with pytest.raises(ValueError):
            self.chat.chat("")

    @patch("modules.LLMs.OllamaAI.requests.get")
    def test_raises_when_server_unreachable(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("refused")
        with pytest.raises(RuntimeError, match="not reachable"):
            self.chat.chat("Hello")
