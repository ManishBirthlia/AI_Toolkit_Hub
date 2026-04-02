import io
from pathlib import Path
from typing import Union

try:
    import easyocr
    import numpy as np
    from PIL import Image
except ImportError as e:
    raise ImportError("pip install easyocr numpy pillow") from e

from utils.logger import get_logger

logger = get_logger(__name__)


class EasyOCRClient:
    """Deep learning-based OCR supporting 80+ languages."""

    def __init__(self, languages: list[str] = None, gpu: bool = False) -> None:
        self.languages = languages or ["en"]
        self.gpu = gpu
        logger.info(f"EasyOCR initializing | langs={self.languages} | gpu={self.gpu}")
        self.reader = easyocr.Reader(self.languages, gpu=self.gpu)

    def extract_text(self, source: Union[str, bytes], detail: bool = False) -> Union[str, list]:
        """
        Extract text from an image file or raw bytes.

        Args:
            source: File path (str) or raw image bytes.
            detail: If False returns plain string; if True returns list with bboxes.

        Returns:
            Plain text string or list of [bbox, text, confidence] tuples.

        Raises:
            ValueError: If source is empty or file not found.
            RuntimeError: If OCR processing fails.
        """
        if not source:
            raise ValueError("Source image cannot be empty.")
        try:
            if isinstance(source, bytes):
                image = np.array(Image.open(io.BytesIO(source)))
            else:
                path = Path(source)
                if not path.exists():
                    raise ValueError(f"Image file not found: {source}")
                image = str(path)
            results = self.reader.readtext(image)
            if detail:
                return results
            return " ".join([item[1] for item in results]).strip()
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"EasyOCR processing error: {e}") from e
