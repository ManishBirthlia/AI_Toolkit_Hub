import pytest, base64
from unittest.mock import MagicMock, patch


class TestDALLEClient:

    @patch("modules.AI_Image.DALLE.OpenAI")
    @patch("modules.AI_Image.DALLE.get_api_key", return_value="sk-test")
    def setup_method(self, method, mock_key, mock_cls):
        from modules.AI_Image.DALLE import DALLEClient
        self.mock_client = MagicMock()
        mock_cls.return_value = self.mock_client
        self.dalle = DALLEClient(model="dall-e-3")

    def _mock_image_response(self):
        fake_bytes = b"\x89PNG fake"
        b64 = base64.b64encode(fake_bytes).decode()
        response = MagicMock()
        response.data[0].b64_json = b64
        return response, fake_bytes

    def test_generate_returns_bytes(self):
        response, expected = self._mock_image_response()
        self.mock_client.images.generate.return_value = response
        result = self.dalle.generate("A sunset")
        assert isinstance(result, bytes) and result == expected

    def test_raises_on_empty_prompt(self):
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            self.dalle.generate("")

    def test_raises_on_invalid_size(self):
        with pytest.raises(ValueError, match="Invalid size"):
            self.dalle.generate("A cat", size="512x512")
