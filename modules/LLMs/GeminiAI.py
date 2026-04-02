from typing import Optional
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError, PermissionDenied, ResourceExhausted

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class GeminiChat:
    """Google Gemini provider. Models: gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp"""

    DEFAULT_MODEL = "gemini-1.5-flash"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        genai.configure(api_key=get_api_key("GEMINI_API_KEY"))
        self._model_client = genai.GenerativeModel(model_name=self.model)
        logger.info(f"GeminiChat initialized | model='{self.model}'")

    def chat(self, prompt: str, system: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Send a user message and return Gemini's reply.

        Args:
            prompt: The user message.
            system: Optional system instruction prepended to prompt.
            temperature: Sampling temperature (0.0–1.0).
            max_tokens: Maximum output tokens.

        Returns:
            Gemini's response as a plain string.

        Raises:
            ValueError: If prompt is empty.
            RuntimeError: If the API call fails.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        generation_config = genai.types.GenerationConfig(
            temperature=temperature, max_output_tokens=max_tokens,
        )

        try:
            response = self._model_client.generate_content(
                full_prompt, generation_config=generation_config,
            )
            return response.text
        except PermissionDenied as e:
            raise RuntimeError("Invalid Gemini API key.") from e
        except ResourceExhausted as e:
            raise RuntimeError("Gemini quota exceeded.") from e
        except GoogleAPIError as e:
            raise RuntimeError(f"Gemini API error: {e}") from e

    def stream(self, prompt: str, system: Optional[str] = None,
               temperature: float = 0.7, max_tokens: int = 1024):
        """Stream Gemini's reply chunk by chunk."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        generation_config = genai.types.GenerationConfig(
            temperature=temperature, max_output_tokens=max_tokens,
        )
        try:
            response = self._model_client.generate_content(
                full_prompt, generation_config=generation_config, stream=True,
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except GoogleAPIError as e:
            raise RuntimeError(f"Gemini streaming failed: {e}") from e
