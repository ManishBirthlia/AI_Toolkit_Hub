from pathlib import Path
from typing import Union

try:
    from google.cloud import vision
except ImportError as e:
    raise ImportError("pip install google-cloud-vision") from e

from utils.logger import get_logger

logger = get_logger(__name__)


class GoogleVisionOCR:
    """Cloud OCR via Google Cloud Vision API."""

    def __init__(self) -> None:
        self.client = vision.ImageAnnotatorClient()
        logger.info("GoogleVisionOCR initialized.")

    def extract_text(self, source: Union[str, bytes], mode: str = "text") -> str:
        """
        Extract text from an image using Google Cloud Vision.

        Args:
            source: File path (str) or raw image bytes.
            mode: 'text' for sparse text or 'document' for dense documents.

        Returns:
            Extracted text as a plain string.

        Raises:
            ValueError: If source is empty or mode is invalid.
            RuntimeError: If the Vision API call fails.
        """
        if not source:
            raise ValueError("Source image cannot be empty.")
        if mode not in ("text", "document"):
            raise ValueError("mode must be 'text' or 'document'.")
        try:
            content = source if isinstance(source, bytes) else Path(source).read_bytes()
            image = vision.Image(content=content)
            if mode == "document":
                response = self.client.document_text_detection(image=image)
                text = response.full_text_annotation.text
            else:
                response = self.client.text_detection(image=image)
                annotations = response.text_annotations
                text = annotations[0].description if annotations else ""
            if response.error.message:
                raise RuntimeError(f"Google Vision API error: {response.error.message}")
            return text.strip()
        except (ValueError, RuntimeError):
            raise
        except Exception as e:
            raise RuntimeError(f"Google Vision processing error: {e}") from e
