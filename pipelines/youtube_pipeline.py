import os
import json
import time
import asyncio
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import httpx
import requests
from ddgs import DDGS
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from openai import AsyncOpenAI

console = Console()

# ==============================================================================
# CONFIGURATION
# ==============================================================================
PIPELINE_CONFIG = {
    "NVIDIA_API_KEY": os.getenv("NVIDIA_DEEPSEEK_API_KEY", ""),
    "LLM_MODEL": "deepseek-ai/deepseek-v3.2",
    "TARGET_VIDEO_LENGTH_MINUTES": 10,
    "CHANNEL_TONE": "educational and entertaining",
    "TARGET_AUDIENCE": "general curious public",
    "CHANNEL_NAME": "Tech India"
}

BASE_OUTPUT_DIR = Path("output")
BASE_OUTPUT_DIR.mkdir(exist_ok=True)


# ==============================================================================
# TOOL IMPLEMENTATIONS (PYTHON LEVEL - ASYNC WRAPPERS)
# ==============================================================================
async def scrape_youtube_trending(niche: str) -> str:
    """Find trending YouTube videos in a niche via DDG Search."""
    def _run():
        try:
            results = DDGS().text(f"{niche} site:youtube.com", max_results=10)
            if not results: return json.dumps([])
            return json.dumps([{"title": r.get("title", ""), "snippet": r.get("body", ""), "url": r.get("href", "")} for r in results])
        except Exception as e:
            return json.dumps({"error": str(e)})
    return await asyncio.to_thread(_run)


async def scrape_google_trends(niche: str) -> str:
    """Mock/Simulate identifying rising queries for the niche using DDG news search."""
    def _run():
        try:
            results = DDGS().news(f"{niche}", max_results=5)
            if not results: return json.dumps([])
            return json.dumps([{"headline": r.get("title", ""), "source": r.get("source", "")} for r in results])
        except Exception as e:
            return json.dumps({"error": str(e)})
    return await asyncio.to_thread(_run)


