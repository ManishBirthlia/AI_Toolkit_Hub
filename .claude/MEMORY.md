# Claude Code Memory Management

This file tracks the history of the project, including every commit and significant milestone. It serves as a persistent memory for AI agents (like Claude Code) to understand the evolution of the codebase.

## 📝 Integration Instructions
To keep this memory updated, run the following command after making significant changes:
```bash
git log --pretty=format:"| %h | %as | %an | %s |" -n 20 >> CLAUDE_MEMORY.md
```

---

## 🚀 Recent Activity

| Hash | Date | Author | Commit Message |
| :--- | :--- | :--- | :--- |
| `---` | 2026-04-08 | Manish Birthlia | feat: add DeepSeekAI and NemotronAI LLM modules with test scripts |
| `---` | 2026-04-07 | Manish Birthlia | fix: resolve torchaudio CUDA mismatch, add GPU speed optimisation for Bark |
| `---` | 2026-04-07 | Manish Birthlia | feat: add Bark TTS test script with async synthesis |
| `---` | 2026-04-07 | Manish Birthlia | fix: downgrade requires-python to >=3.13, pin PyTorch cu124 via uv index |
| `a4bd31a` | 2026-04-06 | Manish Birthlia | Web Search module Created and Updated |
| `9217544` | 2026-04-02 | Manish Birthlia | docs: remove unnecessary whitespace in README.md code block |
| `e20003f` | 2026-04-02 | Manish Birthlia | test: implement initial unit test suite for core AI modules |
| `785288d` | 2026-04-02 | Manish Birthlia | feat: add pipeline scripts for toolkit workflows |
| `8362dc0` | 2026-04-02 | Manish Birthlia | feat: added utility modules for file operations, logging |
| `3c00a38` | 2026-04-02 | Manish Birthlia | feat: implement utility modules for Centralized API keys |
| `bfb6344` | 2026-04-02 | Manish Birthlia | feat: implement URL shortening modules |
| `305d2cb` | 2026-04-02 | Manish Birthlia | feat: implement TTS module with Edge, ElevenLabs, etc. |
| `675c973` | 2026-04-02 | Manish Birthlia | feat: implement VideoDownloader using yt-dlp |
| `369929e` | 2026-04-02 | Manish Birthlia | feat: implement modular translation and transcription |
| `66cbed6` | 2026-04-02 | Manish Birthlia | feat: implement QR code generation modules |
| `b8b478d` | 2026-04-02 | Manish Birthlia | feat: implement OCR module for Tesseract, EasyOCR |
| `bcf5ec2` | 2026-04-02 | Manish Birthlia | feat: implement Google Maps and OSM provider modules |
| `9a57d43` | 2026-04-02 | Manish Birthlia | feat: implement image generation for FLUX, SD, DALL-E |
| `aac0555` | 2026-04-02 | Manish Birthlia | feat: initialize project with uv configuration |
| `e7ee2f5` | 2026-04-02 | Manish Birthlia | docs: add project contribution guidelines |
| `6d83f75` | 2026-04-02 | Manish Birthlia | feat: initialize project structure with docs and tests |
| `af0f06f` | 2026-04-02 | Manish Birthlia | feat: initial modular AI architecture and core infra |

---

## 🔧 Architecture Decisions & Gotchas

- **Python version**: Pinned to `>=3.13` in `pyproject.toml` (was 3.14, but PyTorch/torchaudio don't have 3.14 wheels yet).
- **PyTorch CUDA**: All three packages (`torch`, `torchaudio`, `torchvision`) **must** come from the same CUDA index (`cu124`). Mixing PyPI CPU wheels with CUDA wheels causes `WinError 127` DLL crashes.
- **Bark speed**: Set `SUNO_OFFLOAD_CPU=False` and `SUNO_USE_SMALL_MODELS=True` env vars **before** importing `bark` to keep models in VRAM. This drops generation from ~85s to ~10-15s on a GTX 1660 Ti (6GB).
- **GPU**: User's machine has an **NVIDIA GTX 1660 Ti** (6GB VRAM). CUDA 12.4 confirmed working.
- **uv sources**: PyTorch CUDA packages are configured via `[[tool.uv.index]]` pointing to `https://download.pytorch.org/whl/cu124`.

---

## 📡 Push History (GitHub Sync)
- **Repo URL**: `https://github.com/ManishBirthlia/AI_Toolkit_Hub.git`
- **Main Branch**: `master`
- **Last Sync Check**: 2026-04-08
  - Local commits from `a4bd31a` onward are pending push to `origin/master`.
  - Uncommitted work: DeepSeekAI, NemotronAI modules + test scripts, Bark speed fix, pyproject.toml CUDA config.

---

## 📌 Project Milestones
- **2026-04-02**: Initialized project with modular architecture for LLMs, Image Gen, and Utilities.
- **2026-04-02**: Added comprehensive test suite and documentation.
- **2026-04-03**: Implemented Claude Code Memory Management Structure (CLAUDE_MEMORY.md).
- **2026-04-06**: Created `modules/Internet/WebSearch.py` — modular web search with LLM summarization.
- **2026-04-06**: Created `modules/LLMs/chat.py` — unified chat interface.
- **2026-04-07**: Created `modules/TTS/Bark.py` — Suno Bark TTS with chunking, GPU acceleration.
- **2026-04-07**: Fixed PyTorch CUDA environment — pinned Python 3.13, configured `cu124` index for torch/torchaudio/torchvision.
- **2026-04-07**: Optimised Bark TTS speed with `SUNO_OFFLOAD_CPU=False` (85s → ~10s).
- **2026-04-08**: Created `modules/LLMs/DeepSeekAI.py` — NVIDIA DeepSeek v3.2 with reasoning/thinking support.
- **2026-04-08**: Created `modules/LLMs/NemotronAI.py` — NVIDIA Nemotron nano-30b with reasoning/thinking support.
- **2026-04-08**: Added test scripts for DeepSeek and Nemotron (`tests/LLMs/`).
- **2026-04-08**: Updated `utils/config.py` with `NVIDIA_NEMOTRON_API_KEY`, `NVIDIA_DEEPSEEK_API_KEY`, `HF_TOKEN`.

