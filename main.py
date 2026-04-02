"""
AI Utility Toolkit — Central Orchestrator
==========================================
Usage:
    from main import toolkit
    toolkit.llms.openai.chat("Hello!")
    toolkit.transcribe.whisper.transcribe("audio.mp3")
    toolkit.qr.segno.generate_wifi("MyNet", "pass123")
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from utils.config import get_all_configured_keys
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LLMsNamespace:
    _openai: Optional[object] = field(default=None, repr=False)
    _claude: Optional[object] = field(default=None, repr=False)
    _groq:   Optional[object] = field(default=None, repr=False)
    _gemini: Optional[object] = field(default=None, repr=False)
    _ollama: Optional[object] = field(default=None, repr=False)

    @property
    def openai(self):
        if self._openai is None:
            from modules.LLMs.OpenAI import OpenAIChat
            self._openai = OpenAIChat()
        return self._openai

    @property
    def claude(self):
        if self._claude is None:
            from modules.LLMs.ClaudeAI import ClaudeChat
            self._claude = ClaudeChat()
        return self._claude

    @property
    def groq(self):
        if self._groq is None:
            from modules.LLMs.GroqAI import GroqChat
            self._groq = GroqChat()
        return self._groq

    @property
    def gemini(self):
        if self._gemini is None:
            from modules.LLMs.GeminiAI import GeminiChat
            self._gemini = GeminiChat()
        return self._gemini

    @property
    def ollama(self):
        if self._ollama is None:
            from modules.LLMs.OllamaAI import OllamaChat
            self._ollama = OllamaChat()
        return self._ollama


@dataclass
class OCRsNamespace:
    _tesseract:    Optional[object] = field(default=None, repr=False)
    _easyocr:      Optional[object] = field(default=None, repr=False)
    _googlevision: Optional[object] = field(default=None, repr=False)

    @property
    def tesseract(self):
        if self._tesseract is None:
            from modules.OCRs.Tesseract import TesseractOCR
            self._tesseract = TesseractOCR()
        return self._tesseract

    @property
    def easyocr(self):
        if self._easyocr is None:
            from modules.OCRs.EasyOCR import EasyOCRClient
            self._easyocr = EasyOCRClient()
        return self._easyocr

    @property
    def google_vision(self):
        if self._googlevision is None:
            from modules.OCRs.GoogleVision import GoogleVisionOCR
            self._googlevision = GoogleVisionOCR()
        return self._googlevision


@dataclass
class AIImageNamespace:
    _stablediffusion: Optional[object] = field(default=None, repr=False)
    _dalle:           Optional[object] = field(default=None, repr=False)
    _flux:            Optional[object] = field(default=None, repr=False)

    @property
    def stable_diffusion(self):
        if self._stablediffusion is None:
            from modules.AI_Image.StableDiffusion import StableDiffusionClient
            self._stablediffusion = StableDiffusionClient()
        return self._stablediffusion

    @property
    def dalle(self):
        if self._dalle is None:
            from modules.AI_Image.DALLE import DALLEClient
            self._dalle = DALLEClient()
        return self._dalle

    @property
    def flux(self):
        if self._flux is None:
            from modules.AI_Image.FLUX import FLUXClient
            self._flux = FLUXClient()
        return self._flux


@dataclass
class AIVideoNamespace:
    _runway:        Optional[object] = field(default=None, repr=False)
    _kling:         Optional[object] = field(default=None, repr=False)
    _videoanalysis: Optional[object] = field(default=None, repr=False)

    @property
    def runway(self):
        if self._runway is None:
            from modules.AI_Video.RunwayML import RunwayMLClient
            self._runway = RunwayMLClient()
        return self._runway

    @property
    def kling(self):
        if self._kling is None:
            from modules.AI_Video.KlingAI import KlingAIClient
            self._kling = KlingAIClient()
        return self._kling

    @property
    def analysis(self):
        if self._videoanalysis is None:
            from modules.AI_Video.VideoAnalysis import VideoAnalysisClient
            self._videoanalysis = VideoAnalysisClient()
        return self._videoanalysis


@dataclass
class TTSNamespace:
    _elevenlabs: Optional[object] = field(default=None, repr=False)
    _google:     Optional[object] = field(default=None, repr=False)
    _edge:       Optional[object] = field(default=None, repr=False)

    @property
    def elevenlabs(self):
        if self._elevenlabs is None:
            from modules.TTS.ElevenLabs import ElevenLabsTTS
            self._elevenlabs = ElevenLabsTTS()
        return self._elevenlabs

    @property
    def google(self):
        if self._google is None:
            from modules.TTS.GoogleTTS import GoogleTTS
            self._google = GoogleTTS()
        return self._google

    @property
    def edge(self):
        if self._edge is None:
            from modules.TTS.EdgeTTS import EdgeTTS
            self._edge = EdgeTTS()
        return self._edge


@dataclass
class TranscribeNamespace:
    _whisper:    Optional[object] = field(default=None, repr=False)
    _assemblyai: Optional[object] = field(default=None, repr=False)
    _deepgram:   Optional[object] = field(default=None, repr=False)

    @property
    def whisper(self):
        if self._whisper is None:
            from modules.Transcribe.Whisper import WhisperTranscriber
            self._whisper = WhisperTranscriber()
        return self._whisper

    @property
    def assemblyai(self):
        if self._assemblyai is None:
            from modules.Transcribe.AssemblyAI import AssemblyAITranscriber
            self._assemblyai = AssemblyAITranscriber()
        return self._assemblyai

    @property
    def deepgram(self):
        if self._deepgram is None:
            from modules.Transcribe.Deepgram import DeepgramTranscriber
            self._deepgram = DeepgramTranscriber()
        return self._deepgram


@dataclass
class TranslateNamespace:
    _deepl:  Optional[object] = field(default=None, repr=False)
    _google: Optional[object] = field(default=None, repr=False)
    _llm:    Optional[object] = field(default=None, repr=False)

    @property
    def deepl(self):
        if self._deepl is None:
            from modules.Translate.DeepL import DeepLTranslator
            self._deepl = DeepLTranslator()
        return self._deepl

    @property
    def google(self):
        if self._google is None:
            from modules.Translate.GoogleTranslate import GoogleTranslator
            self._google = GoogleTranslator()
        return self._google

    @property
    def llm(self):
        if self._llm is None:
            from modules.Translate.LLMTranslate import LLMTranslator
            self._llm = LLMTranslator()
        return self._llm


@dataclass
class MapNamespace:
    _google: Optional[object] = field(default=None, repr=False)
    _osm:    Optional[object] = field(default=None, repr=False)

    @property
    def google(self):
        if self._google is None:
            from modules.Map.GoogleMaps import GoogleMapsClient
            self._google = GoogleMapsClient()
        return self._google

    @property
    def osm(self):
        if self._osm is None:
            from modules.Map.OpenStreetMap import OpenStreetMapClient
            self._osm = OpenStreetMapClient()
        return self._osm


@dataclass
class VideoDownloaderNamespace:
    _ytdlp: Optional[object] = field(default=None, repr=False)

    @property
    def ytdlp(self):
        if self._ytdlp is None:
            from modules.Video_Downloader.YtDlp import VideoDownloader
            self._ytdlp = VideoDownloader()
        return self._ytdlp


@dataclass
class ShortLinkNamespace:
    _bitly:     Optional[object] = field(default=None, repr=False)
    _tinyurl:   Optional[object] = field(default=None, repr=False)
    _rebrandly: Optional[object] = field(default=None, repr=False)

    @property
    def bitly(self):
        if self._bitly is None:
            from modules.Short_Link.Bitly import BitlyShortener
            self._bitly = BitlyShortener()
        return self._bitly

    @property
    def tinyurl(self):
        if self._tinyurl is None:
            from modules.Short_Link.TinyURL import TinyURLShortener
            self._tinyurl = TinyURLShortener()
        return self._tinyurl

    @property
    def rebrandly(self):
        if self._rebrandly is None:
            from modules.Short_Link.Rebrandly import RebrandlyShortener
            self._rebrandly = RebrandlyShortener()
        return self._rebrandly


@dataclass
class QRNamespace:
    _qrcode: Optional[object] = field(default=None, repr=False)
    _segno:  Optional[object] = field(default=None, repr=False)

    @property
    def qrcode(self):
        if self._qrcode is None:
            from modules.QR_Generate.QRCode import QRCodeGenerator
            self._qrcode = QRCodeGenerator()
        return self._qrcode

    @property
    def segno(self):
        if self._segno is None:
            from modules.QR_Generate.Segno import SegnoGenerator
            self._segno = SegnoGenerator()
        return self._segno


class AIToolkit:
    """
    Central access point for all AI Utility Toolkit modules.
    All providers are lazily loaded on first access.

    Example:
        from main import toolkit

        toolkit.llms.openai.chat("Hello")
        toolkit.llms.groq.chat("Hello")
        toolkit.ocr.tesseract.extract_text("image.png")
        toolkit.transcribe.whisper.transcribe("audio.mp3")
        toolkit.translate.deepl.translate("Hello", target_lang="FR")
        toolkit.tts.edge.synthesize("Bonjour", output_path="out.mp3")
        toolkit.qr.segno.generate_wifi("MyNet", "password")
        toolkit.maps.osm.geocode("Connaught Place, New Delhi")
        toolkit.downloader.ytdlp.download_audio("https://youtube.com/...")
    """

    def __init__(self) -> None:
        self.llms       = LLMsNamespace()
        self.ocr        = OCRsNamespace()
        self.image      = AIImageNamespace()
        self.video      = AIVideoNamespace()
        self.tts        = TTSNamespace()
        self.transcribe = TranscribeNamespace()
        self.translate  = TranslateNamespace()
        self.maps       = MapNamespace()
        self.downloader = VideoDownloaderNamespace()
        self.shortlink  = ShortLinkNamespace()
        self.qr         = QRNamespace()
        logger.info("AIToolkit initialized. All modules ready (lazy-loaded).")

    def health_check(self) -> dict:
        """
        Check which API keys are configured. No API calls made.

        Returns:
            Dict mapping key name to True (configured) or False (missing).
        """
        status = get_all_configured_keys()
        configured   = [k for k, v in status.items() if v]
        unconfigured = [k for k, v in status.items() if not v]

        print("=" * 58)
        print("  AI Utility Toolkit — Environment Health Check")
        print("=" * 58)
        for key, ok in status.items():
            icon = "✅" if ok else "❌"
            print(f"  {icon}  {key}")
        print("=" * 58)
        print(f"  {len(configured)} configured  |  {len(unconfigured)} missing")
        print("=" * 58)
        return status


# Singleton instance — import this from anywhere
toolkit = AIToolkit()


if __name__ == "__main__":
    toolkit.health_check()
