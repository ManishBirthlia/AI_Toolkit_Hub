import pytest
from unittest.mock import patch


class TestEdgeTTS:

    def setup_method(self):
        from modules.TTS.EdgeTTS import EdgeTTS
        self.tts = EdgeTTS(voice="en-US-JennyNeural")

    @patch("modules.TTS.EdgeTTS.asyncio.run")
    def test_synthesize_returns_bytes(self, mock_run):
        mock_run.return_value = b"fake_mp3"
        assert self.tts.synthesize("Hello") == b"fake_mp3"

    def test_raises_on_empty_text(self):
        with pytest.raises(ValueError, match="Text cannot be empty"):
            self.tts.synthesize("")

    def test_default_voice(self):
        assert self.tts.voice == "en-US-JennyNeural"
