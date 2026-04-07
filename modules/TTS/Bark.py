from typing import Optional
import io
import os
import asyncio
import functools
import re

# Dramatically speeds up generation on GPUs with >= 6GB VRAM by keeping models in VRAM
# instead of transferring them over PCIe on every step.
os.environ["SUNO_OFFLOAD_CPU"] = "False"
os.environ["SUNO_USE_SMALL_MODELS"] = "True"

try:
    import torch
    import numpy as np
    from bark import SAMPLE_RATE, generate_audio as bark_generate_audio, preload_models
    import scipy.io.wavfile
except ImportError as e:
    raise ImportError("pip install bark torch scipy numpy") from e

from utils.helpers import save_bytes_to_file
from utils.logger import get_logger

logger = get_logger(__name__)

# Keep track of models to avoid reloading unnecessarily
_models_loaded = False
_device = "cuda" if torch.cuda.is_available() else "cpu"

class BarkTTS:
    """Suno Bark Text-to-Speech provider. Supports multi-lingual and non-speech sounds."""

    DEFAULT_SPEAKER = "v2/en_speaker_6"

    def __init__(self, speaker: str = DEFAULT_SPEAKER) -> None:
        self.speaker = speaker
        logger.info(f"BarkTTS initialized | speaker='{self.speaker}' | device='{_device}'")

    @classmethod
    def _ensure_models_loaded(cls):
        global _models_loaded, _device
        
        if not _models_loaded:
            logger.info(f"Loading Bark models on: {_device.upper()} (this may take a while...)")
            
            # Monkey-patch torch.load to handle legacy Bark models in PyTorch 2.6+
            _orig_torch_load = torch.load
            def _patched_torch_load(*args, **kwargs):
                if 'weights_only' not in kwargs:
                    kwargs['weights_only'] = False
                return _orig_torch_load(*args, **kwargs)
            torch.load = _patched_torch_load

            preload_models(
                text_use_gpu=(_device == "cuda"),
                text_use_small=True,
                coarse_use_gpu=(_device == "cuda"),
                coarse_use_small=True,
                fine_use_gpu=(_device == "cuda"),
                fine_use_small=True,
                codec_use_gpu=(_device == "cuda")
            )
            _models_loaded = True
            logger.info("Bark models loaded successfully.")

    def synthesize(self, text: str, output_path: Optional[str] = None) -> bytes:
        """Convert text to speech using Suno Bark, applying chunking for long prompts.

        Args:
            text: Text to synthesize.
            output_path: If provided, saves audio to this path.

        Returns:
            Raw audio bytes (WAV format).
            
        Raises:
            ValueError: If text is empty.
            RuntimeError: If synthesis fails.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        self._ensure_models_loaded()
        
        try:
            # Clean and split text into sentences
            text = text.replace("\n", " ").strip()
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
            
            # Group sentences into chunks of reasonable length (e.g. max 150 chars roughly)
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) < 150:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
            if current_chunk:
                chunks.append(current_chunk.strip())
                
            if not chunks:
                chunks = [text]

            pieces = []
            for i, chunk in enumerate(chunks):
                logger.debug(f"Generating Bark audio for chunk {i+1}/{len(chunks)}: '{chunk}'")
                audio_array = bark_generate_audio(chunk, history_prompt=self.speaker, silent=True)
                pieces.append(audio_array)

            # Combine all pieces array into one
            final_audio_array = np.concatenate(pieces)
            
            # Convert numpy array to WAV bytes
            bytes_io = io.BytesIO()
            scipy.io.wavfile.write(bytes_io, SAMPLE_RATE, final_audio_array)
            audio_bytes = bytes_io.getvalue()
            
            if output_path:
                save_bytes_to_file(audio_bytes, output_path)
                
            return audio_bytes
            
        except Exception as e:
            raise RuntimeError(f"Bark TTS synthesis failed: {e}") from e

    async def synthesize_async(self, text: str, output_path: Optional[str] = None) -> bytes:
        """Asynchronously convert text to speech using Suno Bark."""
        logger.debug("Starting async Bark TTS synthesis...")
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            functools.partial(self.synthesize, text=text, output_path=output_path)
        )
