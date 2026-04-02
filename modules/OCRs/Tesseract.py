import io
from pathlib import Path
from typing import Optional, Union

try:
    import pytesseract
    from PIL import Image
except ImportError as e:
    raise ImportError("pip install pytesseract pillow") from e

from utils.logger import get_logger

logger = get_logger(__name__)


class TesseractOCR:
    """Offline OCR using Tesseract. Requires tesseract binary installed."""

    def __init__(self, lang: str = "eng", tesseract_cmd: Optional[str] = None) -> None:
        self.lang = lang
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        logger.info(f"TesseractOCR initialized | lang='{self.lang}'")

    def extract_text(self, source: Union[str, bytes], config: str = "") -> str:
        """
        Extract text from an image file or raw bytes.

        Args:
            source: File path (str) or raw image bytes.
            config: Optional Tesseract config string (e.g. '--psm 6').

        Returns:
            Extracted text as a plain string.

        Raises:
            ValueError: If source is empty or file not found.
            RuntimeError: If Tesseract fails.
        """
        if not source:
            raise ValueError("Source image cannot be empty.")
        try:
            if isinstance(source, bytes):
                image = Image.open(io.BytesIO(source))
            else:
                path = Path(source)
                if not path.exists():
                    raise ValueError(f"Image file not found: {source}")
                image = Image.open(path)
            text = pytesseract.image_to_string(image, lang=self.lang, config=config)
            return text.strip()
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Tesseract processing error: {e}") from e

    def extract_data(self, source: Union[str, bytes]) -> dict:
        """Extract detailed OCR data including bounding boxes and confidence scores."""
        if not source:
            raise ValueError("Source image cannot be empty.")
        try:
            if isinstance(source, bytes):
                image = Image.open(io.BytesIO(source))
            else:
                path = Path(source)
                if not path.exists():
                    raise ValueError(f"Image file not found: {source}")
                image = Image.open(path)
            return pytesseract.image_to_data(image, lang=self.lang,
                                             output_type=pytesseract.Output.DICT)
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Tesseract data extraction error: {e}") from e
