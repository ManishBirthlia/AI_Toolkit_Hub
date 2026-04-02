import pytest
from unittest.mock import MagicMock, patch


class TestDeepLTranslator:

    @patch("modules.Translate.DeepL.deepl.Translator")
    @patch("modules.Translate.DeepL.get_api_key", return_value="deepl_test:fx")
    def setup_method(self, method, mock_key, mock_cls):
        from modules.Translate.DeepL import DeepLTranslator
        self.mock_translator = MagicMock()
        mock_cls.return_value = self.mock_translator
        self.translator = DeepLTranslator()

    def _mock_result(self, text: str):
        r = MagicMock()
        r.text = text
        r.detected_source_lang = "EN"
        return r

    def test_translate_returns_string(self):
        self.mock_translator.translate_text.return_value = self._mock_result("Bonjour")
        assert self.translator.translate("Hello", target_lang="FR") == "Bonjour"

    def test_raises_on_empty_text(self):
        with pytest.raises(ValueError, match="Text cannot be empty"):
            self.translator.translate("", target_lang="FR")

    def test_translate_batch_returns_list(self):
        self.mock_translator.translate_text.return_value = [
            self._mock_result("Bonjour"), self._mock_result("Au revoir")]
        result = self.translator.translate_batch(["Hello", "Goodbye"], target_lang="FR")
        assert result == ["Bonjour", "Au revoir"]

    def test_batch_raises_on_empty_list(self):
        with pytest.raises(ValueError, match="texts list cannot be empty"):
            self.translator.translate_batch([], target_lang="FR")

    def test_get_usage_returns_dict(self):
        usage = MagicMock()
        usage.character.count = 5000
        usage.character.limit = 500000
        self.mock_translator.get_usage.return_value = usage
        result = self.translator.get_usage()
        assert result["character_count"] == 5000
