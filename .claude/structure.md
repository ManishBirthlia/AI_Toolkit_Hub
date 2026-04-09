# Project Structure Map

This file provides a clear tree-view mapping of all important logic and configuration paths from the root directory so the AI agent does not need to search for them.

**Absolute Root Path:** `d:\My Business\My Projects\On-Going\AI_Toolkit_Hub\`

```text
📁 .claude/                 (Agentic Operating System)
   ├── .mcp.json            (Model Context Protocol configurations)
   ├── CLAUDE.md            (Rules, Tone, Skills)
   ├── MEMORY.md            (Architecture notes, history, and backlog)
   ├── settings.json        (Tool permissions and settings)
   ├── settings.local.json
   ├── structure.md         (This file)
   └── reference/           (Architecture specs and deep dive references)

📁 modules/                 (Core Application Logic)
   ├── __init__.py
   ├── AI_Image/
   │   ├── __init__.py
   │   ├── DALLE.py
   │   ├── FLUX.py
   │   └── StableDiffusion.py
   ├── AI_Video/
   │   ├── __init__.py
   │   ├── KlingAI.py
   │   ├── RunwayML.py
   │   └── VideoAnalysis.py
   ├── Internet/
   │   ├── GoogleTrends.py
   │   └── WebSearch.py
   ├── LLMs/
   │   ├── __init__.py
   │   ├── ClaudeAI.py
   │   ├── DeepSeekAI.py
   │   ├── GeminiAI.py
   │   ├── GroqAI.py
   │   ├── NemotronAI.py
   │   ├── OllamaAI.py
   │   ├── OpenAI.py
   │   └── chat.py
   ├── Map/
   │   ├── __init__.py
   │   ├── GoogleMaps.py
   │   └── OpenStreetMap.py
   ├── OCRs/
   │   ├── __init__.py
   │   ├── EasyOCR.py
   │   ├── GoogleVision.py
   │   └── Tesseract.py
   ├── QR_Generate/
   │   ├── __init__.py
   │   ├── QRCode.py
   │   └── Segno.py
   ├── Short_Link/
   │   ├── __init__.py
   │   ├── Bitly.py
   │   ├── Rebrandly.py
   │   └── TinyURL.py
   ├── TTS/
   │   ├── __init__.py
   │   ├── Bark.py
   │   ├── EdgeTTS.py
   │   ├── ElevenLabs.py
   │   └── GoogleTTS.py
   ├── Transcribe/
   │   ├── __init__.py
   │   ├── AssemblyAI.py
   │   ├── Deepgram.py
   │   └── Whisper.py
   ├── Translate/
   │   ├── __init__.py
   │   ├── DeepL.py
   │   ├── GoogleTranslate.py
   │   └── LLMTranslate.py
   └── Video_Downloader/
       ├── __init__.py
       └── YtDlp.py

📁 System Modules/           (Jarvis AI Agent — System-Level Tools)
   ├── __init__.py           (Package init + get_all_tool_schemas())
   ├── system.py             (open_application, run_command, get_system_info, kill_process)
   ├── browser.py            (search_web, open_url, get_page_content)
   ├── files.py              (read_file, write_file, move_file, delete_file, list_directory)
   ├── keyboard.py           (type_text, press_hotkey, click, scroll, take_screenshot)
   ├── vision.py             (capture_screen, find_text_on_screen, get_active_window_title, describe_screen_with_ai)
   ├── email_tool.py         (send_email, read_latest_emails)
   ├── clipboard.py          (copy_to_clipboard, paste_from_clipboard)
   ├── audio.py              (speak, listen_for_command, transcribe_audio)
   ├── memory.py             (save_memory, get_memory, list_all_memories, clear_memory)
   └── requirements.txt      (Third-party dependencies for this package)

📁 utils/                   (Helper Methods & Utilities)
   ├── __init__.py
   ├── config.py
   ├── helpers.py
   └── logger.py

📁 examples/                (Usage Demonstrations)
   ├── __init__.py
   └── pipeline_demo.py

📁 tests/                   (Test Cases)
   ├── __init__.py
   ├── AI_Image/
   ├── AI_Video/
   ├── Internet/
   │   └── test_google_trends.py
   ├── LLMs/
   │   ├── test_deepseek.py
   │   └── test_nemotron.py
   ├── Map/
   ├── OCRs/
   ├── QR_Generate/
   ├── Short_Link/
   ├── TTS/
   │   └── test_bark.py
   ├── Transcribe/
   ├── Translate/
   └── Video_Downloader/

📄 Root Project Files
   ├── .env.example
   ├── .gitignore
   ├── .python-version
   ├── CONTRIBUTING.md
   ├── Feature.md
   ├── README.md
   ├── main.py
   ├── pyproject.toml
   ├── pytest.ini
   ├── requirements-dev.txt
   ├── requirements.txt
   └── uv.lock
```
