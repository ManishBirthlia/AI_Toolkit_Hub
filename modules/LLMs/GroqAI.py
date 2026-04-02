from typing import Optional
from groq import Groq, APIError, AuthenticationError, RateLimitError

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class GroqChat:
    """Groq provider for ultra-fast LLM inference. Models: llama-3.3-70b-versatile, mixtral-8x7b-32768"""

    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.client = Groq(api_key=get_api_key("GROQ_API_KEY"))
        logger.info(f"GroqChat initialized | model='{self.model}'")

    def chat(self, prompt: str, system: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Send a user message and return the model's reply via Groq.

        Args:
            prompt: The user message.
            system: Optional system prompt.
            temperature: Sampling temperature (0.0–2.0).
            max_tokens: Maximum tokens in the response.

        Returns:
            Model response as a plain string.

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
            raise RuntimeError("Invalid Groq API key.") from e
        except RateLimitError as e:
            raise RuntimeError("Groq rate limit exceeded.") from e
        except APIError as e:
            raise RuntimeError(f"Groq API error: {e}") from e

    def stream(self, prompt: str, system: Optional[str] = None,
               temperature: float = 0.7, max_tokens: int = 1024):
        """Stream the model's reply token by token."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = self.client.chat.completions.create(
                model=self.model, messages=messages,
                temperature=temperature, max_tokens=max_tokens, stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except APIError as e:
            raise RuntimeError(f"Groq streaming failed: {e}") from e
