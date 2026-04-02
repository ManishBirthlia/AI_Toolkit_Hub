import time
from typing import Optional
import requests

from utils.config import get_api_key
from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)

_POLL_INTERVAL_SEC = 2
_MAX_POLL_ATTEMPTS = 60


class FLUXClient:
    """FLUX image generation via Replicate API."""

    DEFAULT_MODEL = "black-forest-labs/flux-schnell"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.api_key = get_api_key("REPLICATE_API_KEY")
        self._headers = {"Authorization": f"Bearer {self.api_key}",
                         "Content-Type": "application/json"}
        logger.info(f"FLUXClient initialized | model='{self.model}'")

    def generate(self, prompt: str, width: int = 1024, height: int = 1024,
                 num_inference_steps: int = 4, guidance_scale: float = 3.5,
                 output_path: Optional[str] = None) -> bytes:
        """
        Generate an image using FLUX via Replicate. Polls until complete.

        Args:
            prompt: Text description of the desired image.
            width: Image width in pixels.
            height: Image height in pixels.
            num_inference_steps: Denoising steps (4 for schnell, 20-50 for dev).
            guidance_scale: Classifier-free guidance scale.
            output_path: If provided, saves the image to this path.

        Returns:
            Raw image bytes.

        Raises:
            ValueError: If prompt is empty.
            RuntimeError: If the prediction fails or times out.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        url = f"https://api.replicate.com/v1/models/{self.model}/predictions"
        payload = {"input": {"prompt": prompt, "width": width, "height": height,
                              "num_inference_steps": num_inference_steps,
                              "guidance_scale": guidance_scale}}
        try:
            resp = requests.post(url, json=payload, headers=self._headers, timeout=30)
            resp.raise_for_status()
            prediction_id = resp.json()["id"]
            poll_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"

            for _ in range(_MAX_POLL_ATTEMPTS):
                time.sleep(_POLL_INTERVAL_SEC)
                poll = requests.get(poll_url, headers=self._headers, timeout=15)
                poll.raise_for_status()
                result = poll.json()
                status = result.get("status")

                if status == "succeeded":
                    output = result.get("output", [])
                    image_url = output[0] if isinstance(output, list) else output
                    image_bytes = requests.get(image_url, timeout=60).content
                    if output_path:
                        save_bytes_to_file(image_bytes, output_path)
                    return image_bytes
                elif status == "failed":
                    raise RuntimeError(f"FLUX prediction failed: {result.get('error')}")

            raise RuntimeError("FLUX prediction timed out.")
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"FLUX error: {e}") from e
