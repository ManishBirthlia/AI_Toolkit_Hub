from pathlib import Path
from typing import Optional, Union

try:
    from deepgram import DeepgramClient, PrerecordedOptions, FileSource
except ImportError as e:
    raise ImportError("pip install deepgram-sdk") from e

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class DeepgramTranscriber:
    """Deepgram Nova-2 transcription with smart formatting and speaker diarization."""

    DEFAULT_MODEL = "nova-2"
    _VALID_MODELS = {"nova-2", "nova", "enhanced", "base", "whisper-large"}

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        if model not in self._VALID_MODELS:
            raise ValueError(f"Unknown model '{model}'. Valid: {self._VALID_MODELS}")
        self.model = model
        self.client = DeepgramClient(api_key=get_api_key("DEEPGRAM_API_KEY"))
        logger.info(f"DeepgramTranscriber initialized | model='{self.model}'")

    def transcribe(self, source: str, language: str = "en", smart_format: bool = True,
                   diarize: bool = False, punctuate: bool = True,
                   utterances: bool = False, keywords: Optional[list[str]] = None) -> dict:
        """Transcribe audio from a local file path or public URL.

        Args:
            source: Local file path or publicly accessible URL.
            language: BCP-47 language code (e.g. 'en', 'hi').
            smart_format: Apply intelligent formatting.
            diarize: Enable speaker diarization.
            punctuate: Add punctuation to transcript.
            utterances: Return utterance-level segments.
            keywords: List of keywords to boost recognition accuracy.

        Returns:
            Deepgram response dict with transcript and metadata.

        Raises:
            ValueError: If source is empty.
            RuntimeError: If transcription fails.
        """
        if not source:
            raise ValueError("source cannot be empty.")

        options = PrerecordedOptions(
            model=self.model, language=language, smart_format=smart_format,
            diarize=diarize, punctuate=punctuate, utterances=utterances,
            keywords=keywords or [],
        )

        try:
            path = Path(source)
            if path.exists():
                with open(path, "rb") as f:
                    audio_data = f.read()
                file_source: FileSource = {"buffer": audio_data}
                response = self.client.listen.prerecorded.v("1").transcribe_file(
                    file_source, options)
            else:
                response = self.client.listen.prerecorded.v("1").transcribe_url(
                    {"url": source}, options)
            return response.to_dict()
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Deepgram transcription failed: {e}") from e

    def get_text(self, source: str, language: str = "en",
                 smart_format: bool = True) -> str:
        """Transcribe and return only the plain text."""
        result = self.transcribe(source, language=language, smart_format=smart_format)
        return (result.get("results", {}).get("channels", [{}])[0]
                .get("alternatives", [{}])[0].get("transcript", ""))
