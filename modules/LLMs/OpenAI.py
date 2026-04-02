from typing import Optional
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIChat:
    """OpenAI provider for chat completions. Models: gpt-4o, gpt-4o-mini, gpt-4-turbo"""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.client = OpenAI(api_key=get_api_key("OPENAI_API_KEY"))
        logger.info(f"OpenAIChat initialized | model='{self.model}'")

    def chat(self, prompt: str, system: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Send a user message and return the assistant's reply.

        Args:
            prompt: The user message.
            system: Optional system prompt.
            temperature: Sampling temperature (0.0–2.0).
            max_tokens: Maximum tokens in the response.

        Returns:
            Assistant response as a plain string.

        Raises:
            ValueError: If prompt is empty.
            RuntimeError: If the API call fails.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages,
                temperature=temperature, max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except AuthenticationError as e:
            raise RuntimeError("Invalid OpenAI API key.") from e
        except RateLimitError as e:
            raise RuntimeError("OpenAI rate limit exceeded.") from e
        except APIError as e:
            raise RuntimeError(f"OpenAI API error: {e}") from e

    def stream(self, prompt: str, system: Optional[str] = None,
               temperature: float = 0.7, max_tokens: int = 1024):
        """Stream the assistant's reply token by token."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            with self.client.chat.completions.stream(
                model=self.model, messages=messages,
                temperature=temperature, max_tokens=max_tokens,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except APIError as e:
            raise RuntimeError(f"OpenAI streaming failed: {e}") from e
