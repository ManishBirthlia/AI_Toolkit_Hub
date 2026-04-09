"""
audio.py — Audio / voice tools for the Jarvis AI agent.

Provides text-to-speech (TTS), microphone voice-command listening, and
audio file transcription.  Uses ``pyttsx3`` for offline TTS,
``speech_recognition`` for mic input, and ``openai-whisper`` or the
``SpeechRecognition`` Google backend for transcription.
"""

import os
import tempfile

try:
    import pyttsx3
    _PYTTSX3_AVAILABLE = True
except ImportError:
    _PYTTSX3_AVAILABLE = False
    print("[audio] ⚠  pyttsx3 not installed — speak() will not work.  "
          "pip install pyttsx3")

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False
    print("[audio] ⚠  SpeechRecognition not installed — listen/transcribe disabled.  "
          "pip install SpeechRecognition")

try:
    import whisper as openai_whisper
    _WHISPER_AVAILABLE = True
except ImportError:
    _WHISPER_AVAILABLE = False
    # Silently skip — optional, we fall back to Google STT


# ── Public Tool Functions ────────────────────────────────────────────────────

def speak(text: str, rate: int = 175, voice_index: int = 0) -> dict:
    """Convert text to speech and play it through the default audio output.

    Uses ``pyttsx3`` for fully offline, Windows-compatible TTS.

    Args:
        text:        The text to speak aloud.
        rate:        Speech rate in words per minute (default 175).
        voice_index: Index of the system voice to use (0 = first available).

    Returns:
        dict confirming speech output.
    """
    if not _PYTTSX3_AVAILABLE:
        return {"success": False, "result": None, "error": "pyttsx3 is not installed."}
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)

        voices = engine.getProperty("voices")
        if voices and 0 <= voice_index < len(voices):
            engine.setProperty("voice", voices[voice_index].id)

        engine.say(text)
        engine.runAndWait()
        engine.stop()
        return {"success": True, "result": f"Spoke {len(text)} characters", "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def listen_for_command(timeout: int = 5, phrase_limit: int = 15) -> dict:
    """Listen on the microphone and transcribe the spoken command.

    Uses the default microphone via ``SpeechRecognition``.  Transcription
    is done with Google's free web API by default.

    Args:
        timeout:       Seconds to wait for speech to begin (default 5).
        phrase_limit:  Maximum seconds of speech to capture (default 15).

    Returns:
        dict with the transcribed text in ``result``.
    """
    if not _SR_AVAILABLE:
        return {"success": False, "result": None,
                "error": "SpeechRecognition is not installed. Run: pip install SpeechRecognition"}
    try:
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

        # Try Google STT (free, no API key needed for light use)
        text = recognizer.recognize_google(audio)
        return {"success": True, "result": text, "error": None}
    except sr.WaitTimeoutError:
        return {"success": False, "result": None, "error": "No speech detected within timeout."}
    except sr.UnknownValueError:
        return {"success": False, "result": None, "error": "Could not understand the audio."}
    except sr.RequestError as exc:
        return {"success": False, "result": None, "error": f"Speech recognition service error: {exc}"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def transcribe_audio(file_path: str, model_name: str = "base") -> dict:
    """Transcribe an audio file to text.

    Tries OpenAI Whisper (local) first for accuracy, then falls back
    to SpeechRecognition's Google backend.

    Args:
        file_path:  Path to the audio file (WAV, MP3, M4A, etc.).
        model_name: Whisper model size — 'tiny', 'base', 'small', 'medium',
                    'large' (default 'base').  Only used with local Whisper.

    Returns:
        dict with the transcribed text in ``result``.
    """
    if not os.path.isfile(file_path):
        return {"success": False, "result": None, "error": f"Audio file not found: {file_path}"}

    # Strategy 1: Local Whisper (best quality)
    if _WHISPER_AVAILABLE:
        try:
            model = openai_whisper.load_model(model_name)
            result = model.transcribe(file_path)
            return {"success": True, "result": result["text"].strip(), "error": None}
        except Exception as exc:
            # Fall through to Google STT
            pass

    # Strategy 2: SpeechRecognition with Google
    if _SR_AVAILABLE:
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(file_path) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            return {"success": True, "result": text, "error": None}
        except sr.UnknownValueError:
            return {"success": False, "result": None,
                    "error": "Could not understand audio content."}
        except Exception as exc:
            return {"success": False, "result": None, "error": str(exc)}

    return {
        "success": False, "result": None,
        "error": "No transcription backend available. Install openai-whisper or SpeechRecognition.",
    }


# ── Anthropic Tool Schema ────────────────────────────────────────────────────

def get_tool_schema() -> list[dict]:
    """Return Anthropic-compatible tool definitions for this module."""
    return [
        {
            "name": "speak",
            "description": "Convert text to speech and play it through the system speakers (offline TTS).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to speak aloud."
                    },
                    "rate": {
                        "type": "integer",
                        "description": "Speech rate in words per minute. Defaults to 175."
                    },
                    "voice_index": {
                        "type": "integer",
                        "description": "Index of the system voice to use. Defaults to 0."
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "listen_for_command",
            "description": "Listen on the microphone for a spoken command and transcribe it to text.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Seconds to wait for speech to begin. Defaults to 5."
                    },
                    "phrase_limit": {
                        "type": "integer",
                        "description": "Maximum seconds of speech to capture. Defaults to 15."
                    }
                },
                "required": []
            }
        },
        {
            "name": "transcribe_audio",
            "description": "Transcribe an audio file (WAV, MP3, etc.) to text using Whisper or Google STT.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the audio file to transcribe."
                    },
                    "model_name": {
                        "type": "string",
                        "enum": ["tiny", "base", "small", "medium", "large"],
                        "description": "Whisper model size. Defaults to 'base'. Only used with local Whisper."
                    }
                },
                "required": ["file_path"]
            }
        },
    ]
