from typing import Optional
import anthropic
from anthropic import APIError, AuthenticationError, RateLimitError

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class ClaudeChat:
    """Anthropic Claude provider. Models: claude-opus-4-5, claude-sonnet-4-5"""

    DEFAULT_MODEL = "claude-sonnet-4-5"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.client = anthropic.Anthropic(api_key=get_api_key("ANTHROPIC_API_KEY"))
        logger.info(f"ClaudeChat initialized | model='{self.model}'")

    def chat(self, prompt: str, system: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Send a user message and return Claude's reply.

        Args:
            prompt: The user message.
            system: Optional system prompt.
            temperature: Sampling temperature (0.0–1.0).
            max_tokens: Maximum tokens in the response.

        Returns:
            Claude's response as a plain string.

        Raises:
            ValueError: If prompt is empty.
            RuntimeError: If the API call fails.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        kwargs = dict(model=self.model, max_tokens=max_tokens,
                      temperature=temperature,
                      messages=[{"role": "user", "content": prompt}])
        if system:
            kwargs["system"] = system

        try:
            response = self.client.messages.create(**kwargs)
            return response.content[0].text
        except AuthenticationError as e:
            raise RuntimeError("Invalid Anthropic API key.") from e
        except RateLimitError as e:
            raise RuntimeError("Anthropic rate limit exceeded.") from e
        except APIError as e:
            raise RuntimeError(f"Claude API error: {e}") from e

    def stream(self, prompt: str, system: Optional[str] = None,
               temperature: float = 0.7, max_tokens: int = 1024):
        """Stream Claude's reply token by token."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        kwargs = dict(model=self.model, max_tokens=max_tokens,
                      temperature=temperature,
                      messages=[{"role": "user", "content": prompt}])
        if system:
            kwargs["system"] = system

        try:
            with self.client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    yield text
        except APIError as e:
            raise RuntimeError(f"Claude streaming failed: {e}") from e
