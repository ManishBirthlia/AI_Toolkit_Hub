import json
from typing import Optional, Generator
import requests

from utils.logger import get_logger

logger = get_logger(__name__)

_DEFAULT_BASE_URL = "http://localhost:11434"


class OllamaChat:
    """Ollama provider for running LLMs locally. Requires: ollama serve"""

    DEFAULT_MODEL = "llama3.2"

    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = _DEFAULT_BASE_URL) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._chat_url = f"{self.base_url}/api/chat"
        logger.info(f"OllamaChat initialized | model='{self.model}' | url='{self.base_url}'")

    def _is_server_running(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except requests.ConnectionError:
            return False

    def chat(self, prompt: str, system: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Send a user message to the local Ollama model and return its reply.

        Args:
            prompt: The user message.
            system: Optional system prompt.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.

        Returns:
            Model's response as a plain string.

        Raises:
            ValueError: If prompt is empty.
            RuntimeError: If Ollama server is unreachable or the call fails.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        if not self._is_server_running():
            raise RuntimeError(
                f"Ollama server not reachable at '{self.base_url}'. Run: ollama serve"
            )

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model, "messages": messages, "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        try:
            response = requests.post(self._chat_url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.HTTPError as e:
            raise RuntimeError(f"Ollama request failed: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Ollama error: {e}") from e

    def stream(self, prompt: str, system: Optional[str] = None,
               temperature: float = 0.7, max_tokens: int = 1024) -> Generator[str, None, None]:
        """Stream the Ollama model's reply token by token."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        if not self._is_server_running():
            raise RuntimeError(
                f"Ollama server not reachable at '{self.base_url}'. Run: ollama serve"
            )

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model, "messages": messages, "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        try:
            with requests.post(self._chat_url, json=payload, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        delta = chunk.get("message", {}).get("content", "")
                        if delta:
                            yield delta
                        if chunk.get("done"):
                            break
        except Exception as e:
            raise RuntimeError(f"Ollama streaming error: {e}") from e
