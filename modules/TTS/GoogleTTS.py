from typing import Optional

try:
    from google.cloud import texttospeech
except ImportError as e:
    raise ImportError("pip install google-cloud-texttospeech") from e

from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)


class GoogleTTS:
    """Google Cloud Text-to-Speech provider. Supports 380+ voices across 50+ languages."""

    DEFAULT_LANGUAGE = "en-US"
    DEFAULT_VOICE = "en-US-Neural2-F"

    def __init__(self, language_code: str = DEFAULT_LANGUAGE,
                 voice_name: str = DEFAULT_VOICE) -> None:
        self.language_code = language_code
        self.voice_name = voice_name
        self.client = texttospeech.TextToSpeechClient()
        logger.info(f"GoogleTTS initialized | lang='{self.language_code}' | voice='{self.voice_name}'")

    def synthesize(self, text: str, audio_encoding: str = "MP3",
                   speaking_rate: float = 1.0, pitch: float = 0.0,
                   output_path: Optional[str] = None) -> bytes:
        """Convert text to speech using Google Cloud TTS.

        Args:
            text: Text or SSML to synthesize.
            audio_encoding: 'MP3', 'LINEAR16' (WAV), or 'OGG_OPUS'.
            speaking_rate: Speed multiplier (0.25–4.0).
            pitch: Pitch shift in semitones (-20.0 to 20.0).
            output_path: If provided, saves audio to this path.

        Returns:
            Raw audio bytes.

        Raises:
            ValueError: If text is empty or params out of range.
            RuntimeError: If the API call fails.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
        if not 0.25 <= speaking_rate <= 4.0:
            raise ValueError("speaking_rate must be between 0.25 and 4.0.")
        if not -20.0 <= pitch <= 20.0:
            raise ValueError("pitch must be between -20.0 and 20.0.")

        encoding_map = {"MP3": texttospeech.AudioEncoding.MP3,
                        "LINEAR16": texttospeech.AudioEncoding.LINEAR16,
                        "OGG_OPUS": texttospeech.AudioEncoding.OGG_OPUS}
        if audio_encoding not in encoding_map:
            raise ValueError(f"audio_encoding must be one of {list(encoding_map)}.")

        try:
            response = self.client.synthesize_speech(
                input=texttospeech.SynthesisInput(text=text),
                voice=texttospeech.VoiceSelectionParams(
                    language_code=self.language_code, name=self.voice_name),
                audio_config=texttospeech.AudioConfig(
                    audio_encoding=encoding_map[audio_encoding],
                    speaking_rate=speaking_rate, pitch=pitch),
            )
            audio_bytes = response.audio_content
            if output_path:
                save_bytes_to_file(audio_bytes, output_path)
            return audio_bytes
        except Exception as e:
            raise RuntimeError(f"Google TTS synthesis failed: {e}") from e
