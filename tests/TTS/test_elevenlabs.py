import pytest
from unittest.mock import MagicMock, patch


class TestElevenLabsTTS:

    @patch("modules.TTS.ElevenLabs.get_api_key", return_value="el_test")
    def setup_method(self, method, mock_key):
        from modules.TTS.ElevenLabs import ElevenLabsTTS
        self.tts = ElevenLabsTTS()

    @patch("modules.TTS.ElevenLabs.requests.post")
    def test_synthesize_returns_bytes(self, mock_post):
        mock_post.return_value.content = b"fake_audio"
        mock_post.return_value.raise_for_status = MagicMock()
        assert self.tts.synthesize("Hello") == b"fake_audio"

    def test_raises_on_empty_text(self):
        with pytest.raises(ValueError, match="Text cannot be empty"):
            self.tts.synthesize("")

    def test_raises_on_invalid_stability(self):
        with pytest.raises(ValueError, match="stability"):
            self.tts.synthesize("Hello", stability=1.5)

    @patch("modules.TTS.ElevenLabs.requests.get")
    def test_list_voices_returns_list(self, mock_get):
        mock_get.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.return_value = {
            "voices": [{"voice_id": "abc", "name": "Rachel"}]}
        voices = self.tts.list_voices()
        assert isinstance(voices, list) and len(voices) == 1
