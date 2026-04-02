import pytest
from unittest.mock import MagicMock, patch


class TestEasyOCRClient:

    @patch("modules.OCRs.EasyOCR.easyocr.Reader")
    def setup_method(self, method, mock_reader_cls):
        from modules.OCRs.EasyOCR import EasyOCRClient
        self.mock_reader = MagicMock()
        mock_reader_cls.return_value = self.mock_reader
        self.ocr = EasyOCRClient(languages=["en"], gpu=False)

    def test_extract_text_returns_string(self):
        self.mock_reader.readtext.return_value = [
            ([[0,0],[100,0],[100,30],[0,30]], "Hello World", 0.99)]
        with patch("modules.OCRs.EasyOCR.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            result = self.ocr.extract_text("fake.png", detail=False)
        assert result == "Hello World"

    def test_extract_text_detail_returns_list(self):
        self.mock_reader.readtext.return_value = [
            ([[0,0],[10,0],[10,10],[0,10]], "Hi", 0.95)]
        with patch("modules.OCRs.EasyOCR.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            result = self.ocr.extract_text("fake.png", detail=True)
        assert isinstance(result, list)

    def test_raises_on_empty_source(self):
        with pytest.raises(ValueError):
            self.ocr.extract_text("")
