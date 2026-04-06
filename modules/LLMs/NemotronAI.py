from typing import Optional
import openai
from openai import OpenAIError, AuthenticationError, RateLimitError

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class NemotronChat:
    """NVIDIA Nemotron provider. Models: nvidia/nemotron-3-nano-30b-a3b"""

    DEFAULT_MODEL = "nvidia/nemotron-3-nano-30b-a3b"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        # Using OpenAI compatible client for Nvidia endpoint
        self.client = openai.OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=get_api_key("NVIDIA_SIMPLE_CHAT_API_KEY")
        )
        logger.info(f"NemotronChat initialized | model='{self.model}'")

    def chat(self, prompt: str, system: Optional[str] = None,
             temperature: float = 1.0, max_tokens: int = 18384) -> str:
        """
        Send a user message and return Nemotron's reply.

        Args:
            prompt: The user message.
            system: Optional system prompt.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.

        Returns:
            Nemotron's response as a plain string, including the thinking block.

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

        kwargs = dict(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
            top_p=1.0,
            extra_body={"reasoning_budget": 16384, "chat_template_kwargs": {"enable_thinking": True}}
        )

        try:
            response = self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            
            # The python client with custom Nvidia endpoints might return reasoning_content
            message = choice.message
            content = getattr(message, "content", "") or ""
            reasoning = getattr(message, "reasoning_content", "") or ""

            final_text = ""
            if reasoning.strip():
                reasoning_lines = reasoning.strip().split('\n')
                reasoning_block = "\n".join([f"> {line}" for line in reasoning_lines])
                final_text += f"> 🤔 **Thinking:**\n{reasoning_block}\n\n"
            
            final_text += content
            return final_text

        except AuthenticationError as e:
            raise RuntimeError("Invalid Nvidia API key.") from e
        except RateLimitError as e:
            raise RuntimeError("Nvidia rate limit exceeded.") from e
        except OpenAIError as e:
            raise RuntimeError(f"Nemotron API error: {e}") from e

    def stream(self, prompt: str, system: Optional[str] = None,
               temperature: float = 1.0, max_tokens: int = 18384):
        """Stream Nemotron's reply token by token."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs = dict(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
            top_p=1.0,
            extra_body={"reasoning_budget": 16384, "chat_template_kwargs": {"enable_thinking": True}},
            stream=True
        )

        try:
            stream_obj = self.client.chat.completions.create(**kwargs)
            for chunk in stream_obj:
                if not getattr(chunk, "choices", None):
                    continue
                delta = chunk.choices[0].delta
                
                # Yield reasoning content if present
                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning:
                    yield reasoning
                
                # Yield normal text content if present
                content = getattr(delta, "content", None)
                if content:
                    yield content

        except OpenAIError as e:
            raise RuntimeError(f"Nemotron streaming failed: {e}") from e
