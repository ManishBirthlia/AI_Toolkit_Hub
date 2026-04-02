import os
import re
import unicodedata
from pathlib import Path
from typing import Generator

from utils.logger import get_logger

logger = get_logger(__name__)


def read_file_as_bytes(path: str) -> bytes:
    if not path:
        raise ValueError("File path cannot be empty.")
    file = Path(path)
    if not file.exists():
        raise ValueError(f"File not found: {path}")
    try:
        return file.read_bytes()
    except OSError as e:
        logger.error(f"Failed to read file '{path}': {e}")
        raise RuntimeError(f"Could not read file '{path}': {e}") from e


def save_bytes_to_file(data: bytes, path: str) -> str:
    if not data:
        raise ValueError("Cannot write empty data to file.")
    if not path:
        raise ValueError("Output path cannot be empty.")
    file = Path(path)
    try:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)
        logger.info(f"File saved: {file.resolve()}")
        return str(file.resolve())
    except OSError as e:
        logger.error(f"Failed to save file '{path}': {e}")
        raise RuntimeError(f"Could not write file '{path}': {e}") from e


def is_valid_url(url: str) -> bool:
    pattern = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}(?:\.\d{1,3}){3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return bool(pattern.match(url))


def sanitize_filename(name: str, max_length: int = 200) -> str:
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", ascii_name)
    safe = re.sub(r"[\s_]+", "_", safe).strip("_. ")
    safe = safe[:max_length]
    if not safe:
        raise ValueError(f"Filename '{name}' produces an empty result after sanitization.")
    return safe


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> Generator[str, None, None]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size.")
    if not text:
        return

    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        yield text[start:end]
        if end == text_len:
            break
        start += chunk_size - overlap
