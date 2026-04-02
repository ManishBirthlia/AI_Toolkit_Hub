import time
import base64
from pathlib import Path
from typing import Optional
import requests

from utils.config import get_api_key
from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)

_API_BASE = "https://api.dev.runwayml.com/v1"
_POLL_INTERVAL_SEC = 5
_MAX_POLL_ATTEMPTS = 120


class RunwayMLClient:
    """RunwayML provider for AI video generation (Gen-3 Alpha)."""

    DEFAULT_MODEL = "gen3a_turbo"
    _VALID_MODELS = {"gen3a_turbo", "gen-3-alpha"}
    _VALID_DURATIONS = {5, 10}
    _VALID_RATIOS = {"1280:720", "720:1280", "1104:832", "832:1104", "960:960"}

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        if model not in self._VALID_MODELS:
            raise ValueError(f"Unknown model '{model}'. Valid: {self._VALID_MODELS}")
        self.model = model
        self.api_key = get_api_key("RUNWAY_API_KEY")
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06",
        }
        logger.info(f"RunwayMLClient initialized | model='{self.model}'")

    def text_to_video(self, prompt: str, duration: int = 5,
                      ratio: str = "1280:720", output_path: Optional[str] = None) -> bytes:
        """Generate a video from a text prompt.

        Args:
            prompt: Text description of the video.
            duration: Duration in seconds (5 or 10).
            ratio: Aspect ratio string.
            output_path: If provided, saves video to this path.

        Returns:
            Raw MP4 video bytes.

        Raises:
            ValueError: If prompt is empty or params are invalid.
            RuntimeError: If generation fails or times out.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        if duration not in self._VALID_DURATIONS:
            raise ValueError(f"Duration must be one of {self._VALID_DURATIONS}.")
        if ratio not in self._VALID_RATIOS:
            raise ValueError(f"Invalid ratio. Valid: {self._VALID_RATIOS}")

        payload = {"model": self.model, "promptText": prompt,
                   "duration": duration, "ratio": ratio}
        return self._submit_and_poll(payload, output_path)

    def image_to_video(self, image_path: str, prompt: str = "", duration: int = 5,
                       ratio: str = "1280:720", output_path: Optional[str] = None) -> bytes:
        """Animate a static image into a video.

        Args:
            image_path: Path to source image (JPEG or PNG).
            prompt: Optional motion prompt.
            duration: Duration in seconds (5 or 10).
            ratio: Aspect ratio string.
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
        if duration not in self._VALID_DURATIONS:
            raise ValueError(f"Duration must be one of {self._VALID_DURATIONS}.")

        suffix = path.suffix.lower()
        mime = "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png"
        b64 = base64.b64encode(path.read_bytes()).decode()
        payload = {"model": self.model, "promptImage": f"data:{mime};base64,{b64}",
                   "duration": duration, "ratio": ratio}
        if prompt:
            payload["promptText"] = prompt
        return self._submit_and_poll(payload, output_path)

    def _submit_and_poll(self, payload: dict, output_path: Optional[str]) -> bytes:
        try:
            resp = requests.post(f"{_API_BASE}/image_to_video", json=payload,
                                 headers=self._headers, timeout=30)
            resp.raise_for_status()
            task_id = resp.json().get("id")
            if not task_id:
                raise RuntimeError("RunwayML did not return a task ID.")

            for attempt in range(_MAX_POLL_ATTEMPTS):
                time.sleep(_POLL_INTERVAL_SEC)
                poll = requests.get(f"{_API_BASE}/tasks/{task_id}",
                                    headers=self._headers, timeout=15)
                poll.raise_for_status()
                data = poll.json()
                status = data.get("status")
                if status == "SUCCEEDED":
                    video_url = data.get("output", [None])[0]
                    if not video_url:
                        raise RuntimeError("RunwayML succeeded but no output URL.")
                    video_bytes = requests.get(video_url, timeout=120).content
                    if output_path:
                        save_bytes_to_file(video_bytes, output_path)
                    return video_bytes
                elif status == "FAILED":
                    raise RuntimeError(f"RunwayML task failed: {data.get('failure')}")
                logger.debug(f"RunwayML status={status} | attempt={attempt+1}")

            raise RuntimeError("RunwayML timed out.")
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"RunwayML error: {e}") from e
