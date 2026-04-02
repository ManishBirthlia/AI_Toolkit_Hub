<div align="center">

# ⚙️ AI Utility Toolkit

### A modular, extensible Python framework for integrating AI capabilities into any application.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Modules](https://img.shields.io/badge/Modules-12%2B-f59e0b?style=flat-square)](#-modules)
[![Status](https://img.shields.io/badge/Status-Active%20Development-6366f1?style=flat-square)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-ec4899?style=flat-square)](CONTRIBUTING.md)

</div>

---

## Overview

**AI Utility Toolkit** is a production-oriented, modular Python framework that consolidates a growing suite of AI-powered capabilities into a single, unified toolbox. Each feature is isolated in its own module — independently testable, swappable, and deployable — while a central `main.py` orchestrator ties everything together for seamless cross-feature workflows.

Designed from the ground up with scalability in mind, this project is equally suitable as a **personal automation engine**, a **backend for SaaS products**, or the **foundation of a full REST API platform**.

---

## Why This Project?

| Problem | Solution |
|---|---|
| AI integrations are scattered, inconsistent, and hard to maintain | Every capability is a clean, self-contained module |
| Switching providers (e.g., OpenAI → Groq) breaks entire codebases | Provider logic is encapsulated; swap with one change |
| Combining AI features (e.g., transcribe → translate → TTS) is fragile | The orchestrator enables composable, chained pipelines |
| Prototypes don't scale into products | Architecture supports REST API and SaaS deployment from day one |

---

## Modules

Each capability lives in its own **subdirectory** under `modules/`, with one file per provider or backend. All modules are imported and accessible through `main.py`.

| Module | Directory | Providers / Files |
|---|---|---|
| 🤖 **AI Chat / LLMs** | `modules/LLMs/` | OpenAI, Claude, Groq, Gemini, Ollama |
| 👁️ **OCR** | `modules/OCRs/` | Tesseract, EasyOCR, Google Vision |
| 🎨 **AI Image Generation** | `modules/AI_Image/` | Stable Diffusion, DALL·E, FLUX |
| 🎬 **AI Video Processing** | `modules/AI_Video/` | RunwayML, Kling, Video Analysis |
| 🔊 **Text-to-Speech** | `modules/TTS/` | ElevenLabs, Google TTS, Edge TTS |
| 🎙️ **Speech-to-Text** | `modules/Transcribe/` | Whisper, AssemblyAI, Deepgram |
| 🌐 **Translation** | `modules/Translate/` | DeepL, Google Translate, LLM-based |
| 🗺️ **Maps / Location** | `modules/Map/` | Google Maps, OpenStreetMap |
| 📥 **Video Downloader** | `modules/Video_Downloader/` | yt-dlp (YouTube, 1000+ platforms) |
| 🔗 **URL Shortener** | `modules/Short_Link/` | Bitly, TinyURL, Rebrandly |
| 📱 **QR Code Generator** | `modules/QR_Generate/` | qrcode, segno (custom styling) |

> **More modules are actively being developed.** See [Roadmap](#-roadmap) for what's coming next.

---

## Project Structure

```
ai-utility-toolkit/
│
├── main.py                        # Central orchestrator and entry point
│
├── modules/
│   │
│   ├── LLMs/                      # AI Chat & Language Models
│   │   ├── __init__.py
│   │   ├── OpenAI.py              # GPT-4o, GPT-4-turbo
│   │   ├── ClaudeAI.py            # Claude 3.5 Sonnet / Opus
│   │   ├── GroqAI.py              # LLaMA 3, Mixtral via Groq
│   │   ├── GeminiAI.py            # Gemini 1.5 Pro / Flash
│   │   └── OllamaAI.py            # Local models via Ollama
│   │
│   ├── OCRs/                      # Optical Character Recognition
│   │   ├── __init__.py
│   │   ├── Tesseract.py           # Offline OCR via pytesseract
│   │   ├── EasyOCR.py             # Deep learning-based OCR
│   │   └── GoogleVision.py        # Google Cloud Vision API
│   │
│   ├── AI_Image/                  # AI Image Generation
│   │   ├── __init__.py
│   │   ├── StableDiffusion.py     # Local / Automatic1111 / ComfyUI
│   │   ├── DALLE.py               # OpenAI DALL·E 3
│   │   └── FLUX.py                # FLUX.1 via Replicate / fal.ai
│   │
│   ├── AI_Video/                  # AI Video Processing
│   │   ├── __init__.py
│   │   ├── RunwayML.py            # Gen-3 video generation
│   │   ├── KlingAI.py             # Kling video synthesis
│   │   └── VideoAnalysis.py       # Frame extraction, captioning
│   │
│   ├── TTS/                       # Text-to-Speech
│   │   ├── __init__.py
│   │   ├── ElevenLabs.py          # Ultra-realistic voice cloning
│   │   ├── GoogleTTS.py           # Google Cloud Text-to-Speech
│   │   └── EdgeTTS.py             # Microsoft Edge TTS (free)
│   │
│   ├── Transcribe/                # Speech-to-Text / Transcription
│   │   ├── __init__.py
│   │   ├── Whisper.py             # OpenAI Whisper (local + API)
│   │   ├── AssemblyAI.py          # AssemblyAI with speaker diarization
│   │   └── Deepgram.py            # Deepgram Nova-2
│   │
│   ├── Translate/                 # Translation
│   │   ├── __init__.py
│   │   ├── DeepL.py               # DeepL API (high accuracy)
│   │   ├── GoogleTranslate.py     # Google Translate API
│   │   └── LLMTranslate.py        # LLM-powered contextual translation
│   │
│   ├── Map/                       # Maps & Location APIs
│   │   ├── __init__.py
│   │   ├── GoogleMaps.py          # Geocoding, Places, Directions
│   │   └── OpenStreetMap.py       # OSM via Nominatim (free)
│   │
│   ├── Video_Downloader/          # Video Downloading
│   │   ├── __init__.py
│   │   └── YtDlp.py               # yt-dlp (YouTube + 1000+ sites)
│   │
│   ├── Short_Link/                # URL Shortening
│   │   ├── __init__.py
│   │   ├── Bitly.py               # Bitly API
│   │   ├── TinyURL.py             # TinyURL API
│   │   └── Rebrandly.py           # Branded links via Rebrandly
│   │
│   └── QR_Generate/               # QR Code Generation
│       ├── __init__.py
│       ├── QRCode.py              # qrcode library (standard)
│       └── Segno.py               # segno (advanced styling & formats)
│
├── utils/
│   ├── config.py                  # Centralized API key and config management
│   ├── logger.py                  # Unified logging across modules
│   └── helpers.py                 # Shared utility functions
│
├── tests/
│   ├── LLMs/
│   │   ├── test_openai.py
│   │   ├── test_claude.py
│   │   └── test_groq.py
│   ├── OCRs/
│   │   └── test_tesseract.py
│   └── ...                        # Mirrors modules/ structure
│
├── examples/
│   └── pipeline_demo.py           # Example of chaining multiple modules
│
├── .env.example                   # Environment variable template
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` or `uv` for package management
- API keys for desired providers (see `.env.example`)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-utility-toolkit.git
cd ai-utility-toolkit

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Environment Variables

```env
# LLMs
OPENAI_API_KEY=
GROQ_API_KEY=
GEMINI_API_KEY=

# Image Generation
STABILITY_API_KEY=

# Translation
DEEPL_API_KEY=

# Maps
GOOGLE_MAPS_API_KEY=

# TTS
ELEVENLABS_API_KEY=

# URL Shortener
BITLY_API_KEY=
```

---

## Usage

### Single Module

```python
# Use any module independently
from modules.LLMs import chat
from modules.Transcribe import transcribe_audio
from modules.Translate import translate_text

# Chat with an LLM
response = chat("Summarize the theory of relativity in 3 bullet points.")
print(response)

# Transcribe an audio file
transcript = transcribe_audio("meeting_recording.mp3")
print(transcript)

# Translate text
translated = translate_text("Hello, world!", target_lang="hi")  # Hindi
print(translated)
```

### Chained Pipeline (Orchestration)

```python
from modules.Transcribe import transcribe_audio
from modules.Translate import translate_text
from modules.TTS import synthesize_speech

# Pipeline: Audio → Transcript → Translation → Speech
audio_file = "spanish_lecture.mp3"

transcript = transcribe_audio(audio_file)               # Step 1: Transcribe
translated = translate_text(transcript, target_lang="en")  # Step 2: Translate
synthesize_speech(translated, output="english_audio.mp3")  # Step 3: Re-voice
```

### Via main.py

```python
# main.py exposes a unified interface to all modules
from main import toolkit

# Access any module through the toolkit object
result = toolkit.ocr.extract_text("invoice.png")
qr = toolkit.qr.generate("https://your-site.com", style="rounded")
short = toolkit.url.shorten("https://very-long-url.com/path?params=values")
```

---

## Design Principles

### 1. Modularity First
Every feature is a standalone module. Adding, removing, or updating a capability has zero impact on unrelated modules. New features are added by creating a new `.py` file — nothing else needs to change.

### 2. Provider Agnosticism
No module is hard-coupled to a single API provider. Each module supports multiple backends, selectable via config or at call time. This prevents vendor lock-in and enables cost/performance optimization.

### 3. Composability
Modules are designed to be piped together. The output of one module (e.g., a transcript) is a clean string or structured object that flows naturally into the next (e.g., translation). The orchestrator in `main.py` enables building complex, multi-step AI pipelines from simple building blocks.

### 4. Production Readiness
- Centralized configuration and secret management via `.env`
- Unified logging across all modules
- Per-module unit tests
- Clear separation of concerns (modules, utils, tests, examples)

---

## Roadmap

- [ ] **REST API Layer** — FastAPI wrapper to expose all modules as HTTP endpoints
- [ ] **Web Dashboard** — Admin UI for managing API keys, monitoring usage, and testing modules
- [ ] **Document Intelligence** (`Docs.py`) — PDF parsing, summarization, Q&A over documents
- [ ] **AI Web Search** (`WebSearch.py`) — Agentic web search with summarization
- [ ] **Face Recognition** (`FaceRecog.py`) — Face detection, identification, and verification
- [ ] **Sentiment Analysis** (`Sentiment.py`) — Analyze tone and sentiment in text or audio
- [ ] **Code Execution Sandbox** (`CodeRunner.py`) — Safe, isolated code execution
- [ ] **Docker Support** — Containerized deployment for each module
- [ ] **Authentication & Rate Limiting** — For SaaS/API platform deployment
- [ ] **Usage Analytics** — Per-module call tracking and cost estimation

---

## Contributing

Contributions are welcome. To add a new module:

1. Fork the repository
2. Create a new file: `modules/YourFeature.py`
3. Follow the existing module interface conventions
4. Add unit tests in `tests/test_yourfeature.py`
5. Update `main.py` to register the new module
6. Submit a pull request with a clear description

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Author

**Manish** — Full Stack Developer & AI Engineer

Focused on building practical, production-grade AI tools and developer utilities.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/your-profile)
[![YouTube](https://img.shields.io/badge/YouTube-Subscribe-FF0000?style=flat-square&logo=youtube)](https://youtube.com/@your-channel)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat-square&logo=github)](https://github.com/your-username)

---

<div align="center">
  <sub>Built with precision. Designed to scale.</sub>
</div>
