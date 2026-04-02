import pytest
from unittest.mock import MagicMock, patch


class TestQRCodeGenerator:

    def setup_method(self):
        from modules.QR_Generate.QRCode import QRCodeGenerator
        self.gen = QRCodeGenerator()

    def test_raises_on_empty_data(self):
        with pytest.raises(ValueError, match="data cannot be empty"):
            self.gen.generate("")

    def test_raises_on_whitespace_data(self):
        with pytest.raises(ValueError):
            self.gen.generate("   ")

    def test_decode_raises_on_empty_path(self):
        with pytest.raises(ValueError, match="image_path cannot be empty"):
            self.gen.decode("")

    @patch("modules.QR_Generate.QRCode.Path")
    def test_decode_raises_when_file_not_found(self, mock_path):
        mock_path.return_value.exists.return_value = False
        with pytest.raises(ValueError, match="Image file not found"):
            self.gen.decode("missing.png")
