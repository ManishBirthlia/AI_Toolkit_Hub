import base64
from pathlib import Path
from typing import Optional

try:
    import cv2
except ImportError as e:
    raise ImportError("pip install opencv-python") from e

from openai import OpenAI, APIError
from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class VideoAnalysisClient:
    """AI video analysis using frame extraction + GPT-4o Vision."""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(self, model: str = DEFAULT_MODEL, max_frames: int = 10) -> None:
        self.model = model
        self.max_frames = max_frames
        self.client = OpenAI(api_key=get_api_key("OPENAI_API_KEY"))
        logger.info(f"VideoAnalysisClient initialized | model='{self.model}' | max_frames={self.max_frames}")

    def extract_frames(self, video_path: str) -> list[bytes]:
        """Extract evenly-spaced frames from a video as JPEG bytes.

        Args:
            video_path: Path to the video file.

        Returns:
            List of JPEG image bytes.

        Raises:
            ValueError: If video_path is empty or file not found.
            RuntimeError: If frame extraction fails.
        """
        if not video_path:
            raise ValueError("video_path cannot be empty.")
        path = Path(video_path)
        if not path.exists():
            raise ValueError(f"Video file not found: {video_path}")

        try:
            cap = cv2.VideoCapture(str(path))
            if not cap.isOpened():
                raise RuntimeError(f"Could not open video: {video_path}")
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            step = max(1, total_frames // self.max_frames)
            frame_indices = list(range(0, total_frames, step))[:self.max_frames]

            frames = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                _, buffer = cv2.imencode(".jpg", frame)
                frames.append(buffer.tobytes())
            cap.release()
            logger.info(f"Extracted {len(frames)} frames from video.")
            return frames
        except (ValueError, RuntimeError):
            raise
        except Exception as e:
            raise RuntimeError(f"Frame extraction error: {e}") from e

    def analyze(self, video_path: str,
                prompt: str = "Describe what is happening in this video.") -> str:
        """Analyze a video by sending extracted frames to GPT-4o Vision.

        Args:
            video_path: Path to the video file.
            prompt: Question or instruction for the model.

        Returns:
            Model's analysis as a plain string.

        Raises:
            ValueError: If video_path or prompt is empty.
            RuntimeError: If frame extraction or the API call fails.
        """
        if not video_path:
            raise ValueError("video_path cannot be empty.")
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        frames = self.extract_frames(video_path)
        if not frames:
            raise RuntimeError("No frames could be extracted from the video.")

        content = [{"type": "text", "text": prompt}]
        for frame_bytes in frames:
            b64 = base64.b64encode(frame_bytes).decode()
            content.append({"type": "image_url",
                             "image_url": {"url": f"data:image/jpeg;base64,{b64}",
                                           "detail": "low"}})
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except APIError as e:
            raise RuntimeError(f"Video analysis API error: {e}") from e

    def caption(self, video_path: str) -> str:
        """Generate a concise one-sentence caption for the video."""
        return self.analyze(video_path,
                            prompt="Generate a single concise caption (one sentence) "
                                   "that best describes this video.")
