import json
from typing import Optional, Literal
from openai import OpenAI, APIError

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMTranslator:
    """LLM-powered contextual translation using GPT-4o. Best for nuanced, domain-specific text."""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.client = OpenAI(api_key=get_api_key("OPENAI_API_KEY"))
        logger.info(f"LLMTranslator initialized | model='{self.model}'")

    def translate(self, text: str, target_lang: str = "English",
                  source_lang: Optional[str] = None,
                  tone: Literal["formal", "informal", "neutral"] = "neutral",
                  domain: Optional[str] = None,
                  instructions: Optional[str] = None) -> str:
        """Translate text using an LLM with contextual understanding.

        Args:
            text: Text to translate.
            target_lang: Target language name (e.g. 'French', 'Hindi').
            source_lang: Source language name. Auto-detected if None.
            tone: Translation tone ('formal', 'informal', 'neutral').
            domain: Optional domain context (e.g. 'medical', 'legal').
            instructions: Free-form custom instruction for the system prompt.

        Returns:
            Translated text as a plain string.

        Raises:
            ValueError: If text is empty.
            RuntimeError: If the API call fails.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        parts = [f"You are a professional translator. Translate the user's text into {target_lang}."]
        if source_lang:
            parts.append(f"The source language is {source_lang}.")
        if tone != "neutral":
            parts.append(f"Use a {tone} tone.")
        if domain:
            parts.append(f"This is a {domain} text — use appropriate domain-specific terminology.")
        parts.append("Return ONLY the translated text. Do not include explanations or the original.")
        if instructions:
            parts.append(instructions)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": " ".join(parts)},
                          {"role": "user", "content": text}],
                temperature=0.2,
                max_tokens=min(len(text) * 4, 4096),
            )
            return response.choices[0].message.content.strip()
        except APIError as e:
            raise RuntimeError(f"LLM translation failed: {e}") from e

    def translate_with_explanation(self, text: str, target_lang: str = "English",
                                   source_lang: Optional[str] = None) -> dict:
        """Translate and return an explanation of key translation decisions.

        Returns:
            Dict with 'translation', 'explanation', and 'alternatives'.

        Raises:
            ValueError: If text is empty.
            RuntimeError: If the API call fails.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        source_clause = f"from {source_lang}" if source_lang else ""
        system_prompt = (
            f"You are a professional translator and linguist. "
            f"Translate the text {source_clause} into {target_lang}. "
            "Respond in JSON with exactly three keys: 'translation', 'explanation', 'alternatives'. "
            "Return only valid JSON — no markdown, no backticks."
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": text}],
                temperature=0.3, max_tokens=2048,
            )
            return json.loads(response.choices[0].message.content.strip())
        except APIError as e:
            raise RuntimeError(f"LLM translation with explanation failed: {e}") from e
