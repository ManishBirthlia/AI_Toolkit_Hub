from typing import Optional
import requests

from utils.config import get_api_key
from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)

_API_BASE = "https://api.elevenlabs.io/v1"


class ElevenLabsTTS:
    """ElevenLabs provider for ultra-realistic text-to-speech synthesis."""

    DEFAULT_MODEL = "eleven_multilingual_v2"
    _VALID_MODELS = {"eleven_multilingual_v2", "eleven_turbo_v2",
                     "eleven_turbo_v2_5", "eleven_monolingual_v1"}
    VOICES = {"rachel": "21m00Tcm4TlvDq8ikWAM", "adam": "pNInz6obpgDQGcFmaJgB",
              "bella": "EXAVITQu4vr4xnSDxMaL", "josh": "TxGEqnHWrfWFTfGW9XjX"}

    def __init__(self, voice_id: str = "21m00Tcm4TlvDq8ikWAM",
                 model: str = DEFAULT_MODEL) -> None:
        if model not in self._VALID_MODELS:
            raise ValueError(f"Unknown model '{model}'.")
        self.voice_id = voice_id
        self.model = model
        self.api_key = get_api_key("ELEVENLABS_API_KEY")
        self._headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        logger.info(f"ElevenLabsTTS initialized | voice={self.voice_id} | model='{self.model}'")

    def synthesize(self, text: str, stability: float = 0.5, similarity_boost: float = 0.75,
                   style: float = 0.0, output_path: Optional[str] = None) -> bytes:
        """Convert text to speech and return audio bytes.

        Args:
            text: Text to synthesize (max ~5000 chars).
            stability: Voice stability (0.0–1.0).
            similarity_boost: Voice clarity boost (0.0–1.0).
            style: Style exaggeration (0.0–1.0).
            output_path: If provided, saves audio to this path (MP3).

        Returns:
            Raw MP3 audio bytes.

        Raises:
            ValueError: If text is empty or params out of range.
            RuntimeError: If the API call fails.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
        if not 0.0 <= stability <= 1.0:
            raise ValueError("stability must be between 0.0 and 1.0.")
        if not 0.0 <= similarity_boost <= 1.0:
            raise ValueError("similarity_boost must be between 0.0 and 1.0.")

        url = f"{_API_BASE}/text-to-speech/{self.voice_id}"
        payload = {"text": text, "model_id": self.model,
                   "voice_settings": {"stability": stability,
                                      "similarity_boost": similarity_boost,
                                      "style": style, "use_speaker_boost": True}}
        try:
            resp = requests.post(url, json=payload, headers=self._headers, timeout=60)
            resp.raise_for_status()
            audio_bytes = resp.content
            if output_path:
                save_bytes_to_file(audio_bytes, output_path)
            return audio_bytes
        except requests.HTTPError as e:
            raise RuntimeError(f"ElevenLabs API error: {e}") from e
        except Exception as e:
            raise RuntimeError(f"ElevenLabs TTS error: {e}") from e

    def list_voices(self) -> list[dict]:
        """Fetch all available voices from the ElevenLabs account."""
        try:
            resp = requests.get(f"{_API_BASE}/voices", headers=self._headers, timeout=15)
            resp.raise_for_status()
            return resp.json().get("voices", [])
        except Exception as e:
            raise RuntimeError(f"Could not fetch ElevenLabs voices: {e}") from e
