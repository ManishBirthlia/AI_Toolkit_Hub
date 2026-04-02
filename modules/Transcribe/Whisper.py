from pathlib import Path
from typing import Optional, Union, Literal

try:
    from openai import OpenAI, APIError
except ImportError as e:
    raise ImportError("pip install openai") from e

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)

_MAX_FILE_SIZE_MB = 25


class WhisperTranscriber:
    """OpenAI Whisper transcription. Modes: 'api' (cloud) or 'local' (on-device)."""

    DEFAULT_MODEL = "whisper-1"

    def __init__(self, mode: Literal["api", "local"] = "api",
                 model: str = DEFAULT_MODEL) -> None:
        if mode not in ("api", "local"):
            raise ValueError("mode must be 'api' or 'local'.")
        self.mode = mode
        self.model = model
        self._local_model = None
        if mode == "api":
            self.client = OpenAI(api_key=get_api_key("OPENAI_API_KEY"))
        logger.info(f"WhisperTranscriber initialized | mode={mode} | model='{model}'")

    def _load_local_model(self):
        if self._local_model is None:
            try:
                import whisper
            except ImportError as e:
                raise ImportError("pip install openai-whisper") from e
            self._local_model = whisper.load_model(self.model)
        return self._local_model

    def transcribe(self, audio_path: str, language: Optional[str] = None,
                   prompt: Optional[str] = None,
                   response_format: Literal["text", "json", "srt", "vtt"] = "text") -> Union[str, dict]:
        """Transcribe an audio/video file to text.

        Args:
            audio_path: Path to the audio/video file.
            language: Optional ISO-639-1 language code (e.g. 'en', 'hi').
            prompt: Optional context hint to improve accuracy.
            response_format: Output format ('text', 'json', 'srt', 'vtt').

        Returns:
            Transcription as string (text/srt/vtt) or dict (json).

        Raises:
            ValueError: If audio_path is empty or file not found.
            RuntimeError: If transcription fails.
        """
        if not audio_path:
            raise ValueError("audio_path cannot be empty.")
        path = Path(audio_path)
        if not path.exists():
            raise ValueError(f"Audio file not found: {audio_path}")
        if self.mode == "api":
            return self._transcribe_api(path, language, prompt, response_format)
        return self._transcribe_local(path, language, prompt)

    def _transcribe_api(self, path: Path, language, prompt, response_format) -> Union[str, dict]:
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > _MAX_FILE_SIZE_MB:
            raise ValueError(f"File size {size_mb:.1f}MB exceeds the Whisper API "
                             f"limit of {_MAX_FILE_SIZE_MB}MB. Use mode='local'.")
        kwargs = {"model": self.model, "response_format": response_format}
        if language:
            kwargs["language"] = language
        if prompt:
            kwargs["prompt"] = prompt
        try:
            with open(path, "rb") as f:
                response = self.client.audio.transcriptions.create(file=f, **kwargs)
            if response_format == "json":
                return response.model_dump()
            return response.text if hasattr(response, "text") else str(response)
        except APIError as e:
            raise RuntimeError(f"Whisper API transcription failed: {e}") from e

    def _transcribe_local(self, path: Path, language, prompt) -> str:
        model = self._load_local_model()
        kwargs = {}
        if language:
            kwargs["language"] = language
        if prompt:
            kwargs["initial_prompt"] = prompt
        try:
            result = model.transcribe(str(path), **kwargs)
            return result.get("text", "").strip()
        except Exception as e:
            raise RuntimeError(f"Whisper local transcription failed: {e}") from e

    def translate(self, audio_path: str, prompt: Optional[str] = None) -> str:
        """Transcribe and translate audio to English (API mode only)."""
        if self.mode != "api":
            raise ValueError("translate() is only available in API mode.")
        if not audio_path:
            raise ValueError("audio_path cannot be empty.")
        path = Path(audio_path)
        if not path.exists():
            raise ValueError(f"Audio file not found: {audio_path}")
        kwargs = {"model": self.model}
        if prompt:
            kwargs["prompt"] = prompt
        try:
            with open(path, "rb") as f:
                response = self.client.audio.translations.create(file=f, **kwargs)
            return response.text
        except APIError as e:
            raise RuntimeError(f"Whisper translation failed: {e}") from e
