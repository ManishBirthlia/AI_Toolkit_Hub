from typing import Optional, Literal

try:
    import deepl
except ImportError as e:
    raise ImportError("pip install deepl") from e

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class DeepLTranslator:
    """DeepL provider for high-accuracy neural machine translation. Supports 31 languages."""

    LANGUAGES = {
        "english": "EN-US", "british": "EN-GB", "hindi": "HI", "french": "FR",
        "german": "DE", "spanish": "ES", "portuguese": "PT-BR", "italian": "IT",
        "japanese": "JA", "chinese": "ZH", "arabic": "AR", "russian": "RU",
        "korean": "KO", "dutch": "NL", "polish": "PL",
    }

    def __init__(self) -> None:
        self.translator = deepl.Translator(get_api_key("DEEPL_API_KEY"))
        logger.info("DeepLTranslator initialized.")

    def translate(self, text: str, target_lang: str = "EN-US",
                  source_lang: Optional[str] = None,
                  formality: Literal["default", "more", "less",
                                     "prefer_more", "prefer_less"] = "default",
                  preserve_formatting: bool = False) -> str:
        """Translate text to the target language using DeepL.

        Args:
            text: Text to translate.
            target_lang: Target language code (e.g. 'EN-US', 'FR', 'DE').
            source_lang: Source language code. Auto-detected if None.
            formality: Tone formality ('more'=formal, 'less'=informal).
            preserve_formatting: Preserve original text formatting.

        Returns:
            Translated text as a plain string.

        Raises:
            ValueError: If text is empty.
            RuntimeError: If the API call fails.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
        try:
            result = self.translator.translate_text(
                text, target_lang=target_lang, source_lang=source_lang,
                formality=formality, preserve_formatting=preserve_formatting)
            return result.text
        except deepl.DeepLException as e:
            raise RuntimeError(f"DeepL translation failed: {e}") from e

    def translate_batch(self, texts: list[str], target_lang: str = "EN-US",
                        source_lang: Optional[str] = None) -> list[str]:
        """Translate a list of texts in a single API call."""
        if not texts:
            raise ValueError("texts list cannot be empty.")
        if any(not t or not t.strip() for t in texts):
            raise ValueError("No entry in texts can be empty.")
        try:
            results = self.translator.translate_text(
                texts, target_lang=target_lang, source_lang=source_lang)
            return [r.text for r in results]
        except deepl.DeepLException as e:
            raise RuntimeError(f"DeepL batch translation failed: {e}") from e

    def get_usage(self) -> dict:
        """Retrieve current DeepL API usage and limits."""
        try:
            usage = self.translator.get_usage()
            return {"character_count": usage.character.count,
                    "character_limit": usage.character.limit}
        except Exception as e:
            raise RuntimeError(f"Could not fetch DeepL usage: {e}") from e
