import asyncio
from typing import Optional

try:
    import edge_tts
except ImportError as e:
    raise ImportError("pip install edge-tts") from e

from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)


class EdgeTTS:
    """Microsoft Edge TTS — free, no API key required. 400+ voices."""

    DEFAULT_VOICE = "en-US-JennyNeural"

    def __init__(self, voice: str = DEFAULT_VOICE) -> None:
        self.voice = voice
        logger.info(f"EdgeTTS initialized | voice='{self.voice}'")

    def synthesize(self, text: str, rate: str = "+0%", volume: str = "+0%",
                   pitch: str = "+0Hz", output_path: Optional[str] = None) -> bytes:
        """Convert text to speech using Microsoft Edge TTS.

        Args:
            text: Text to synthesize.
            rate: Speaking rate adjustment (e.g. '+20%' or '-10%').
            volume: Volume adjustment (e.g. '+10%').
            pitch: Pitch adjustment (e.g. '+5Hz').
            output_path: If provided, saves audio to this path (MP3).

        Returns:
            Raw MP3 audio bytes.

        Raises:
            ValueError: If text is empty.
            RuntimeError: If synthesis fails.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
        try:
            audio_bytes = asyncio.run(self._synthesize_async(text, rate, volume, pitch))
            if output_path:
                save_bytes_to_file(audio_bytes, output_path)
            return audio_bytes
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Edge TTS synthesis failed: {e}") from e

    async def _synthesize_async(self, text: str, rate: str,
                                 volume: str, pitch: str) -> bytes:
        communicate = edge_tts.Communicate(text=text, voice=self.voice,
                                           rate=rate, volume=volume, pitch=pitch)
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks)

    @staticmethod
    def list_voices() -> list[dict]:
        """Fetch all available Edge TTS voices."""
        try:
            voices = asyncio.run(edge_tts.list_voices())
            return voices
        except Exception as e:
            raise RuntimeError(f"Could not fetch Edge TTS voices: {e}") from e
