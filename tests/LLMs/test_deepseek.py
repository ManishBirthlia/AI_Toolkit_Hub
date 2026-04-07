import os
import sys
import time

# Add the project root to the Python path so it can find "modules" and "utils"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.LLMs.DeepSeekAI import DeepSeekChat

import logging
logging.basicConfig(level=logging.INFO)


def test_deepseek_chat():
    """Test DeepSeek chat completion (non-streaming)."""
    print("=" * 60)
    print("  DeepSeek Chat Test (Non-Streaming)")
    print("=" * 60)

    llm = DeepSeekChat()

    prompt = "Explain what a neural network is in 2-3 sentences."
    system = "You are a concise AI tutor. Keep answers short and clear."

    print(f"\nSystem : {system}")
    print(f"Prompt : {prompt}\n")

    start = time.time()
    try:
        reply = llm.chat(prompt=prompt, system=system, temperature=1, max_tokens=512)
        elapsed = time.time() - start
        print(f"Response ({elapsed:.2f}s):\n{reply}\n")
    except Exception as e:
        print(f"Error: {e}\n")


def test_deepseek_stream():
    """Test DeepSeek streaming completion."""
    print("=" * 60)
    print("  DeepSeek Stream Test")
    print("=" * 60)

    llm = DeepSeekChat()

    prompt = "Write a haiku about coding."

    print(f"\nPrompt : {prompt}")
    print(f"Streamed response:\n")

    start = time.time()
    try:
        full_response = ""
        for token in llm.stream(prompt=prompt, temperature=0.7, max_tokens=256):
            print(token, end="", flush=True)
            full_response += token
        elapsed = time.time() - start
        print(f"\n\n[Streamed {len(full_response)} chars in {elapsed:.2f}s]\n")
    except Exception as e:
        print(f"\nError: {e}\n")


if __name__ == "__main__":
    test_deepseek_chat()
    # test_deepseek_stream()
