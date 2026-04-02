import time
import base64
import hmac
import hashlib
from pathlib import Path
from typing import Optional
import requests

from utils.config import get_api_key
from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)

_API_BASE = "https://api.klingai.com/v1"
_POLL_INTERVAL_SEC = 5
_MAX_POLL_ATTEMPTS = 120


class KlingAIClient:
    """Kling AI provider for high-quality video generation."""

    DEFAULT_MODEL = "kling-v1"
    _VALID_MODES = {"std", "pro"}
    _VALID_DURATIONS = {"5", "10"}
    _VALID_RATIOS = {"16:9", "9:16", "1:1"}

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.api_key = get_api_key("KLING_API_KEY")
        self.api_secret = get_api_key("KLING_API_SECRET")
        logger.info(f"KlingAIClient initialized | model='{self.model}'")

    def _get_auth_headers(self) -> dict:
        timestamp = str(int(time.time()))
        sign_str = f"{self.api_key}{timestamp}"
        signature = hmac.new(self.api_secret.encode(),
                              sign_str.encode(), hashlib.sha256).hexdigest()
        return {"Content-Type": "application/json", "X-Api-Key": self.api_key,
                "X-Timestamp": timestamp, "X-Signature": signature}

    def text_to_video(self, prompt: str, negative_prompt: str = "", mode: str = "std",
                      duration: str = "5", aspect_ratio: str = "16:9",
                      output_path: Optional[str] = None) -> bytes:
        """Generate a video from a text prompt using Kling AI.

        Args:
            prompt: Text description of the video.
            negative_prompt: Elements to avoid.
            mode: 'std' or 'pro'.
            duration: '5' or '10' seconds.
            aspect_ratio: '16:9', '9:16', or '1:1'.
            output_path: If provided, saves video to this path.

        Returns:
            Raw MP4 video bytes.

        Raises:
            ValueError: If prompt is empty or params are invalid.
            RuntimeError: If generation fails or times out.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        if mode not in self._VALID_MODES:
            raise ValueError(f"mode must be one of {self._VALID_MODES}.")
        if duration not in self._VALID_DURATIONS:
            raise ValueError(f"duration must be one of {self._VALID_DURATIONS}.")
        if aspect_ratio not in self._VALID_RATIOS:
            raise ValueError(f"aspect_ratio must be one of {self._VALID_RATIOS}.")

        payload = {"model": self.model, "prompt": prompt, "mode": mode,
                   "duration": duration, "aspect_ratio": aspect_ratio}
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        return self._submit_and_poll(f"{_API_BASE}/videos/text2video", payload, output_path)

    def image_to_video(self, image_path: str, prompt: str = "", negative_prompt: str = "",
                       mode: str = "std", duration: str = "5",
                       output_path: Optional[str] = None) -> bytes:
        """Animate a static image into a video using Kling AI.

        Args:
            image_path: Path to source image (JPEG or PNG).
            prompt: Optional motion prompt.
            negative_prompt: Elements to avoid.
            mode: 'std' or 'pro'.
            duration: '5' or '10' seconds.
            output_path: If provided, saves video to this path.

        Returns:
            Raw MP4 video bytes.

        Raises:
            ValueError: If image_path is invalid.
            RuntimeError: If generation fails or times out.
        """
        if not image_path:
            raise ValueError("image_path cannot be empty.")
        path = Path(image_path)
        if not path.exists():
            raise ValueError(f"Image file not found: {image_path}")
        if mode not in self._VALID_MODES:
            raise ValueError(f"mode must be one of {self._VALID_MODES}.")

        b64 = base64.b64encode(path.read_bytes()).decode()
        suffix = path.suffix.lower()
        mime = "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png"
        payload = {"model": self.model, "image": f"data:{mime};base64,{b64}",
                   "mode": mode, "duration": duration}
        if prompt:
            payload["prompt"] = prompt
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        return self._submit_and_poll(f"{_API_BASE}/videos/image2video", payload, output_path)

    def _submit_and_poll(self, endpoint: str, payload: dict,
                         output_path: Optional[str]) -> bytes:
        try:
            resp = requests.post(endpoint, json=payload,
                                 headers=self._get_auth_headers(), timeout=30)
            resp.raise_for_status()
            task_id = resp.json().get("data", {}).get("task_id")
            if not task_id:
                raise RuntimeError("KlingAI did not return a task_id.")

            poll_url = f"{_API_BASE}/videos/text2video/{task_id}"
            for attempt in range(_MAX_POLL_ATTEMPTS):
                time.sleep(_POLL_INTERVAL_SEC)
                poll = requests.get(poll_url, headers=self._get_auth_headers(), timeout=15)
                poll.raise_for_status()
                data = poll.json().get("data", {})
                status = data.get("task_status")
                if status == "succeed":
                    works = data.get("task_result", {}).get("videos", [])
                    if not works:
                        raise RuntimeError("KlingAI succeeded but no video URLs.")
                    video_bytes = requests.get(works[0].get("url"), timeout=120).content
                    if output_path:
                        save_bytes_to_file(video_bytes, output_path)
                    return video_bytes
                elif status == "failed":
                    raise RuntimeError(f"KlingAI task failed: {data.get('task_status_msg')}")
                logger.debug(f"KlingAI status={status} | attempt={attempt+1}")

            raise RuntimeError("KlingAI timed out.")
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"KlingAI error: {e}") from e
