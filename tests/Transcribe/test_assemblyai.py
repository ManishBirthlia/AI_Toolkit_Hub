import pytest
from unittest.mock import MagicMock, patch


class TestAssemblyAITranscriber:

    @patch("modules.Transcribe.AssemblyAI.get_api_key", return_value="aai_test")
    def setup_method(self, method, mock_key):
        from modules.Transcribe.AssemblyAI import AssemblyAITranscriber
        self.transcriber = AssemblyAITranscriber()

    def test_raises_on_empty_source(self):
        with pytest.raises(ValueError, match="source cannot be empty"):
            self.transcriber.transcribe("")

    @patch("modules.Transcribe.AssemblyAI.requests.post")
    @patch("modules.Transcribe.AssemblyAI.requests.get")
    @patch("modules.Transcribe.AssemblyAI.Path")
    def test_transcribe_returns_dict(self, mock_path, mock_get, mock_post):
        mock_path.return_value.exists.return_value = False
        mock_post.return_value.raise_for_status = MagicMock()
        mock_post.return_value.json.return_value = {"id": "abc123"}
        done = MagicMock()
        done.raise_for_status = MagicMock()
        done.json.return_value = {"status": "completed", "text": "Hello."}
        mock_get.return_value = done
        result = self.transcriber.transcribe("https://example.com/audio.mp3")
        assert result["text"] == "Hello."

    @patch("modules.Transcribe.AssemblyAI.requests.post")
    @patch("modules.Transcribe.AssemblyAI.requests.get")
    @patch("modules.Transcribe.AssemblyAI.Path")
    def test_raises_on_error_status(self, mock_path, mock_get, mock_post):
        mock_path.return_value.exists.return_value = False
        mock_post.return_value.raise_for_status = MagicMock()
        mock_post.return_value.json.return_value = {"id": "err_id"}
        failed = MagicMock()
        failed.raise_for_status = MagicMock()
        failed.json.return_value = {"status": "error", "error": "Audio too short"}
        mock_get.return_value = failed
        with pytest.raises(RuntimeError, match="Audio too short"):
            self.transcriber.transcribe("https://example.com/short.mp3")
