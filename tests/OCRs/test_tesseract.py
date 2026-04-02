import pytest
from unittest.mock import MagicMock, patch


class TestTesseractOCR:

    @patch("modules.OCRs.Tesseract.pytesseract")
    @patch("modules.OCRs.Tesseract.Image")
    def setup_method(self, method, mock_image, mock_pytesseract):
        from modules.OCRs.Tesseract import TesseractOCR
        self.mock_pytesseract = mock_pytesseract
        self.mock_image = mock_image
        self.ocr = TesseractOCR(lang="eng")

    @patch("modules.OCRs.Tesseract.Path")
    def test_extract_text_from_path(self, mock_path):
        mock_path.return_value.exists.return_value = True
        self.mock_pytesseract.image_to_string.return_value = "  Hello World  "
        self.mock_image.open.return_value = MagicMock()
        assert self.ocr.extract_text("fake.png") == "Hello World"

    def test_extract_text_from_bytes(self):
        self.mock_pytesseract.image_to_string.return_value = "Bytes text"
        self.mock_image.open.return_value = MagicMock()
        assert self.ocr.extract_text(b"\x89PNG") == "Bytes text"

    def test_raises_on_empty_source(self):
        with pytest.raises(ValueError, match="Source image cannot be empty"):
            self.ocr.extract_text("")

    @patch("modules.OCRs.Tesseract.Path")
    def test_raises_when_file_not_found(self, mock_path):
        mock_path.return_value.exists.return_value = False
        with pytest.raises(ValueError, match="Image file not found"):
            self.ocr.extract_text("missing.png")
