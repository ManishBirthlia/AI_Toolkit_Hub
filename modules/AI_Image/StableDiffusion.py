from typing import Optional
import requests

from utils.config import get_api_key
from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)


class StableDiffusionClient:
    """Stable Diffusion via Stability AI REST API."""

    DEFAULT_MODEL = "stable-image-core"
    _MODEL_URLS = {
        "stable-image-core":  "https://api.stability.ai/v2beta/stable-image/generate/core",
        "stable-diffusion-3": "https://api.stability.ai/v2beta/stable-image/generate/sd3",
        "stable-image-ultra": "https://api.stability.ai/v2beta/stable-image/generate/ultra",
    }

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        if model not in self._MODEL_URLS:
            raise ValueError(f"Unknown model '{model}'. Choose from: {list(self._MODEL_URLS)}")
        self.model = model
        self.api_key = get_api_key("STABILITY_API_KEY")
        self._url = self._MODEL_URLS[model]
        logger.info(f"StableDiffusionClient initialized | model='{self.model}'")

    def generate(self, prompt: str, negative_prompt: str = "",
                 width: int = 1024, height: int = 1024,
                 output_path: Optional[str] = None, output_format: str = "png") -> bytes:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of the desired image.
            negative_prompt: Things to exclude from the image.
            width: Image width in pixels.
            height: Image height in pixels.
            output_path: If provided, saves the image to this path.
            output_format: 'png' or 'jpeg'.

        Returns:
            Raw image bytes.

        Raises:
            ValueError: If prompt is empty or dimensions too small.
            RuntimeError: If the API call fails.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        if width < 64 or height < 64:
            raise ValueError("Dimensions must be at least 64x64.")

        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "image/*"}
        data = {"prompt": prompt, "output_format": output_format}
        if negative_prompt:
            data["negative_prompt"] = negative_prompt

        try:
            response = requests.post(self._url, headers=headers,
                                     files={"none": ""}, data=data, timeout=120)
            if response.status_code != 200:
                raise RuntimeError(f"Stability AI error {response.status_code}: {response.text}")
            image_bytes = response.content
            if output_path:
                save_bytes_to_file(image_bytes, output_path)
            return image_bytes
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Stable Diffusion error: {e}") from e
