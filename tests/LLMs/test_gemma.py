import sys
import os

# Add root folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.LLMs.NvidiaGemmaAI import NvidiaGemmaAI
from utils.logger import get_logger

logger = get_logger(__name__)


def test_gemma_chat():
    """Test Nvidia Hosted Gemma capabilities synchronously."""
    print("\n--- Testing NvidiaGemmaAI (Sync) ---")
    
    try:
        gemma = NvidiaGemmaAI()
        prompt = "Explain quantum computing in one short sentence."
        print(f"User: {prompt}")
        
        response = gemma.chat(prompt=prompt, max_tokens=100)
        print(f"Gemma: {response}")
        
    except Exception as e:
        print(f"❌ Error testing Gemma sync: {e}")


def test_gemma_stream():
    """Test Nvidia Hosted Gemma capabilities with streaming."""
    print("\n--- Testing NvidiaGemmaAI (Streaming) ---")
    
    try:
        gemma = NvidiaGemmaAI()
        prompt = "Write a haiku about a robot learning to feel."
        print(f"User: {prompt}\nGemma: ", end="")
        
        for token in gemma.stream(prompt=prompt, max_tokens=100):
            print(token, end="", flush=True)
        print()
        
    except Exception as e:
        print(f"\n❌ Error testing Gemma stream: {e}")


if __name__ == "__main__":
    test_gemma_chat()
    test_gemma_stream()
