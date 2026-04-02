"""
AI Utility Toolkit — Pipeline Demos
=====================================
Demonstrates chaining multiple modules into real-world workflows.
Each demo is self-contained. Run only the ones you have keys for.

    python examples/pipeline_demo.py
"""

from main import toolkit
from utils.logger import get_logger

logger = get_logger(__name__)
DIVIDER = "=" * 58


def demo_llm_comparison():
    """Send the same prompt to OpenAI, Claude, and Groq."""
    print(f"\n{DIVIDER}")
    print("  DEMO 1 — Multi-Provider LLM Comparison")
    print(DIVIDER)

    prompt = "Explain recursion in exactly two sentences."
    providers = {
        "OpenAI (GPT-4o)": lambda: toolkit.llms.openai.chat(prompt),
        "Claude (Sonnet)":  lambda: toolkit.llms.claude.chat(prompt),
        "Groq (LLaMA 3.3)": lambda: toolkit.llms.groq.chat(prompt),
    }
    import time
    for name, fn in providers.items():
        try:
            start = time.time()
            response = fn()
            elapsed = time.time() - start
            print(f"\n[{name}] ({elapsed:.2f}s)\n  {response}")
        except Exception as e:
            print(f"\n[{name}] SKIPPED — {e}")


def demo_audio_pipeline(audio_file: str = "sample.mp3"):
    """Transcribe → Translate → TTS pipeline."""
    print(f"\n{DIVIDER}")
    print("  DEMO 2 — Audio → Transcript → Translate → TTS")
    print(DIVIDER)
    try:
        print(f"\n[Step 1] Transcribing '{audio_file}' with Whisper...")
        transcript = toolkit.transcribe.whisper.transcribe(audio_file, language="en")
        print(f"  Transcript: {transcript[:120]}...")

        print("\n[Step 2] Translating to French with DeepL...")
        french = toolkit.translate.deepl.translate(transcript, target_lang="FR")
        print(f"  French: {french[:120]}...")

        print("\n[Step 3] Synthesizing with Edge TTS (free)...")
        audio_bytes = toolkit.tts.edge.synthesize(french, output_path="output_french.mp3")
        print(f"  Saved → output_french.mp3 ({len(audio_bytes)} bytes)")
        print("\n✅ Audio pipeline complete!")
    except Exception as e:
        print(f"\n❌ Audio pipeline failed: {e}")


def demo_qr_suite():
    """Generate multiple types of QR codes."""
    print(f"\n{DIVIDER}")
    print("  DEMO 3 — QR Code Suite")
    print(DIVIDER)
    try:
        print("\n[1] Standard URL QR...")
        toolkit.qr.qrcode.generate(
            "https://github.com/your-username/ai-utility-toolkit",
            fill_color="#1a1a2e", back_color="#ffffff", output_path="qr_url.png")
        print("  ✅ qr_url.png")

        print("\n[2] Styled rounded QR with gradient...")
        toolkit.qr.qrcode.generate_styled(
            "https://github.com/your-username/ai-utility-toolkit",
            module_style="rounded", fill_color=(26, 26, 46),
            gradient=True, gradient_color=(100, 50, 200), output_path="qr_styled.png")
        print("  ✅ qr_styled.png")

        print("\n[3] WiFi QR...")
        toolkit.qr.segno.generate_wifi(
            ssid="MyHomeNetwork", password="supersecret123",
            security="WPA", output_path="qr_wifi.png")
        print("  ✅ qr_wifi.png")

        print("\n[4] vCard contact QR...")
        toolkit.qr.segno.generate_vcard(
            name="Manish Developer", email="manish@example.com",
            phone="+91-9876543210", org="AI Utility Toolkit",
            output_path="qr_vcard.png")
        print("  ✅ qr_vcard.png")

        print("\n[5] SVG QR (vector, transparent bg)...")
        toolkit.qr.segno.generate(
            "https://github.com/your-username/ai-utility-toolkit",
            output_format="svg", dark="#1a1a2e", light="transparent",
            output_path="qr_vector.svg")
        print("  ✅ qr_vector.svg")

        print("\n[6] Terminal QR preview:")
        toolkit.qr.segno.print_terminal("https://github.com")
        print("\n✅ QR suite complete!")
    except Exception as e:
        print(f"\n❌ QR suite failed: {e}")


def demo_youtube_to_blog(youtube_url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
    """YouTube → Transcribe → Blog Post pipeline."""
    print(f"\n{DIVIDER}")
    print("  DEMO 4 — YouTube → Transcribe → Blog Post")
    print(DIVIDER)
    try:
        print("\n[Step 1] Downloading audio...")
        audio_path = toolkit.downloader.ytdlp.download_audio(
            youtube_url, audio_format="mp3", filename="yt_audio")
        print(f"  Downloaded → '{audio_path}'")

        print("\n[Step 2] Transcribing with AssemblyAI...")
        result = toolkit.transcribe.assemblyai.transcribe(audio_path, auto_chapters=True)
        transcript = result.get("text", "")
        chapters = result.get("chapters", [])
        print(f"  {len(transcript)} chars | {len(chapters)} chapters")

        print("\n[Step 3] Writing blog post with GPT-4o...")
        blog_post = toolkit.llms.openai.chat(
            prompt=f"Write a blog post from this transcript:\n\n{transcript[:3000]}",
            system="You are an expert content writer. Format in Markdown with headers.",
            max_tokens=1500,
        )
        with open("output_blog_post.md", "w", encoding="utf-8") as f:
            f.write(blog_post)
        print(f"  ✅ Saved → output_blog_post.md")
        print("\n✅ YouTube → Blog pipeline complete!")
    except Exception as e:
        print(f"\n❌ YouTube pipeline failed: {e}")


def demo_shortlink_qr():
    """Shorten URL with Bitly then generate QR for it."""
    print(f"\n{DIVIDER}")
    print("  DEMO 5 — URL Shortener + QR Bundle")
    print(DIVIDER)
    long_url = "https://github.com/your-username/ai-utility-toolkit"
    try:
        print("\n[Step 1] Shortening with Bitly...")
        result = toolkit.shortlink.bitly.shorten(long_url, title="AI Toolkit")
        short_url = result["short_url"]
        print(f"  Short URL: {short_url}")

        print("\n[Step 2] Generating QR for short URL...")
        toolkit.qr.segno.generate(
            short_url, output_format="png", scale=15, output_path="qr_shortlink.png")
        print("  ✅ qr_shortlink.png")

        print("\n[Step 3] Fetching click analytics...")
        analytics = toolkit.shortlink.bitly.get_clicks(short_url, unit="day", units=7)
        print(f"  Clicks (last 7 days): {analytics['total_clicks']}")
        print("\n✅ Shortlink + QR bundle complete!")
    except Exception as e:
        print(f"\n❌ Shortlink + QR pipeline failed: {e}")


if __name__ == "__main__":
    print(f"\n{DIVIDER}")
    print("  AI Utility Toolkit — Pipeline Demos")
    print(DIVIDER)
    print("\nRunning environment health check...\n")
    toolkit.health_check()

    print("\nStarting demos (missing keys are skipped automatically)...\n")

    demo_llm_comparison()
    demo_qr_suite()
    demo_shortlink_qr()

    # Uncomment these when you have the relevant files/keys:
    # demo_audio_pipeline("sample.mp3")
    # demo_youtube_to_blog("https://www.youtube.com/watch?v=YOUR_ID")

    print(f"\n{DIVIDER}")
    print("  All demos complete.")
    print(f"{DIVIDER}\n")
