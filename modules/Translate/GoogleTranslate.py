from typing import Optional

try:
    from google.cloud import translate_v2 as translate
except ImportError as e:
    raise ImportError("pip install google-cloud-translate") from e

from utils.logger import get_logger

logger = get_logger(__name__)


class GoogleTranslator:
    """Google Cloud Translation provider. Supports 133+ languages."""

    def __init__(self) -> None:
        self.client = translate.Client()
        logger.info("GoogleTranslator initialized.")

    def translate(self, text: str, target_lang: str = "en",
                  source_lang: Optional[str] = None) -> str:
        """Translate text to the target language.

        Args:
            text: Text to translate.
            target_lang: BCP-47 target language code (e.g. 'en', 'fr', 'hi').
            source_lang: Source language code. Auto-detected if None.

        Returns:
            Translated text as a plain string.

        Raises:
            ValueError: If text is empty.
            RuntimeError: If the API call fails.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
        try:
            kwargs = {"target_language": target_lang}
            if source_lang:
                kwargs["source_language"] = source_lang
            result = self.client.translate(text, **kwargs)
            return result.get("translatedText", "")
        except Exception as e:
            raise RuntimeError(f"Google translation failed: {e}") from e

    def translate_batch(self, texts: list[str], target_lang: str = "en",
                        source_lang: Optional[str] = None) -> list[str]:
        """Translate multiple texts in a single API call."""
        if not texts:
            raise ValueError("texts list cannot be empty.")
        try:
            kwargs = {"target_language": target_lang}
            if source_lang:
                kwargs["source_language"] = source_lang
            results = self.client.translate(texts, **kwargs)
            return [r.get("translatedText", "") for r in results]
        except Exception as e:
            raise RuntimeError(f"Google batch translation failed: {e}") from e

    def detect_language(self, text: str) -> dict:
        """Detect the language of a given text."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
        try:
            result = self.client.detect_language(text)
            return {"language": result.get("language", ""),
                    "confidence": result.get("confidence", 0.0)}
        except Exception as e:
            raise RuntimeError(f"Language detection failed: {e}") from e

    def list_languages(self, target_language: str = "en") -> list[dict]:
        """List all supported languages."""
        try:
            return self.client.get_languages(target_language=target_language)
        except Exception as e:
            raise RuntimeError(f"Could not fetch supported languages: {e}") from e
