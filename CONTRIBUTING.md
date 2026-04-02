# Contributing to AI Utility Toolkit

Thank you for your interest in contributing. This document covers everything you need to know — from setting up your environment to getting your pull request merged.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [What You Can Contribute](#what-you-can-contribute)
- [Project Architecture — Read First](#project-architecture--read-first)
- [Development Setup](#development-setup)
- [Adding a New Provider to an Existing Module](#adding-a-new-provider-to-an-existing-module)
- [Adding a Brand New Module](#adding-a-brand-new-module)
- [Code Standards](#code-standards)
- [Writing Tests](#writing-tests)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

---

## Code of Conduct

This project follows a simple standard: be professional, be constructive, and be respectful. Contributions of all experience levels are welcome. Dismissive or hostile communication will not be tolerated.

---

## What You Can Contribute

| Type | Examples |
|---|---|
| **New provider** | Add `Anthropic.py` under `modules/LLMs/` |
| **New module** | Add a complete `modules/Sentiment/` directory |
| **Bug fix** | Fix broken API handling, incorrect output formatting |
| **Tests** | Add missing unit or integration tests |
| **Documentation** | Improve docstrings, examples, or this file |
| **Performance** | Optimize response parsing, reduce latency |
| **Refactoring** | Improve structure without changing behavior |

If you're unsure whether your idea fits, open a [Discussion](../../discussions) before writing code.

---

## Project Architecture — Read First

Before contributing, understand the module structure. Every capability is a **directory**, not a single file. Each provider within that capability is a **separate `.py` file**.

```
modules/
├── LLMs/
│   ├── __init__.py       ← Exports a unified interface
│   ├── OpenAI.py         ← Provider-specific logic
│   ├── ClaudeAI.py
│   └── GroqAI.py
```

**The `__init__.py` pattern is critical.** It exposes a consistent interface so that callers never import provider files directly — they always go through the module's `__init__.py`. This is what makes the toolkit swappable and provider-agnostic.

```python
# modules/LLMs/__init__.py
from .OpenAI import OpenAIChat
from .ClaudeAI import ClaudeChat
from .GroqAI import GroqChat

__all__ = ["OpenAIChat", "ClaudeChat", "GroqChat"]
```

---

## Development Setup

### 1. Fork and clone

```bash
git clone https://github.com/your-username/ai-utility-toolkit.git
cd ai-utility-toolkit
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt   # Linting, testing tools
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Fill in only the API keys relevant to what you're working on
```

### 5. Verify setup

```bash
python -m pytest tests/ -v
```

All existing tests should pass before you begin.

---

## Adding a New Provider to an Existing Module

**Example:** Adding `MistralAI.py` to the `LLMs` module.

### Step 1 — Create the provider file

```
modules/LLMs/MistralAI.py
```

Follow the structure of an existing provider file in the same module:

```python
# modules/LLMs/MistralAI.py

from mistralai.client import MistralClient
from utils.config import get_api_key
from utils.logger import get_logger

logger = get_logger(__name__)


class MistralChat:
    """
    Mistral AI provider for LLM chat completions.

    Supported models: mistral-large-latest, mistral-small-latest, open-mixtral-8x7b
    Docs: https://docs.mistral.ai/
    """

    def __init__(self, model: str = "mistral-large-latest"):
        self.model = model
        self.client = MistralClient(api_key=get_api_key("MISTRAL_API_KEY"))

    def chat(self, prompt: str, system: str = None) -> str:
        """
        Send a chat message and return the response as a string.

        Args:
            prompt: The user message.
            system: Optional system prompt.

        Returns:
            The model's response text.

        Raises:
            ValueError: If the prompt is empty.
            RuntimeError: If the API call fails.
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty.")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat(model=self.model, messages=messages)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"MistralAI chat failed: {e}")
            raise RuntimeError(f"MistralAI API error: {e}") from e
```

### Step 2 — Register in `__init__.py`

```python
# modules/LLMs/__init__.py
from .MistralAI import MistralChat   # Add this line
```

### Step 3 — Add the API key to `.env.example`

```env
# Mistral AI
MISTRAL_API_KEY=
```

### Step 4 — Write a test

```
tests/LLMs/test_mistral.py
```

See [Writing Tests](#writing-tests) below.

### Step 5 — Update `requirements.txt`

Add the new dependency with a minimum version pinned:

```
mistralai>=1.0.0
```

---

## Adding a Brand New Module

**Example:** Adding a `Sentiment/` module.

### Step 1 — Create the module directory

```
modules/Sentiment/
├── __init__.py
├── HuggingFace.py       # Provider 1
└── OpenAISentiment.py   # Provider 2
```

### Step 2 — Implement provider files

Follow the same class-based pattern shown above. Every provider class must:

- Accept configuration in `__init__` (model, API key via `get_api_key`)
- Expose at minimum one clearly named public method
- Include full docstrings (Args, Returns, Raises)
- Use `utils.logger` for all logging — no bare `print()` statements
- Raise meaningful exceptions with context, never swallow errors silently

### Step 3 — Create `__init__.py`

Export all provider classes cleanly:

```python
# modules/Sentiment/__init__.py
from .HuggingFace import HuggingFaceSentiment
from .OpenAISentiment import OpenAISentiment

__all__ = ["HuggingFaceSentiment", "OpenAISentiment"]
```

### Step 4 — Register in `main.py`

```python
# main.py
from modules.Sentiment import HuggingFaceSentiment, OpenAISentiment
```

### Step 5 — Add tests

```
tests/Sentiment/
├── __init__.py
└── test_huggingface_sentiment.py
```

### Step 6 — Add an example

```python
# examples/sentiment_demo.py
from modules.Sentiment import HuggingFaceSentiment

analyzer = HuggingFaceSentiment()
result = analyzer.analyze("This product exceeded all my expectations.")
print(result)  # {'label': 'POSITIVE', 'score': 0.9987}
```

### Step 7 — Update the README

Add your new module to the Modules table in `README.md`.

---

## Code Standards

### Formatting

This project uses **Black** for formatting and **isort** for import ordering.

```bash
black modules/ tests/
isort modules/ tests/
```

### Linting

```bash
flake8 modules/ tests/ --max-line-length=100
```

### Type hints

All public methods must include type hints:

```python
# ✅ Correct
def translate(self, text: str, target_lang: str = "en") -> str:

# ❌ Wrong
def translate(self, text, target_lang="en"):
```

### Naming conventions

| Item | Convention | Example |
|---|---|---|
| Module directories | `PascalCase` | `AI_Image/` |
| Provider files | `PascalCase` | `StableDiffusion.py` |
| Classes | `PascalCase` | `StableDiffusionClient` |
| Methods / functions | `snake_case` | `generate_image()` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_MODEL` |
| Private methods | `_snake_case` | `_parse_response()` |

### No hardcoded credentials

Never commit API keys, tokens, or secrets. Always use `utils/config.py`:

```python
from utils.config import get_api_key

api_key = get_api_key("OPENAI_API_KEY")   # ✅
api_key = "sk-abc123..."                   # ❌ Never do this
```

---

## Writing Tests

Tests mirror the `modules/` directory structure under `tests/`.

```
tests/
├── LLMs/
│   └── test_mistral.py
├── Sentiment/
│   └── test_huggingface_sentiment.py
```

### Test template

```python
# tests/LLMs/test_mistral.py

import pytest
from unittest.mock import patch, MagicMock
from modules.LLMs.MistralAI import MistralChat


class TestMistralChat:

    def setup_method(self):
        with patch("modules.LLMs.MistralAI.MistralClient"):
            self.client = MistralChat(model="mistral-large-latest")

    def test_chat_returns_string(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Hello from Mistral!"
        self.client.client.chat.return_value = mock_response

        result = self.client.chat("Say hello.")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_chat_raises_on_empty_prompt(self):
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            self.client.chat("")

    def test_chat_raises_on_api_failure(self):
        self.client.client.chat.side_effect = Exception("API timeout")
        with pytest.raises(RuntimeError, match="MistralAI API error"):
            self.client.chat("Hello")
```

### Rules

- All tests must use mocks — never make real API calls in tests
- Test the happy path, empty inputs, and API failure scenarios at minimum
- Use `pytest` fixtures for shared setup
- Run the full suite before submitting: `python -m pytest tests/ -v`

---

## Commit Message Convention

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard.

```
<type>(<scope>): <short description>
```

| Type | When to use |
|---|---|
| `feat` | New provider, module, or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `refactor` | Code restructuring, no behavior change |
| `chore` | Dependency updates, config changes |
| `perf` | Performance improvement |

**Examples:**

```
feat(LLMs): add MistralAI provider
fix(Transcribe): handle empty audio file gracefully
docs(CONTRIBUTING): clarify module naming conventions
test(OCRs): add unit tests for EasyOCR provider
refactor(TTS): extract shared audio utilities to helpers.py
```

Keep the subject line under 72 characters. Use the commit body to explain *why*, not *what*.

---

## Pull Request Process

1. **Branch from `main`** using a descriptive branch name:
   ```bash
   git checkout -b feat/llms-mistral-provider
   git checkout -b fix/transcribe-empty-audio
   ```

2. **Keep PRs focused.** One feature or fix per PR. Large PRs are harder to review and slower to merge.

3. **Fill out the PR template completely.** Include:
   - What the change does
   - Which module(s) are affected
   - How to test it manually
   - Any new environment variables required

4. **Ensure all checks pass:**
   - `black --check modules/ tests/`
   - `flake8 modules/ tests/`
   - `python -m pytest tests/ -v`

5. **Request a review.** PRs require at least one approval before merging.

6. **Respond to feedback promptly.** PRs inactive for more than 14 days may be closed.

---

## Reporting Bugs

Open an issue using the **Bug Report** template. Include:

- **Module and provider affected** (e.g., `Transcribe/Whisper.py`)
- **Python version** and OS
- **Minimal reproducible example** — the shortest code that triggers the bug
- **Expected vs. actual behavior**
- **Full traceback** if applicable

Do not include real API keys in bug reports.

---

## Requesting Features

Open an issue using the **Feature Request** template. Include:

- **What capability you want** (new provider, new module, new method)
- **Why it's valuable** — what use case does it unlock?
- **Which existing providers/APIs** could implement it
- **Whether you're willing to implement it yourself**

Feature requests with a clear rationale and a willing contributor are prioritized.

---

<div align="center">
  <sub>Every great toolbox is built one tool at a time. Thanks for contributing.</sub>
</div>