async def scrape_reddit_buzz(niche: str) -> str:
    """Fetch hot posts from Reddit via JSON API."""
    def _run():
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(f"https://www.reddit.com/search.json?q={niche}&sort=hot&limit=5", headers=headers, timeout=10)
            if res.status_code == 200:
                posts = res.json().get("data", {}).get("children", [])
                return json.dumps([{"title": p["data"]["title"], "upvotes": p["data"]["ups"], "comments": p["data"]["num_comments"]} for p in posts])
            return json.dumps({"error": f"reddit search failed: {res.status_code}"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    return await asyncio.to_thread(_run)


async def save_output_file(filename: str, content: str, output_dir: Path) -> str:
    """Generic tool to save generated content to output directory."""
    clean_filename = Path(filename).name
    path = output_dir / clean_filename
    await asyncio.to_thread(path.write_text, content, encoding="utf-8")
    return json.dumps({"status": f"Saved {clean_filename}"})


# ==============================================================================
# OPENAI-COMPATIBLE SCHEMAS
# ==============================================================================
WORKER_A_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "scrape_youtube_trending",
            "description": "Find top video titles and snippets for a niche.",
            "parameters": {"type": "object", "properties": {"niche": {"type": "string"}}, "required": ["niche"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_google_trends",
            "description": "Identify rising queries/momentum for a niche.",
            "parameters": {"type": "object", "properties": {"niche": {"type": "string"}}, "required": ["niche"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_reddit_buzz",
            "description": "Find top discussed subtopics, upvotes and comments.",
            "parameters": {"type": "object", "properties": {"niche": {"type": "string"}}, "required": ["niche"]}
        }
    }
]

WORKER_B_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_gaps",
            "description": "Report what angles are missing and propose 5 video ideas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis": {"type": "string"},
                    "ideas": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["analysis", "ideas"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "select_best_idea",
            "description": "Select the single best idea based on metrics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "best_idea_title": {"type": "string"},
                    "justification": {"type": "string"}
                },
                "required": ["best_idea_title", "justification"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_viral_title_variants",
            "description": "Generate 10 title variants for the chosen idea.",
            "parameters": {
                "type": "object",
                "properties": {
                    "titles": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["titles"]
            }
        }
    }
]

WORKER_C_TOOLS = [
    {"type": "function", "function": {"name": "generate_video_script", "description": "Save full spoken script (name is script.md) with visual cues.", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_video_description", "description": "Save SEO-optimized description (name is description.txt).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_tags", "description": "Save 30 SEO tags (name is tags.txt).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_thumbnail_brief", "description": "Save visual brief and AI prompt explicitly for Nano Banana Pro (name is thumbnail_brief.md).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_chapters_and_timestamps", "description": "Save 6-10 chapter markers (name is chapters.txt).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_upload_checklist", "description": "Save pre-upload checklist & Studio guide (name is upload_checklist.md).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_shorts_hook", "description": "Save standalone 45-second Shorts/Reels script (name is shorts_script.md).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_community_post", "description": "Save social media posts (Community, X thread, LinkedIn) (name is social_posts.md).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}}
]


# ==============================================================================
# AGENT RUNNER LOOP (ASYNC OPENAI API)
# ==============================================================================
async def run_agent(client: AsyncOpenAI, system_prompt: str, user_prompt: str, tools: list, output_dir: Path) -> str:
    """Executes a DeepSeek/OpenAI tool-use loop until the agent completes its job."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    while True:
        # BETTER EXECUTION: Custom infinite-timeout and visual retry system.
        # Catches NVIDIA server 504s immediately and retries with visual feedback.
        for attempt in range(1, 11):  # Up to 10 manual retries
            try:
                response = await client.chat.completions.create(
                    model=PIPELINE_CONFIG["LLM_MODEL"],
                    messages=messages,
                    tools=tools,
                    temperature=0.7,
                    max_tokens=8000
                )
                break  # Success, break out of retry loop
            except Exception as e:
                err_msg = str(e).lower()
                if attempt == 10:
                    console.print(f"\n[red]❌ Agent failed after 10 attempts: {e}[/red]")
                    return ""
                    
                if "504" in err_msg or "timeout" in err_msg or "502" in err_msg or "503" in err_msg:
                    wait = 2 ** attempt
                    console.print(f"\n[yellow]⚠️ NVIDIA Server Overloaded (50x/Timeout). No limits applying! Retrying in {wait}s... (Attempt {attempt}/10)[/yellow]")
                    await asyncio.sleep(wait)
                else:
                    console.print(f"\n[red]API Error: {e}[/red]")
                    return ""
            
        choice = response.choices[0]
        message = choice.message
        
        if getattr(message, "tool_calls", None):
            messages.append(message)
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                
                res = ""
                if tool_name == "scrape_youtube_trending":
                    res = await scrape_youtube_trending(**args)
                elif tool_name == "scrape_google_trends":
                    res = await scrape_google_trends(**args)
                elif tool_name == "scrape_reddit_buzz":
                    res = await scrape_reddit_buzz(**args)
                elif tool_name in ["analyze_gaps", "select_best_idea", "generate_viral_title_variants"]:
                    res = json.dumps({"status": f"{tool_name} recorded."})
                elif tool_name.startswith("generate_"):
                    filename = args.get("filename", f"{tool_name}.txt")
                    content = args.get("content", "")
                    res = await save_output_file(filename, content, output_dir)
                else:
                    res = json.dumps({"error": f"Unknown tool: {tool_name}"})
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": res
                })
        else:
            return message.content or ""


# ==============================================================================
# MAIN ORCHESTRATOR
# ==============================================================================
async def async_main():
    if not PIPELINE_CONFIG["NVIDIA_API_KEY"]:
        console.print("[red]Error: NVIDIA_DEEPSEEK_API_KEY environment variable is missing.[/red]")
        return

    # Using httpx.Timeout(None) guarantees NO client-side logic limits the request duration
    client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=PIPELINE_CONFIG["NVIDIA_API_KEY"],
        timeout=httpx.Timeout(None), 
        max_retries=0  # Disabled silent retries so our custom visual retry loop handles it
    )
    
    console.print(f"\n[bold cyan]🎥 YouTube Automation Pipeline (Powered by {PIPELINE_CONFIG['LLM_MODEL']})[/bold cyan]")
    title = console.input("[bold yellow]Enter the title of the video: [/bold yellow]")
    
    session_id = uuid.uuid4().hex[:8]
    output_dir = BASE_OUTPUT_DIR / session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"\n[bold green]✅ Session initialized. Run ID: {session_id}[/bold green]")
    console.print(f"[dim]Output files will be saved to: {output_dir}[/dim]\n")

    start_total = time.time()
    
    # ── Worker A
    sys_a = "You are Worker A (Trend Intelligence). Use all your tools to gather trending momentum, then summarize the raw data clearly."
    prompt_a = f"Gather intelligence for the topic of this video title: {title}"
    
    start_a = time.time()
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task_a = progress.add_task("[bold blue]Worker A — Gathering Trend Intelligence...", total=None)
        trends_data = await run_agent(client, sys_a, prompt_a, WORKER_A_TOOLS, output_dir)
        time_a = time.time() - start_a
        progress.update(task_a, completed=100, description=f"[bold green]Worker A — Complete! ({time_a:.2f}s)[/bold green]")
        
    # ── Worker B
    sys_b = "You are Worker B (Content Strategy). Call analyze_gaps(), select_best_idea(), and generate_viral_title_variants() successively based on the trend data provided. Provide a summary at the end."
    prompt_b = f"Process this trend data and decide on the best video strategy for the video titled '{title}':\n\n{trends_data}"
    
    start_b = time.time()
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task_b = progress.add_task("[bold magenta]Worker B — Strategizing & Ideation...", total=None)
        strategy_data = await run_agent(client, sys_b, prompt_b, WORKER_B_TOOLS, output_dir)
        time_b = time.time() - start_b
        progress.update(task_b, completed=100, description=f"[bold green]Worker B — Complete! ({time_b:.2f}s)[/bold green]")
        
    # ── Worker C (Async Parallelized)
    prompt_c = f"Create the requested file. Make sure it's fully complete and uses this approved strategy data:\n\n{strategy_data}\n\nTitle of video: {title}"

    start_c = time.time()
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task_c = progress.add_task("[bold yellow]Worker C — Generating Video Package Assets...", total=None)
        
        for tool in WORKER_C_TOOLS:
            sys_c = f"""You are Worker C (Full Package Generator).
Config: Length={PIPELINE_CONFIG['TARGET_VIDEO_LENGTH_MINUTES']} mins, Tone={PIPELINE_CONFIG['CHANNEL_TONE']}, Audience={PIPELINE_CONFIG['TARGET_AUDIENCE']}, Channel={PIPELINE_CONFIG['CHANNEL_NAME']}.
Your ONLY job is to execute the following tool: {tool['function']['name']}.
Provide rich, complete, ready-to-upload content.
CRITICAL INSTRUCTION: Any types of Image Generation prompt (such as thumbnail brief prompts) MUST specifically include that they are for 'Nano Banana Pro'. Always append "(Generator format: Nano Banana Pro)" or similar to image prompts.
If the tool is generate_thumbnail_brief, focus entirely on creating a prompt for 'Nano Banana Pro'."""
            await run_agent(client, sys_c, prompt_c, [tool], output_dir)
        time_c = time.time() - start_c
        progress.update(task_c, completed=100, description=f"[bold green]Worker C — Complete! ({time_c:.2f}s)[/bold green]")

    total_time = time.time() - start_total

    console.print(f"\n[bold green]🎬 YouTube Package Ready! All files saved to {output_dir}[/bold green]")
    console.print(f"\n[bold cyan]⏱️ Pipeline Timings:[/bold cyan]")
    console.print(f"[dim]• Worker A (Intelligence): {time_a:.2f}s[/dim]")
    console.print(f"[dim]• Worker B (Strategy):     {time_b:.2f}s[/dim]")
    console.print(f"[dim]• Worker C (Generation):   {time_c:.2f}s[/dim]")
    console.print(f"[bold cyan]• Total Time Taken:      {total_time:.2f}s[/bold cyan]\n")
    
    from rich.table import Table
    table = Table(title=f"Generated Assets (ID: {session_id})")
    table.add_column("Filename", style="cyan")
    table.add_column("Status", style="green")
    for f in output_dir.glob("*"):
        table.add_row(f.name, "✅ Saved")
    console.print(table)


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        console.print("\n[red]Pipeline interrupted by user.[/red]")

if __name__ == "__main__":
    main()
