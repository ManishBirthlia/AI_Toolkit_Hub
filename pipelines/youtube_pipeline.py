import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import requests
from ddgs import DDGS
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import openai

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
    "CHANNEL_NAME": "Omni Insights"
}

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ==============================================================================
# TOOL IMPLEMENTATIONS (PYTHON LEVEL)
# ==============================================================================
def scrape_youtube_trending(niche: str) -> str:
    """Find trending YouTube videos in a niche via DDG Search."""
    results = DDGS().text(f"{niche} site:youtube.com", max_results=10)
    return json.dumps([{"title": r["title"], "snippet": r["body"], "url": r["href"]} for r in results])


def scrape_google_trends(niche: str) -> str:
    """Mock/Simulate identifying rising queries for the niche using DDG news search."""
    results = DDGS().news(f"{niche}", max_results=5)
    return json.dumps([{"headline": r["title"], "source": r["source"]} for r in results])


def scrape_reddit_buzz(niche: str) -> str:
    """Fetch hot posts from Reddit via JSON API."""
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(f"https://www.reddit.com/search.json?q={niche}&sort=hot&limit=5", headers=headers)
    if res.status_code == 200:
        posts = res.json().get("data", {}).get("children", [])
        return json.dumps([{"title": p["data"]["title"], "upvotes": p["data"]["ups"], "comments": p["data"]["num_comments"]} for p in posts])
    return json.dumps({"error": "reddit search failed"})


def analyze_gaps(analysis: str, ideas: list) -> str:
    """Store generated ideas."""
    return json.dumps({"status": "Gaps analyzed and ideas mapped."})


def select_best_idea(best_idea_title: str, justification: str) -> str:
    """Store selected best idea."""
    return json.dumps({"status": "Best idea received successfully."})


def generate_viral_title_variants(titles: list) -> str:
    """Store title variants."""
    return json.dumps({"status": "Titles received successfully."})


def save_output_file(filename: str, content: str) -> str:
    """Generic tool to save generated content to output directory."""
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    return json.dumps({"status": f"Saved {filename}"})


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
    {"type": "function", "function": {"name": "generate_video_script", "description": "Save full spoken script (output/script.md) with visual cues.", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_video_description", "description": "Save SEO-optimized description (output/description.txt).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_tags", "description": "Save 30 SEO tags (output/tags.txt).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_thumbnail_brief", "description": "Save visual brief and AI prompt (output/thumbnail_brief.md).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_chapters_and_timestamps", "description": "Save 6-10 chapter markers (output/chapters.txt).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_upload_checklist", "description": "Save pre-upload checklist & Studio guide (output/upload_checklist.md).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_shorts_hook", "description": "Save standalone 45-second Shorts/Reels script (output/shorts_script.md).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "generate_community_post", "description": "Save social media posts (Community, X thread, LinkedIn) (output/social_posts.md).", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}}
]


# ==============================================================================
# AGENT RUNNER LOOP (OPENAI API / DEEPSEEK FORMAT)
# ==============================================================================
def run_agent(client: openai.OpenAI, system_prompt: str, user_prompt: str, tools: list) -> str:
    """Executes a DeepSeek/OpenAI tool-use loop until the agent completes its job."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    while True:
        response = client.chat.completions.create(
            model=PIPELINE_CONFIG["LLM_MODEL"],
            messages=messages,
            tools=tools,
            temperature=0.7,
            max_tokens=8000
        )
        
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
                
                if tool_name == "scrape_youtube_trending":
                    res = scrape_youtube_trending(**args)
                elif tool_name == "scrape_google_trends":
                    res = scrape_google_trends(**args)
                elif tool_name == "scrape_reddit_buzz":
                    res = scrape_reddit_buzz(**args)
                elif tool_name in ["analyze_gaps", "select_best_idea", "generate_viral_title_variants"]:
                    res = json.dumps({"status": f"{tool_name} recorded."})
                elif tool_name.startswith("generate_"):
                    res = save_output_file(**args)
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
def main():
    if not PIPELINE_CONFIG["NVIDIA_API_KEY"]:
        console.print("[red]Error: NVIDIA_DEEPSEEK_API_KEY environment variable is missing.[/red]")
        return

    client = openai.OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=PIPELINE_CONFIG["NVIDIA_API_KEY"]
    )
    
    console.print(f"\n[bold cyan]🎥 YouTube Automation Pipeline (Powered by {PIPELINE_CONFIG['LLM_MODEL']})[/bold cyan]")
    niche = console.input("[bold yellow]Enter your YouTube niche or topic: [/bold yellow]")
    
    # ── Worker A
    sys_a = "You are Worker A (Trend Intelligence). Use all your tools to gather trending momentum, then summarize the raw data clearly."
    prompt_a = f"Gather intelligence for niche: {niche}"
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task_a = progress.add_task("[bold blue]Worker A — Gathering Trend Intelligence...", total=None)
        trends_data = run_agent(client, sys_a, prompt_a, WORKER_A_TOOLS)
        progress.update(task_a, completed=100, description="[bold green]Worker A — Complete![/bold green]")
        
    # ── Worker B
    sys_b = "You are Worker B (Content Strategy). Call analyze_gaps(), select_best_idea(), and generate_viral_title_variants() successively based on the trend data provided. Provide a summary at the end."
    prompt_b = f"Process this trend data and decide on the best video strategy:\n\n{trends_data}"
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task_b = progress.add_task("[bold magenta]Worker B — Strategizing & Ideation...", total=None)
        strategy_data = run_agent(client, sys_b, prompt_b, WORKER_B_TOOLS)
        progress.update(task_b, completed=100, description="[bold green]Worker B — Complete![/bold green]")
        
    # ── Worker C
    sys_c = f"""You are Worker C (Full Package Generator).
Config: Length={PIPELINE_CONFIG['TARGET_VIDEO_LENGTH_MINUTES']} mins, Tone={PIPELINE_CONFIG['CHANNEL_TONE']}, Audience={PIPELINE_CONFIG['TARGET_AUDIENCE']}, Channel={PIPELINE_CONFIG['CHANNEL_NAME']}.
You MUST sequentially call EVERY tool provided to save the 8 files to the output directory:
generate_video_script -> script.md
generate_video_description -> description.txt
generate_tags -> tags.txt
generate_thumbnail_brief -> thumbnail_brief.md
generate_chapters_and_timestamps -> chapters.txt
generate_upload_checklist -> upload_checklist.md
generate_shorts_hook -> shorts_script.md
generate_community_post -> social_posts.md"""
    prompt_c = f"Create all files based on this approved strategy:\n\n{strategy_data}"

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task_c = progress.add_task("[bold yellow]Worker C — Generating Video Package Assets...", total=None)
        run_agent(client, sys_c, prompt_c, WORKER_C_TOOLS)
        progress.update(task_c, completed=100, description="[bold green]Worker C — Complete![/bold green]")

    console.print("\n[bold green]🎬 YouTube Package Ready! All files saved to /output[/bold green]")
    
    from rich.table import Table
    table = Table(title="Generated Assets")
    table.add_column("Filename", style="cyan")
    table.add_column("Status", style="green")
    for f in OUTPUT_DIR.glob("*"):
        table.add_row(f.name, "✅ Saved")
    console.print(table)


if __name__ == "__main__":
    main()
