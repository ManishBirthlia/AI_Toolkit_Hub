import pytest, json
from unittest.mock import MagicMock, patch


class TestLLMTranslator:

    @patch("modules.Translate.LLMTranslate.OpenAI")
    @patch("modules.Translate.LLMTranslate.get_api_key", return_value="sk-test")
    def setup_method(self, method, mock_key, mock_cls):
        from modules.Translate.LLMTranslate import LLMTranslator
        self.mock_client = MagicMock()
        mock_cls.return_value = self.mock_client
        self.translator = LLMTranslator()

    def _mock_response(self, text: str):
        r = MagicMock()
        r.choices[0].message.content = text
        return r

    def test_translate_returns_string(self):
        self.mock_client.chat.completions.create.return_value = self._mock_response("Bonjour")
        assert self.translator.translate("Hello", target_lang="French") == "Bonjour"

    def test_raises_on_empty_text(self):
        with pytest.raises(ValueError):
            self.translator.translate("", target_lang="French")

    def test_translate_with_explanation_returns_dict(self):
        payload = {"translation": "Bonjour", "explanation": "Direct", "alternatives": []}
        self.mock_client.chat.completions.create.return_value = (
            self._mock_response(json.dumps(payload)))
        result = self.translator.translate_with_explanation("Hello", target_lang="French")
        assert result["translation"] == "Bonjour"
