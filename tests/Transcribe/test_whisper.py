import pytest
from unittest.mock import MagicMock, patch, mock_open


class TestWhisperTranscriber:

    @patch("modules.Transcribe.Whisper.OpenAI")
    @patch("modules.Transcribe.Whisper.get_api_key", return_value="sk-test")
    def setup_method(self, method, mock_key, mock_cls):
        from modules.Transcribe.Whisper import WhisperTranscriber
        self.mock_client = MagicMock()
        mock_cls.return_value = self.mock_client
        self.transcriber = WhisperTranscriber(mode="api")

    def test_raises_on_invalid_mode(self):
        with pytest.raises(ValueError, match="mode must be"):
            from modules.Transcribe.Whisper import WhisperTranscriber
            WhisperTranscriber(mode="cloud")

    def test_raises_on_empty_path(self):
        with pytest.raises(ValueError, match="audio_path cannot be empty"):
            self.transcriber.transcribe("")

    @patch("modules.Transcribe.Whisper.Path")
    def test_raises_when_file_not_found(self, mock_path):
        mock_path.return_value.exists.return_value = False
        with pytest.raises(ValueError, match="Audio file not found"):
            self.transcriber.transcribe("missing.mp3")

    @patch("modules.Transcribe.Whisper.Path")
    def test_transcribe_returns_text(self, mock_path):
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.stat.return_value.st_size = 1024 * 1024
        mock_path.return_value.name = "audio.mp3"
        mock_path.return_value.__str__ = lambda s: "audio.mp3"
        response = MagicMock()
        response.text = "Hello transcript."
        self.mock_client.audio.transcriptions.create.return_value = response
        with patch("builtins.open", mock_open(read_data=b"audio")):
            result = self.transcriber.transcribe("audio.mp3")
        assert result == "Hello transcript."

    @patch("modules.Transcribe.Whisper.Path")
    def test_raises_on_file_too_large(self, mock_path):
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.stat.return_value.st_size = 30 * 1024 * 1024
        mock_path.return_value.name = "big.mp3"
        with pytest.raises(ValueError, match="exceeds the Whisper API limit"):
            self.transcriber.transcribe("big.mp3")
