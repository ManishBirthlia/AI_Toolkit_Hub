import os
import sys
import asyncio
import time

# Add the project root to the Python path so it can find "modules" and "utils"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.TTS.Bark import BarkTTS
from utils.logger import get_logger

# Ensure logging is set up to see information from modules
import logging
logging.basicConfig(level=logging.INFO)

async def test_bark():
    # Define the new folder name where the sample will be stored
    output_dir = "bark_samples"
    
    # Create the folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory established at: {os.path.abspath(output_dir)}")
    
    # Initialize the Bark TTS engine
    print("\nInitializing Bark TTS (models will be lazy-loaded on first synthesis)...")
    tts = BarkTTS()
    
    # The text we want to synthesize. Bark supports some non-speech sounds like [laughs], [sighs], etc.
    # sample_text = "Hello there! [laughs] This is a test of the Suno Bark text-to-speech engine running locally."
    sample_text = "Yes! [laughs] By default, the suno-bark library aggressively offloads [anger] model layers back to your computer's system RAM..[crying] step-by-step to save GPU memory. But.. [sighs] since the models are being moved over the PCI-e bus thousands of times per generation, it crawls—which is exactly why it was taking 85 seconds for a ~10 word sentence."
    
    # The path where we will save the generated WAV file
    timestamp = int(time.time())
    output_file = os.path.join(output_dir, f"bark_test_{timestamp}.wav")
    
    print(f"\nGenerating audio for text:\n'{sample_text}'")
    print("This might take a while on the first run as models are downloaded/loaded into memory...")
    
    start_time = time.time()
    
    # Perform the audio synthesis asynchronously
    try:
        await tts.synthesize_async(
            text=sample_text,
            output_path=output_file
        )
        elapsed_time = time.time() - start_time
        print(f"\nSuccess! Synthesis complete in {elapsed_time:.2f} seconds.")
        print(f"Your voice sample has been saved to: {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"\nAn error occurred during synthesis: {e}")

if __name__ == "__main__":
    # Run the async test script
    asyncio.run(test_bark())
