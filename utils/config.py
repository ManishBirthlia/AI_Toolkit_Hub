import os
from dotenv import load_dotenv

load_dotenv()

_REQUIRED_KEYS: dict[str, str] = {
    "OPENAI_API_KEY":       "OpenAI (LLMs, DALL·E)",
    "ANTHROPIC_API_KEY":    "Anthropic Claude (LLMs)",
    "GROQ_API_KEY":         "Groq (LLMs)",
    "GEMINI_API_KEY":       "Google Gemini (LLMs)",
    "STABILITY_API_KEY":    "Stable Diffusion (AI_Image)",
    "REPLICATE_API_KEY":    "FLUX via Replicate (AI_Image)",
    "RUNWAY_API_KEY":       "RunwayML (AI_Video)",
    "KLING_API_KEY":        "KlingAI (AI_Video)",
    "ELEVENLABS_API_KEY":   "ElevenLabs (TTS)",
    "GOOGLE_API_KEY":       "Google Cloud (TTS, Translate, Maps, Vision)",
    "ASSEMBLYAI_API_KEY":   "AssemblyAI (Transcribe)",
    "DEEPGRAM_API_KEY":     "Deepgram (Transcribe)",
    "DEEPL_API_KEY":        "DeepL (Translate)",
    "BITLY_API_KEY":        "Bitly (Short_Link)",
    "REBRANDLY_API_KEY":    "Rebrandly (Short_Link)",
}


def get_api_key(key_name: str, required: bool = True) -> str:
    value = os.getenv(key_name, "").strip()
    if not value and required:
        provider_hint = _REQUIRED_KEYS.get(key_name, key_name)
        raise RuntimeError(
            f"Missing API key: '{key_name}' (used by: {provider_hint}). "
            f"Add it to your .env file."
        )
    return value


def get_all_configured_keys() -> dict[str, bool]:
    return {key: bool(os.getenv(key, "").strip()) for key in _REQUIRED_KEYS}
