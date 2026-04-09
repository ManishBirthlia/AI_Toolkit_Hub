import json
import base64
import requests
from typing import Optional

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


def read_b64(path: str) -> str:
    """Read a file and return its base64 encoded string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


class NvidiaGemmaAI:
    """NVIDIA Gemma Model provider via Requests. Default: google/gemma-4-31b-it"""

    DEFAULT_MODEL = "google/gemma-4-31b-it"
    INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.api_key = get_api_key("NVIDIA_GEMMA_API_KEY")
        logger.info(f"NvidiaHostedChat initialized | model='{self.model}'")

    def _build_payload(self, prompt: str, system: Optional[str] = None, image_path: Optional[str] = None,
                       temperature: float = 1.0, max_tokens: int = 16384, stream: bool = False) -> dict:
        
        # Build contents array if image is present, or simple text if not
        if image_path:
            b64_img = read_b64(image_path)
            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
            ]
        else:
            content = prompt

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        
        messages.append({"role": "user", "content": content})

        return {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.95,
            "stream": stream,
            "chat_template_kwargs": {"enable_thinking": True},
        }

    def _get_headers(self, stream: bool = False) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream" if stream else "application/json",
            "Content-Type": "application/json"
        }

    def chat(self, prompt: str, system: Optional[str] = None, image_path: Optional[str] = None,
             temperature: float = 1.0, max_tokens: int = 16384) -> str:
        """
        Send a user message (and optional image) and return the model's reply.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        payload = self._build_payload(prompt, system, image_path, temperature, max_tokens, stream=False)
        headers = self._get_headers(stream=False)

        response = requests.post(self.INVOKE_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise RuntimeError(f"Nvidia Hosted API error: {response.status_code} - {response.text}")

        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"].get("content", "")
        return ""

    def stream(self, prompt: str, system: Optional[str] = None, image_path: Optional[str] = None,
               temperature: float = 1.0, max_tokens: int = 16384):
        """Stream the model's reply token by token."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        payload = self._build_payload(prompt, system, image_path, temperature, max_tokens, stream=True)
        headers = self._get_headers(stream=True)

        response = requests.post(self.INVOKE_URL, headers=headers, json=payload, stream=True)
        
        if response.status_code != 200:
            raise RuntimeError(f"Nvidia Hosted Streaming API error: {response.status_code} - {response.text}")

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        if getattr(chunk, "get", None):
                            choices = chunk.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                if "content" in delta and delta["content"]:
                                    yield delta["content"]
                    except json.JSONDecodeError:
                        continue
