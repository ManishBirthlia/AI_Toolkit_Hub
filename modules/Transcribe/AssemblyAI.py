import time
from pathlib import Path
import requests

from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)

_API_BASE = "https://api.assemblyai.com/v2"
_POLL_INTERVAL_SEC = 3
_MAX_POLL_ATTEMPTS = 200


class AssemblyAITranscriber:
    """AssemblyAI transcription with speaker diarization, chapters, and sentiment."""

    def __init__(self) -> None:
        self.api_key = get_api_key("ASSEMBLYAI_API_KEY")
        self._headers = {"authorization": self.api_key, "content-type": "application/json"}
        logger.info("AssemblyAITranscriber initialized.")

    def _upload_file(self, audio_path: str) -> str:
        try:
            with open(audio_path, "rb") as f:
                resp = requests.post(f"{_API_BASE}/upload",
                                     headers={"authorization": self.api_key},
                                     data=f, timeout=120)
            resp.raise_for_status()
            return resp.json().get("upload_url")
        except Exception as e:
            raise RuntimeError(f"AssemblyAI file upload error: {e}") from e

    def transcribe(self, source: str, language_code: str = "en",
                   speaker_labels: bool = False, auto_chapters: bool = False,
                   sentiment_analysis: bool = False, redact_pii: bool = False,
                   content_safety: bool = False) -> dict:
        """Transcribe audio from a file path or public URL.

        Args:
            source: Local file path or publicly accessible URL.
            language_code: ISO-639-1 language code (e.g. 'en', 'hi').
            speaker_labels: Enable speaker diarization.
            auto_chapters: Auto-generate chapter summaries.
            sentiment_analysis: Analyze sentiment per utterance.
            redact_pii: Redact personally identifiable information.
            content_safety: Detect sensitive content categories.

        Returns:
            Dict containing 'text', 'words', 'utterances', 'chapters', etc.

        Raises:
            ValueError: If source is empty.
            RuntimeError: If transcription fails or times out.
        """
        if not source:
            raise ValueError("source cannot be empty.")

        audio_url = self._upload_file(source) if Path(source).exists() else source
        payload = {"audio_url": audio_url, "language_code": language_code,
                   "speaker_labels": speaker_labels, "auto_chapters": auto_chapters,
                   "sentiment_analysis": sentiment_analysis, "redact_pii": redact_pii,
                   "content_safety": content_safety}

        try:
            resp = requests.post(f"{_API_BASE}/transcript", json=payload,
                                 headers=self._headers, timeout=30)
            resp.raise_for_status()
            transcript_id = resp.json().get("id")
            if not transcript_id:
                raise RuntimeError("AssemblyAI did not return a transcript ID.")

            poll_url = f"{_API_BASE}/transcript/{transcript_id}"
            for attempt in range(_MAX_POLL_ATTEMPTS):
                time.sleep(_POLL_INTERVAL_SEC)
                poll = requests.get(poll_url, headers=self._headers, timeout=15)
                poll.raise_for_status()
                data = poll.json()
                status = data.get("status")
                if status == "completed":
                    return data
                elif status == "error":
                    raise RuntimeError(f"AssemblyAI transcription error: {data.get('error')}")
                logger.debug(f"AssemblyAI status={status} | attempt={attempt+1}")

            raise RuntimeError("AssemblyAI timed out.")
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"AssemblyAI error: {e}") from e

    def get_text(self, source: str, language_code: str = "en") -> str:
        """Transcribe and return only the plain text."""
        return self.transcribe(source, language_code=language_code).get("text", "")
