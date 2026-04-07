# 🔗 AI Agent Integration Patterns: Series, Parallel & Beyond
> From a single text-to-text agent → to distributed mesh architectures performing real-world work.
> Every pattern. Every topology. Built to actually do things.

---

## How to Read This Document

Each level introduces a new **structural pattern** — how agents and tools are wired together to perform work. Patterns build on each other. Every level includes:
- A diagram of the architecture
- What problem it solves
- A real-world example
- Working code
- When to use it vs. the level before

**Legend:**
- `→` Series (sequential, output of one feeds next)
- `⇉` Parallel (simultaneous execution)
- `↻` Loop / cycle (output feeds back as input)
- `⊕` Merge (multiple inputs combined into one)
- `⊗` Branch (one input splits into multiple paths)

---

# LEVEL 1 — Single Agent, Text-to-Text
> *"One input. One output. No tools. No memory."*

```
[User Text] → [LLM] → [Text Output]
```

### What It Is
The atomic unit. A single language model receives a text prompt and produces a text response. No tools, no chaining, no memory. One call, one answer.

### Real-World Tasks It Can Do
- Summarize a document
- Translate a paragraph
- Answer a factual question
- Classify a support ticket (positive / negative / neutral)
- Rewrite a sentence in a different tone
- Extract data from unstructured text

### Code
```python
import anthropic

client = anthropic.Anthropic()

def text_to_text(prompt: str, system: str = "") -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# Example 1: Summarization
summary = text_to_text(
    prompt="Summarize this in 3 bullet points:\n\n" + long_document,
    system="You are a technical summarizer. Be concise and precise."
)

# Example 2: Extraction
data = text_to_text(
    prompt="Extract: company name, date, invoice amount from:\n\n" + invoice_text,
    system="Return only JSON with keys: company, date, amount."
)

# Example 3: Classification
label = text_to_text(
    prompt="Classify this support ticket as: bug / feature_request / question\n\n" + ticket,
    system="Return only the label, nothing else."
)
```

### Characteristics
| Property | Value |
|---|---|
| **Agents** | 1 |
| **Tools** | 0 |
| **Latency** | Single API call |
| **Complexity** | Minimal |
| **Failure points** | 1 (the LLM call) |

### Limitations
- No access to real-time data
- No ability to take actions
- No memory between calls
- Output quality bounded by what the model knows

---

# LEVEL 2 — Single Agent, Series Tool Use
> *"One agent. Multiple tools. Used one at a time, in sequence."*

```
[User Input] → [Agent] → [Tool A] → [Agent] → [Tool B] → [Agent] → [Tool C] → [Final Output]
```

### What It Is
The agent decides to use tools, but it uses them **one at a time**, waiting for each result before deciding what to do next. The agent is the "brain" that sequences the tool calls.

### The Pattern
```
Step 1: User asks a question
Step 2: Agent thinks → decides it needs Tool A
Step 3: Tool A runs → returns result to Agent
Step 4: Agent thinks → decides it needs Tool B (with new context)
Step 5: Tool B runs → returns result to Agent
Step 6: Agent has enough info → writes final answer
```

### Real-World Tasks
- Research a topic: search → read page → summarize → cite sources
- Data pipeline: query DB → transform data → write to file
- Content creation: get facts from API → write article → check grammar

### Code
```python
import anthropic
import json

client = anthropic.Anthropic()

# Define tools
tools = [
    {
        "name": "web_search",
        "description": "Search the web for information",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    },
    {
        "name": "fetch_url",
        "description": "Fetch the full content of a web page",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"]
        }
    },
    {
        "name": "save_to_file",
        "description": "Save content to a local file",
        "input_schema": {
            "type": "object",
            "properties": {"filename": {"type": "string"}, "content": {"type": "string"}},
            "required": ["filename", "content"]
        }
    }
]

def execute_tool(name: str, args: dict) -> str:
    """Your actual tool implementations."""
    if name == "web_search":    return do_web_search(args["query"])
    if name == "fetch_url":     return do_fetch_url(args["url"])
    if name == "save_to_file":  return do_save_file(args["filename"], args["content"])

def series_agent(task: str) -> str:
    messages = [{"role": "user", "content": task}]
    
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            tools=tools,
            messages=messages,
            max_tokens=4096
        )
        
        # Agent is done
        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if hasattr(b, "text"))
        
        # Agent wants to use a tool — execute ONE tool at a time (series)
        messages.append({"role": "assistant", "content": response.content})
        
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                print(f"  → Used tool: {block.name}({block.input})")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })
        
        messages.append({"role": "user", "content": tool_results})

# Usage
result = series_agent("Research the latest green hydrogen cost trends and save a summary to hydrogen_report.txt")
# Agent will: search → fetch article → search again → save file
# Each tool call waits for the previous to complete
```

### Execution Trace
```
User: "Research green hydrogen costs and save a report"
  Turn 1: Agent calls web_search("green hydrogen cost 2025")
           ← returns: [list of articles]
  Turn 2: Agent calls fetch_url("best-article.com/hydrogen")
           ← returns: [full article text]
  Turn 3: Agent calls save_to_file("report.txt", summarized_content)
           ← returns: "File saved"
  Turn 4: Agent returns: "I've researched and saved your report."
```

### When the Series Pattern Is Right
- Each step depends on the previous step's output
- You need the agent to reason between each tool call
- Tools have side effects that must happen in order (e.g., first create then update)
- You need a clear audit trail of decisions

---

# LEVEL 3 — Single Agent, Multi-Modal Series
> *"One agent. Multiple input types. Processed in sequence."*

```
[Image] ──┐
[Audio] ──┤→ [Preprocessors] → [Agent] → [Output]
[PDF]   ──┘
```

### What It Is
A single agent handles multiple types of input (text, images, audio, documents) by preprocessing each one into text or structured data before the LLM processes it — all in series.

### Pipeline Per Input Type
```
Audio Input:   [Voice File] → [STT/Whisper] → [Transcript Text] → [LLM]
Image Input:   [Image File] → [Vision LLM or OCR] → [Description/Text] → [LLM]
PDF Input:     [PDF File]   → [PDF Parser] → [Extracted Text] → [LLM]
Data Input:    [CSV/JSON]   → [Data Formatter] → [Structured Text] → [LLM]
```

### Code
```python
import anthropic
import base64
from faster_whisper import WhisperModel

client = anthropic.Anthropic()
stt_model = WhisperModel("base")

def process_input(content) -> list:
    """Convert any input type into LLM-ready content blocks."""
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    
    elif content["type"] == "audio":
        # Series step 1: STT
        segments, _ = stt_model.transcribe(content["path"])
        transcript = " ".join(s.text for s in segments)
        return [{"type": "text", "text": f"[Transcribed audio]: {transcript}"}]
    
    elif content["type"] == "image":
        # Series step 1: encode image
        with open(content["path"], "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        return [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_data}},
            {"type": "text", "text": content.get("prompt", "Describe this image.")}
        ]
    
    elif content["type"] == "pdf":
        # Series step 1: extract text from PDF
        text = extract_pdf_text(content["path"])
        return [{"type": "text", "text": f"[Document content]:\n{text}"}]

def multimodal_agent(inputs: list, task: str) -> str:
    """Agent that processes multiple input types in series, then responds."""
    
    # Series: process each input one by one
    content_blocks = []
    for inp in inputs:
        content_blocks.extend(process_input(inp))
    
    # Add the task instruction last
    content_blocks.append({"type": "text", "text": f"\nTask: {task}"})
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": content_blocks}]
    )
    return response.content[0].text

# Example: Meeting minutes generator
result = multimodal_agent(
    inputs=[
        {"type": "audio", "path": "meeting_recording.mp3"},
        {"type": "image", "path": "whiteboard_photo.jpg"},
        {"type": "pdf",   "path": "agenda.pdf"}
    ],
    task="Generate structured meeting minutes including decisions made and action items."
)
```

---

# LEVEL 4 — Series Pipeline (Agent Chain)
> *"Output of Agent A becomes input of Agent B. Linear. Sequential."*

```
[Input] → [Agent A] → [Output A] → [Agent B] → [Output B] → [Agent C] → [Final Output]
```

### What It Is
Multiple specialized agents in a **production line**. Each agent does one job and passes its output forward. No agent sees the user's original input directly — only what the previous agent produced.

### Why This Is Better Than One Agent
- Each agent has a **focused system prompt** tuned for exactly one task
- You can **swap out** individual agents without touching the rest
- Easier to **debug** — if the output is wrong, you know which stage failed
- Each stage can use a **different model** (cheap model for easy steps, powerful model for hard steps)

### Real-World Pipeline Example: LinkedIn Post Generator
```
[Raw Topic] → [Research Agent] → [Research Notes]
                                        ↓
                              [Structure Agent] → [Structured Outline]
                                                          ↓
                                                [Writing Agent] → [Draft Post]
                                                                        ↓
                                                              [Editor Agent] → [Final Post]
```

### Code
```python
import anthropic

client = anthropic.Anthropic()

def agent(system: str, user_input: str, model: str = "claude-sonnet-4-20250514") -> str:
    """A single configurable agent."""
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user_input}]
    )
    return response.content[0].text

def linkedin_post_pipeline(topic: str) -> dict:
    """4-stage series pipeline to create a LinkedIn post."""
    
    results = {"topic": topic}
    
    # Stage 1: Research (cheap model, broad knowledge)
    print("Stage 1: Researching...")
    results["research"] = agent(
        system="You are a research assistant. Find key facts, statistics, and angles on a topic. Output structured research notes.",
        user_input=f"Research this topic for a LinkedIn post: {topic}",
        model="claude-haiku-4-5-20251001"  # cheap model for research
    )
    
    # Stage 2: Structure (uses research output)
    print("Stage 2: Structuring...")
    results["outline"] = agent(
        system="You are a content strategist. Create a LinkedIn post outline: Hook → Insight 1 → Insight 2 → Insight 3 → CTA. Be specific about what goes in each section.",
        user_input=f"Create an outline using these research notes:\n\n{results['research']}",
        model="claude-haiku-4-5-20251001"
    )
    
    # Stage 3: Write (uses outline, stronger model for quality)
    print("Stage 3: Writing...")
    results["draft"] = agent(
        system="You are a LinkedIn expert who writes viral, authentic posts. No fluff, no em-dashes. Hook in first line. Short paragraphs. Professional but human voice.",
        user_input=f"Write a LinkedIn post from this outline:\n\n{results['outline']}",
        model="claude-sonnet-4-20250514"  # stronger model for the actual writing
    )
    
    # Stage 4: Edit (uses draft, focused on polish)
    print("Stage 4: Editing...")
    results["final"] = agent(
        system="You are a ruthless editor. Make it tighter, punchier. Remove any corporate jargon. Ensure the hook is irresistible. Max 300 words. Return only the final post.",
        user_input=f"Edit and improve this LinkedIn post:\n\n{results['draft']}"
    )
    
    return results

output = linkedin_post_pipeline("Why green hydrogen will be cheaper than natural gas by 2030")
print(output["final"])
```

### Using Different Models at Each Stage
```python
# Cost-optimized series pipeline
STAGE_MODELS = {
    "classify":    "claude-haiku-4-5-20251001",   # ~$0.00025/1K tokens — fast, cheap
    "extract":     "claude-haiku-4-5-20251001",   # structured extraction = easy task
    "analyze":     "claude-sonnet-4-20250514",    # reasoning = needs better model
    "write":       "claude-sonnet-4-20250514",    # quality output = use good model
    "verify":      "claude-haiku-4-5-20251001",   # yes/no check = cheap model fine
}
```

### Visualizing the Data Flow
```
[Raw Customer Email]
        ↓
[Stage 1: Classify]  — "billing complaint"
        ↓
[Stage 2: Extract]   — {customer: "...", issue: "...", amount: "..."}
        ↓
[Stage 3: Analyze]   — "High priority, valid complaint, refund warranted"
        ↓
[Stage 4: Write]     — "Dear [name], I apologize for..."
        ↓
[Stage 5: Verify]    — passes compliance check? → Yes
        ↓
[Final Email Response]
```

---

# LEVEL 5 — Parallel Execution (Fan-Out / Fan-In)
> *"Multiple agents or tools running at the same time. Results merged."*

```
              ┌→ [Agent A] ──┐
[Input] → ⊗  ├→ [Agent B] ──┤ → ⊕ → [Merge] → [Output]
              └→ [Agent C] ──┘
```

### What It Is
Instead of doing things one by one, you **fan out** to multiple agents or tools simultaneously, then **fan in** by merging their results. This is the single biggest performance unlock in agent systems.

### Why It Matters
- Tasks that took 30 seconds in series now take **10 seconds** (run 3 things at once)
- Independent subtasks should **never wait** for each other
- You can run the **same task multiple times** (with different prompts/models) and pick the best result

### Two Types of Parallel

#### Type A: Independent Tasks (true parallelism)
```
[Research topic X] ──┐
[Research topic Y] ──┤ → [Combine all research]
[Research topic Z] ──┘
All three run at the same time. None depend on any other.
```

#### Type B: Same Task, Different Approaches (parallel voting)
```
[Write email - formal tone]  ──┐
[Write email - casual tone]  ──┤ → [Pick best / blend]
[Write email - persuasive]   ──┘
All three write the same email differently. Best one wins.
```

### Code — Parallel Fan-Out
```python
import asyncio
import anthropic

client = anthropic.Anthropic()

async def async_agent(system: str, user_input: str) -> str:
    """Async wrapper for a single agent call."""
    # Note: use AsyncAnthropic for true async
    from anthropic import AsyncAnthropic
    async_client = AsyncAnthropic()
    
    response = await async_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user_input}]
    )
    return response.content[0].text

async def parallel_research(topics: list[str]) -> dict:
    """
    Fan-out: Research multiple topics simultaneously.
    Fan-in: Combine all results.
    """
    
    # Fan-out: launch all research tasks at the same time
    tasks = {
        topic: asyncio.create_task(
            async_agent(
                system="You are a research expert. Provide key facts and insights.",
                user_input=f"Research: {topic}"
            )
        )
        for topic in topics
    }
    
    # Fan-in: wait for ALL tasks to complete
    results = {}
    for topic, task in tasks.items():
        results[topic] = await task
    
    return results

async def parallel_vote(task: str, approaches: list[str]) -> str:
    """
    Fan-out: Same task, multiple approaches.
    Fan-in: LLM picks the best result.
    """
    
    # Fan-out: try all approaches simultaneously
    candidates = await asyncio.gather(*[
        async_agent(system=approach, user_input=task)
        for approach in approaches
    ])
    
    # Fan-in: judge picks the winner
    from anthropic import AsyncAnthropic
    async_client = AsyncAnthropic()
    
    judge_prompt = "\n\n".join(f"Option {i+1}:\n{c}" for i, c in enumerate(candidates))
    
    winner = await async_client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are a quality judge. Pick the single best option and return it unchanged.",
        messages=[{"role": "user", "content": f"Task: {task}\n\n{judge_prompt}\n\nReturn the best option:"}]
    )
    return winner.content[0].text

# Example 1: Parallel research
async def main():
    research = await parallel_research([
        "PEM electrolyzer efficiency improvements 2025",
        "Green hydrogen storage solutions",
        "Hydrogen fuel cell cost reduction trends"
    ])
    # All three run simultaneously — 3x faster than series

    # Example 2: Parallel voting (best of 3 approaches)
    best_email = await parallel_vote(
        task="Write a sales email to a CFO about investing in a green hydrogen plant",
        approaches=[
            "You write direct, ROI-focused business emails.",
            "You write warm, relationship-building emails.",
            "You write technical, data-driven emails for financial audiences."
        ]
    )

asyncio.run(main())
```

### Timing Comparison (Series vs. Parallel)
```
Series (3 tasks × 5 seconds each):
Task A: ████████████ (5s)
Task B:             ████████████ (5s)
Task C:                         ████████████ (5s)
Total: 15 seconds

Parallel (3 tasks × 5 seconds, running simultaneously):
Task A: ████████████ (5s)
Task B: ████████████ (5s)
Task C: ████████████ (5s)
Total: ~5 seconds   ← 3x faster
```

### When to Use Parallel
✅ Tasks are **independent** (no task needs another's output to start)
✅ You need **speed** and have the API rate limit budget
✅ You want **multiple perspectives** on the same problem
✅ You're processing a **batch** of similar items (10 emails, 20 documents)

---

# LEVEL 6 — Series + Parallel Hybrid
> *"Some steps must be sequential. Some can run simultaneously. Mix them."*

```
[Input]
   ↓
[Stage 1: Serial — must happen first]
   ↓
[Stage 2: Fan-Out — independent subtasks run in parallel]
   ├→ [Subtask A] ──┐
   ├→ [Subtask B] ──┤
   └→ [Subtask C] ──┘
         ↓ merge ⊕
[Stage 3: Serial — synthesis requires all subtask outputs]
   ↓
[Final Output]
```

### What It Is
Real workflows are neither purely serial nor purely parallel. You need **both**: sequential stages where order matters, with parallel bursts where independence allows speed.

### Real-World Example: Due Diligence Report
```
SERIAL:   [Parse company name and domain]
              ↓
PARALLEL: [Fetch financials] [Fetch news] [Fetch competitors] [Fetch team info]
              ↓ (all 4 complete)
SERIAL:   [Synthesize findings into report]
              ↓
PARALLEL: [Check legal risks] [Check market risks] [Check technical risks]
              ↓ (all 3 complete)
SERIAL:   [Write executive summary with all risks included]
```

### Code — Hybrid Pipeline
```python
import asyncio
from anthropic import AsyncAnthropic

async_client = AsyncAnthropic()

async def call(system: str, prompt: str) -> str:
    r = await async_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return r.content[0].text

async def due_diligence_pipeline(company_name: str) -> str:
    
    # ── STAGE 1: SERIAL ──────────────────────────────────
    # Must happen first — all other stages depend on this output
    print("Stage 1 [serial]: Identifying company profile...")
    profile = await call(
        system="Extract structured company info. Return JSON.",
        prompt=f"Company: {company_name}\nExtract: industry, size, founded, headquarters"
    )
    
    # ── STAGE 2: PARALLEL ────────────────────────────────
    # All 4 research tasks are independent — run simultaneously
    print("Stage 2 [parallel]: Running research in parallel...")
    (financials, news, competitors, team) = await asyncio.gather(
        call("You are a financial analyst.", f"Summarize financial health of {company_name}: {profile}"),
        call("You are a news analyst.", f"Summarize recent news about {company_name}"),
        call("You are a market analyst.", f"List key competitors of {company_name}: {profile}"),
        call("You are an HR analyst.", f"Assess leadership team quality of {company_name}")
    )
    
    # ── STAGE 3: SERIAL ──────────────────────────────────
    # Must wait for ALL of Stage 2 to complete
    print("Stage 3 [serial]: Synthesizing research...")
    synthesis = await call(
        system="You are a senior analyst. Synthesize research into key findings.",
        prompt=f"""
Company: {company_name}
Financials: {financials}
News: {news}
Competitors: {competitors}
Leadership: {team}

Provide: Key Strengths | Key Risks | Overall Assessment
"""
    )
    
    # ── STAGE 4: PARALLEL ────────────────────────────────
    # Three independent risk assessments
    print("Stage 4 [parallel]: Running risk assessments in parallel...")
    (legal_risk, market_risk, tech_risk) = await asyncio.gather(
        call("You are a legal risk expert.", f"Assess legal risks:\n{synthesis}"),
        call("You are a market risk expert.", f"Assess market risks:\n{synthesis}"),
        call("You are a tech risk expert.", f"Assess technology risks:\n{synthesis}")
    )
    
    # ── STAGE 5: SERIAL ──────────────────────────────────
    # Final synthesis — needs everything above
    print("Stage 5 [serial]: Writing executive summary...")
    final_report = await call(
        system="You are a managing partner writing an investment committee memo. Be direct, structured, decisive.",
        prompt=f"""
Write a due diligence memo for {company_name}.

Synthesis: {synthesis}
Legal Risk: {legal_risk}
Market Risk: {market_risk}
Technology Risk: {tech_risk}

Format: Executive Summary | Key Findings | Risk Matrix | Recommendation
"""
    )
    
    return final_report

report = asyncio.run(due_diligence_pipeline("Avaada Group"))
```

### Timing Visualization
```
SERIES  ██████
               PARALLEL [████████] [████████] [████████] [████████]
                                  ██████
                                        PARALLEL [██████] [██████] [██████]
                                                          ██████████████
Total: ~serial_time + max(parallel_batch_1) + serial + max(parallel_batch_2) + serial
```

---

# LEVEL 7 — Conditional Branching (Dynamic Routing)
> *"The input itself decides which agents get activated."*

```
                    ┌→ [Agent A: Path X] ──┐
[Input] → [Router] ─┤→ [Agent B: Path Y] ──┤ → [Output]
                    └→ [Agent C: Path Z] ──┘
```

### What It Is
A **router** (which can itself be an LLM) analyzes the input and decides which downstream agent or tool path to activate. Different inputs take different routes through the system.

### Router Types
| Router Type | How It Decides | Best For |
|---|---|---|
| **LLM Router** | LLM classifies input | Complex, nuanced routing decisions |
| **Rule Router** | If/else, regex, keyword matching | Clear-cut categories, speed |
| **Embedding Router** | Cosine similarity to route descriptions | Semantic routing without LLM call |
| **Score Router** | Each agent scores the input; highest score wins | When you want agents to self-select |

### Code — LLM Router
```python
import asyncio
from anthropic import AsyncAnthropic
from enum import Enum

async_client = AsyncAnthropic()

class Route(str, Enum):
    TECHNICAL   = "technical"
    COMMERCIAL  = "commercial"
    CREATIVE    = "creative"
    DATA        = "data"

async def router(user_input: str) -> Route:
    """LLM decides which specialist handles this request."""
    response = await async_client.messages.create(
        model="claude-haiku-4-5-20251001",  # cheap model for routing
        max_tokens=10,
        system="""Classify the request into exactly one category:
- technical: code, engineering, technical specs, debugging
- commercial: business, sales, pricing, contracts, strategy
- creative: writing, design, marketing copy, social media
- data: data analysis, spreadsheets, statistics, reports

Return only the category label.""",
        messages=[{"role": "user", "content": user_input}]
    )
    return Route(response.content[0].text.strip().lower())

async def technical_agent(task: str) -> str:
    return await async_agent("You are a senior engineer. Give precise technical answers.", task)

async def commercial_agent(task: str) -> str:
    return await async_agent("You are a business strategist. Focus on ROI and business value.", task)

async def creative_agent(task: str) -> str:
    return await async_agent("You are a creative director. Be original, engaging, and punchy.", task)

async def data_agent(task: str) -> str:
    return await async_agent("You are a data analyst. Be precise, cite numbers, give structured output.", task)

ROUTES = {
    Route.TECHNICAL:  technical_agent,
    Route.COMMERCIAL: commercial_agent,
    Route.CREATIVE:   creative_agent,
    Route.DATA:       data_agent,
}

async def routed_system(user_input: str) -> str:
    route = await router(user_input)
    print(f"  → Routing to: {route.value}")
    return await ROUTES[route](user_input)

# Examples
print(await routed_system("How do I optimize a Redis query for high throughput?"))
# → technical_agent

print(await routed_system("Write a LinkedIn caption for our new hydrogen plant launch"))
# → creative_agent

print(await routed_system("Analyze Q3 electrolyzer sales by region and flag outliers"))
# → data_agent
```

### Parallel Routing (Multi-Label)
Sometimes an input belongs to multiple categories and needs multiple specialists:

```python
async def multi_route(user_input: str) -> str:
    """Route to ALL relevant agents and merge results."""
    
    # LLM identifies ALL applicable routes
    response = await async_client.messages.create(
        model="claude-haiku-4-5-20251001",
        system="Return a JSON list of applicable categories: technical, commercial, creative, data. Return only JSON.",
        messages=[{"role": "user", "content": user_input}]
    )
    routes = json.loads(response.content[0].text)
    
    # Run all applicable agents in parallel
    results = await asyncio.gather(*[ROUTES[Route(r)](user_input) for r in routes])
    
    # Merge: synthesize all specialist outputs
    combined = "\n\n".join(f"[{r.upper()} PERSPECTIVE]:\n{res}" for r, res in zip(routes, results))
    return await async_agent(
        "Synthesize these specialist perspectives into one unified response.",
        combined
    )
```

---

# LEVEL 8 — Feedback Loops (Cycles)
> *"The output feeds back as input. The agent improves itself."*

```
[Input] → [Generator] → [Output]
               ↑              ↓
               └── [Critic] ←─┘
                   (if not good enough, loop again)
```

### What It Is
Instead of a one-shot pipeline, the output is **evaluated** and if it doesn't meet a quality threshold, it's fed back to the generator with critique. The loop runs until the output is good enough or a max iteration limit is hit.

### Loop Patterns

#### Generator-Critic Loop (Most Common)
```
[Generate draft]
      ↓
[Critic scores it] → Score ≥ threshold? → Yes → Done
      ↓
      No → [Critic provides specific feedback]
            ↓
      [Generator revises with feedback]
            ↓ (back to critic)
```

#### Self-Reflection Loop
```
[Agent produces output]
      ↓
[Same agent reviews its own output]
      ↓
Found issues? → Yes → [Agent revises]
      ↓
      No → Done
```

#### Test-Fix Loop (Code Generation)
```
[Agent writes code]
      ↓
[Execute code in sandbox]
      ↓
Tests pass? → Yes → Done
      ↓
      No → [Agent reads error, fixes code]
            ↓ (back to execute)
```

### Code — Generator-Critic Loop
```python
import asyncio
from dataclasses import dataclass
from anthropic import AsyncAnthropic

async_client = AsyncAnthropic()

@dataclass
class EvalResult:
    score: float       # 0.0 to 1.0
    feedback: str      # specific critique
    passed: bool       # did it meet the threshold?

async def generator(task: str, feedback: str = "", previous: str = "") -> str:
    """Generates or revises output."""
    prompt = task
    if feedback:
        prompt += f"\n\nPrevious attempt:\n{previous}\n\nCritic feedback:\n{feedback}\n\nRevise based on this feedback."
    
    r = await async_client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are an expert content creator. Produce high-quality output.",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048
    )
    return r.content[0].text

async def critic(task: str, output: str, criteria: str) -> EvalResult:
    """Evaluates output against specific criteria."""
    r = await async_client.messages.create(
        model="claude-haiku-4-5-20251001",
        system="""You are a strict quality evaluator. 
Return JSON: {"score": 0.0-1.0, "feedback": "specific actionable critique", "passed": true/false}
passed = true only if score >= 0.8""",
        messages=[{"role": "user", "content": f"Task: {task}\n\nCriteria: {criteria}\n\nOutput to evaluate:\n{output}"}],
        max_tokens=512
    )
    import json
    result = json.loads(r.content[0].text)
    return EvalResult(**result)

async def generator_critic_loop(
    task: str,
    criteria: str,
    max_iterations: int = 4
) -> dict:
    """Runs generate → critique → revise loop until quality threshold met."""
    
    history = []
    current_output = ""
    
    for i in range(max_iterations):
        print(f"  Iteration {i+1}/{max_iterations}")
        
        # Generate (or revise if not first iteration)
        feedback = history[-1]["feedback"] if history else ""
        current_output = await generator(task, feedback=feedback, previous=current_output)
        
        # Critique
        eval_result = await critic(task, current_output, criteria)
        print(f"  Score: {eval_result.score:.2f} | Passed: {eval_result.passed}")
        
        history.append({
            "iteration": i + 1,
            "output": current_output,
            "score": eval_result.score,
            "feedback": eval_result.feedback
        })
        
        # Exit loop if quality threshold met
        if eval_result.passed:
            print(f"  ✓ Passed quality check after {i+1} iteration(s)")
            break
    
    return {"final": current_output, "iterations": len(history), "history": history}

# Example: high-quality cold email generation
result = asyncio.run(generator_critic_loop(
    task="Write a cold email to a CFO about investing in a 50MW green hydrogen plant",
    criteria="""
    - Hook in subject line (curiosity or specific ROI number)
    - Under 150 words
    - Specific to CFO role (ROI, payback period, risk mitigation)
    - Clear single CTA
    - No buzzwords or clichés
    - Professional but human tone
    """
))
print(f"Final output after {result['iterations']} iterations:")
print(result["final"])
```

### Code — Test-Fix Loop (Code Agent)
```python
import subprocess

async def code_agent_with_tests(task: str, test_code: str, max_attempts: int = 5) -> str:
    """Generates code, runs tests, fixes failures — loops until green."""
    
    code = ""
    
    for attempt in range(max_attempts):
        # Generate code (first time) or fix it (subsequent times)
        if attempt == 0:
            code = await generator(f"Write Python code that: {task}")
        
        # Run the tests
        test_script = f"{code}\n\n{test_code}"
        result = subprocess.run(
            ["python", "-c", test_script],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            print(f"  ✓ All tests passed on attempt {attempt+1}")
            return code
        
        # Tests failed — feed error back to agent
        error_output = result.stderr + result.stdout
        print(f"  ✗ Tests failed: {error_output[:200]}")
        
        # Revise based on error
        code = await generator(
            task=f"Fix this Python code. Task: {task}",
            feedback=f"Tests failed with this error:\n{error_output}",
            previous=code
        )
    
    return code  # return best attempt even if tests didn't fully pass
```

---

# LEVEL 9 — Hierarchical Agent Trees
> *"An orchestrator breaks work into subtasks. Workers execute. Results roll up."*

```
                    [Orchestrator]
                    /      |      \
            [Worker A] [Worker B] [Worker C]
               /  \                   |
          [Tool1][Tool2]           [Tool3]
```

### What It Is
A **top-down tree** of agents. The orchestrator plans and delegates. Workers execute specialized tasks. Sub-workers or tools handle atomic operations. Results flow back up the tree.

### Why This Scales
- The orchestrator thinks at a **high level** — it never touches raw data
- Workers are **experts** in their domain — they don't know about the big picture
- You can add more layers as complexity grows
- Parallel execution at each layer compounds the speedups

### Three-Layer Hierarchy Example: Market Research System
```
LAYER 1 (Strategy):    [Research Director Agent]
                        "Plan the market research for X"
                              ↓ delegates to ↓
LAYER 2 (Execution):   [Industry Analyst] [Competitor Analyst] [Customer Analyst]
                        Each runs their own sub-pipeline
                              ↓ reports to ↓
LAYER 1 (Synthesis):   [Research Director Agent]
                        "Compile findings into report"
```

### Code
```python
import asyncio
from anthropic import AsyncAnthropic
import json

async_client = AsyncAnthropic()

async def worker_agent(role: str, task: str, tools: list = None) -> str:
    """A generic worker agent with optional tools."""
    response = await async_client.messages.create(
        model="claude-sonnet-4-20250514",
        system=f"You are a {role}. Complete your assigned task thoroughly.",
        tools=tools or [],
        messages=[{"role": "user", "content": task}],
        max_tokens=2048
    )
    return response.content[0].text

async def orchestrator(goal: str) -> str:
    """
    Orchestrator that:
    1. Breaks goal into subtasks
    2. Assigns subtasks to workers in parallel
    3. Synthesizes results
    """
    
    # Step 1: Planning (orchestrator thinks)
    plan_response = await async_client.messages.create(
        model="claude-sonnet-4-20250514",
        system="""You are a project orchestrator. Break any goal into 3-5 specific, 
independent subtasks that can be done in parallel. Each subtask needs: 
role (who should do it) and task (exactly what to do).
Return JSON: [{"role": "...", "task": "..."}]""",
        messages=[{"role": "user", "content": f"Plan this: {goal}"}],
        max_tokens=1024
    )
    
    subtasks = json.loads(plan_response.content[0].text)
    print(f"  Orchestrator created {len(subtasks)} subtasks")
    
    # Step 2: Parallel execution (workers run simultaneously)
    print("  Workers running in parallel...")
    worker_results = await asyncio.gather(*[
        worker_agent(st["role"], st["task"])
        for st in subtasks
    ])
    
    # Step 3: Synthesis (orchestrator combines results)
    print("  Orchestrator synthesizing results...")
    combined = "\n\n".join(
        f"[{st['role'].upper()}]:\n{result}"
        for st, result in zip(subtasks, worker_results)
    )
    
    final = await async_client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are a senior director. Synthesize worker reports into a coherent, actionable final output.",
        messages=[{"role": "user", "content": f"Goal: {goal}\n\nWorker Reports:\n{combined}"}],
        max_tokens=3000
    )
    
    return final.content[0].text

# Example
report = asyncio.run(orchestrator(
    "Create a go-to-market strategy for a green hydrogen distribution company targeting industrial users in India"
))
```

### Recursive Hierarchy (Sub-Orchestrators)
For very complex tasks, workers themselves become orchestrators:

```python
async def recursive_orchestrator(task: str, depth: int = 0, max_depth: int = 2) -> str:
    """
    If task is complex enough, spawn sub-orchestrators.
    Otherwise, just execute directly.
    """
    MAX_INDENT = "  " * depth
    
    # Check if this task needs to be broken down further
    if depth < max_depth:
        complexity_check = await async_client.messages.create(
            model="claude-haiku-4-5-20251001",
            system='Is this task complex enough to require multiple subtasks? Return only "yes" or "no".',
            messages=[{"role": "user", "content": task}],
            max_tokens=5
        )
        
        if "yes" in complexity_check.content[0].text.lower():
            print(f"{MAX_INDENT}Spawning sub-orchestrator for: {task[:50]}...")
            return await orchestrator(task)  # recursively orchestrate
    
    # Simple task — just execute directly
    print(f"{MAX_INDENT}Executing directly: {task[:50]}...")
    return await worker_agent("expert assistant", task)
```

---

# LEVEL 10 — DAG Pipelines (Directed Acyclic Graph)
> *"Complex dependencies. Each node runs as soon as its dependencies are met."*

```
[A] ──────────────────────→ [D]
[B] ──→ [C] ──────────────→ [D] ──→ [F]
[B] ───────────────→ [E] ──→ [F]
```

### What It Is
A **Directed Acyclic Graph (DAG)** lets you define arbitrary dependencies between tasks. Node D runs when A and C are done. Node F runs when D and E are done. Nodes without dependencies run immediately in parallel. This is the most powerful static topology.

### Visual Example: Content Production DAG
```
[Fetch Brief] ──→ [Research Topic A] ──────────────────┐
               └→ [Research Topic B] ─────────────────→ [Synthesize Research]
               └→ [Research Topic C] ──────────────────┘      ↓
                                                         [Write Draft]
[Fetch Brand Guide] ──→ [Extract Style Rules] ──────→ [Apply Style] ← [Write Draft]
[Fetch Competitor Posts] ─→ [Extract Differentiators] → [Apply Style]
                                                               ↓
                                                       [Final Review]
```

### Code — DAG Executor
```python
import asyncio
from dataclasses import dataclass, field
from typing import Callable, Awaitable

@dataclass
class DAGNode:
    id: str
    fn: Callable[..., Awaitable[str]]   # async function to run
    deps: list[str] = field(default_factory=list)  # node IDs this depends on

class DAGExecutor:
    def __init__(self, nodes: list[DAGNode]):
        self.nodes = {n.id: n for n in nodes}
        self.results: dict[str, str] = {}
    
    async def run(self, inputs: dict = {}) -> dict:
        """Execute all nodes, respecting dependencies. Nodes ready to run go immediately."""
        
        self.results = dict(inputs)
        pending = set(self.nodes.keys()) - set(inputs.keys())
        running: dict[str, asyncio.Task] = {}
        
        while pending or running:
            # Find nodes whose dependencies are all satisfied
            ready = [
                nid for nid in pending
                if all(dep in self.results for dep in self.nodes[nid].deps)
                and nid not in running
            ]
            
            # Launch all ready nodes in parallel
            for nid in ready:
                pending.remove(nid)
                node = self.nodes[nid]
                dep_results = {dep: self.results[dep] for dep in node.deps}
                running[nid] = asyncio.create_task(node.fn(**dep_results))
            
            if not running:
                break
            
            # Wait for the first task to complete, then loop again
            done, _ = await asyncio.wait(running.values(), return_when=asyncio.FIRST_COMPLETED)
            
            for task in done:
                nid = next(k for k, v in running.items() if v == task)
                self.results[nid] = await task
                del running[nid]
                print(f"  ✓ Node '{nid}' completed")
        
        return self.results

# Define your DAG for a content pipeline
async def run_content_dag(brief: str, brand_guide: str):
    
    # Define nodes as async functions
    async def research_market(**_):
        return await async_agent("Market researcher", f"Research market trends for: {brief}")
    
    async def research_audience(**_):
        return await async_agent("Audience analyst", f"Research target audience for: {brief}")
    
    async def extract_style(brand_guide_input: str, **_):
        return await async_agent("Brand strategist", f"Extract writing style rules from:\n{brand_guide_input}")
    
    async def synthesize(research_market: str, research_audience: str, **_):
        return await async_agent("Research synthesizer", f"Combine:\n{research_market}\n\n{research_audience}")
    
    async def write_draft(synthesize: str, extract_style: str, **_):
        return await async_agent("Content writer", f"Write using:\nResearch: {synthesize}\nStyle: {extract_style}")
    
    async def final_review(write_draft: str, **_):
        return await async_agent("Editor", f"Final review and polish:\n{write_draft}")
    
    # Build DAG
    dag = DAGExecutor([
        DAGNode("research_market",    research_market,    deps=[]),
        DAGNode("research_audience",  research_audience,  deps=[]),
        DAGNode("extract_style",      extract_style,      deps=["brand_guide_input"]),
        DAGNode("synthesize",         synthesize,         deps=["research_market", "research_audience"]),
        DAGNode("write_draft",        write_draft,        deps=["synthesize", "extract_style"]),
        DAGNode("final_review",       final_review,       deps=["write_draft"]),
    ])
    
    results = await dag.run(inputs={"brand_guide_input": brand_guide})
    return results["final_review"]
```

---

# LEVEL 11 — Peer-to-Peer Multi-Agent Networks
> *"Agents communicate freely with each other. No strict hierarchy."*

```
[Agent A] ←──────────→ [Agent B]
    ↑                       ↑
    └────── [Agent C] ──────┘
               ↕
          [Agent D]
```

### What It Is
Agents are peers on a network. Any agent can send a message to any other agent. There's no fixed orchestrator. Agents self-coordinate to complete tasks.

### Communication Patterns
| Pattern | How | When to Use |
|---|---|---|
| **Blackboard** | Agents read/write to shared state store | Async collaboration, no direct communication needed |
| **Direct Messaging** | Agent A calls Agent B's endpoint directly | Clear agent-to-agent delegation |
| **Pub/Sub** | Agents publish to topics; others subscribe | Loosely coupled, event-driven coordination |
| **Contract Net** | Orchestrator announces task; agents bid; best bid wins | Dynamic task allocation |

### Code — Blackboard Architecture
```python
import asyncio
from typing import Any
from datetime import datetime

class Blackboard:
    """Shared memory space all agents read from and write to."""
    
    def __init__(self):
        self._data: dict[str, Any] = {}
        self._log: list[dict] = []
        self._lock = asyncio.Lock()
    
    async def write(self, key: str, value: Any, agent: str):
        async with self._lock:
            self._data[key] = value
            self._log.append({"time": datetime.now().isoformat(), "agent": agent, "key": key})
            print(f"  [{agent}] wrote: {key}")
    
    async def read(self, key: str) -> Any:
        return self._data.get(key)
    
    async def wait_for(self, key: str, poll_interval: float = 0.1) -> Any:
        """Block until a key appears on the blackboard."""
        while key not in self._data:
            await asyncio.sleep(poll_interval)
        return self._data[key]

async def researcher_agent(bb: Blackboard, topic: str):
    """Runs first. Posts findings to blackboard."""
    result = await async_agent("Research specialist", f"Research: {topic}")
    await bb.write("research", result, "researcher")

async def analyst_agent(bb: Blackboard):
    """Waits for research, then analyzes."""
    research = await bb.wait_for("research")
    result = await async_agent("Data analyst", f"Analyze this research:\n{research}")
    await bb.write("analysis", result, "analyst")

async def writer_agent(bb: Blackboard):
    """Waits for analysis, then writes."""
    analysis = await bb.wait_for("analysis")
    result = await async_agent("Technical writer", f"Write a report from:\n{analysis}")
    await bb.write("report", result, "writer")

async def fact_checker_agent(bb: Blackboard):
    """Waits for report, then fact-checks."""
    report = await bb.wait_for("report")
    result = await async_agent("Fact checker", f"Check this for factual accuracy:\n{report}")
    await bb.write("verified_report", result, "fact_checker")

async def peer_agent_system(topic: str) -> str:
    bb = Blackboard()
    
    # All agents launch simultaneously; they self-coordinate via the blackboard
    await asyncio.gather(
        researcher_agent(bb, topic),
        analyst_agent(bb),
        writer_agent(bb),
        fact_checker_agent(bb)
    )
    
    return await bb.read("verified_report")
```

---

# LEVEL 12 — Event-Driven Agent Systems
> *"Agents sleep until something happens. Then they wake, act, and go back to sleep."*

```
[Event Stream] → [Event Router] → [Agent Wakes] → [Executes] → [Publishes New Event]
                                                                         ↓
                                                              [Other Agents React]
```

### What It Is
Agents are not running constantly — they react to **events**. An event (user message, webhook, timer, file change, market data) triggers the right agent, which acts and may produce new events that trigger other agents.

### Code — Event-Driven Agent
```python
import asyncio
from dataclasses import dataclass, field
from typing import Callable, Awaitable
from enum import Enum

class EventType(str, Enum):
    USER_MESSAGE    = "user_message"
    FILE_UPLOADED   = "file_uploaded"
    SCHEDULE_TICK   = "schedule_tick"
    AGENT_COMPLETE  = "agent_complete"
    ERROR           = "error"

@dataclass
class Event:
    type: EventType
    payload: dict
    source: str = "system"

class EventBus:
    def __init__(self):
        self._handlers: dict[EventType, list[Callable]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
    
    def on(self, event_type: EventType):
        """Decorator to register an event handler."""
        def decorator(fn: Callable):
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(fn)
            return fn
        return decorator
    
    async def emit(self, event: Event):
        await self._queue.put(event)
    
    async def run(self):
        """Continuously process events from the queue."""
        while True:
            event = await self._queue.get()
            handlers = self._handlers.get(event.type, [])
            await asyncio.gather(*[h(event, self) for h in handlers])

bus = EventBus()

@bus.on(EventType.FILE_UPLOADED)
async def handle_file_upload(event: Event, bus: EventBus):
    """Wakes up when a file is uploaded, processes it."""
    file_path = event.payload["path"]
    print(f"File uploaded: {file_path} — processing...")
    
    content = extract_text(file_path)  # OCR / PDF parse
    summary = await async_agent("Document analyst", f"Summarize: {content}")
    
    # Publish a new event (triggers downstream agents)
    await bus.emit(Event(
        type=EventType.AGENT_COMPLETE,
        payload={"result": summary, "file": file_path},
        source="file_processor"
    ))

@bus.on(EventType.AGENT_COMPLETE)
async def handle_completion(event: Event, bus: EventBus):
    """Wakes up when any agent completes, routes the result."""
    if event.source == "file_processor":
        await send_telegram_notification(event.payload["result"])

@bus.on(EventType.SCHEDULE_TICK)
async def daily_report_agent(event: Event, bus: EventBus):
    """Wakes up on a timer — generates daily report."""
    if event.payload.get("time") == "09:00":
        report = await async_agent("Report writer", "Generate today's hydrogen market briefing")
        await send_email(report)

# Start the event loop
asyncio.run(bus.run())
```

---

# LEVEL 13 — Full Real-World System: Combining All Patterns
> *"This is what production AI systems actually look like."*

```
                    ┌─────────────────────────────────────────┐
                    │        USER INTERFACE LAYER              │
                    │   (Telegram Bot / Web App / API)         │
                    └─────────────┬──────────────┬────────────┘
                                  │              │
                            [Event Bus]    [HTTP Gateway]
                                  │              │
                    ┌─────────────▼──────────────▼────────────┐
                    │          ROUTING LAYER                   │
                    │   LLM Router → classifies intent         │
                    └──┬──────────┬──────────┬─────────────────┘
                       │          │          │
              ┌────────▼──┐ ┌─────▼───┐ ┌───▼──────┐
              │ RESEARCH  │ │  CODE   │ │  CONTENT │
              │  CLUSTER  │ │ CLUSTER │ │  CLUSTER │
              │           │ │         │ │          │
              │ ┌────────┐ │ │┌──────┐│ │ ┌──────┐ │
              │ │RAG     │ │ ││Code  ││ │ │Writer│ │
              │ │Search  │ │ ││Agent ││ │ │Critic│ │
              │ │Analyst │ │ ││Tests ││ │ │Router│ │
              │ └────────┘ │ │└──────┘│ │ └──────┘ │
              └─────┬──────┘ └──┬─────┘ └────┬─────┘
                    │           │             │
                    └─────┬─────┘─────────────┘
                          │
                   ┌──────▼──────┐
                   │  SYNTHESIS  │
                   │    AGENT    │
                   └──────┬──────┘
                          │
                   ┌──────▼──────────────────────────────┐
                   │        MEMORY + PERSISTENCE          │
                   │  PostgreSQL | Redis | Vector DB      │
                   └─────────────────────────────────────┘
```

### The Patterns Used at Each Layer
| Layer | Patterns Applied |
|---|---|
| Input handling | Multi-modal series (Level 3) |
| Intent routing | Conditional branching (Level 7) |
| Research cluster | Parallel fan-out + RAG (Level 5 + 6) |
| Code cluster | Test-fix loop (Level 8) |
| Content cluster | Generator-critic loop + parallel voting (Level 8 + 5) |
| Cluster execution | Hierarchical orchestration (Level 9) |
| Cross-cluster | DAG dependency management (Level 10) |
| Result delivery | Series pipeline (Level 4) |
| Agent coordination | Event-driven reactions (Level 12) |

---

# Quick Reference: Pattern Selection Guide

| Your Situation | Use This Pattern | Level |
|---|---|---|
| Simple one-off question | Text-to-text | 1 |
| Need to look things up or do actions | Series tool use | 2 |
| Mixed text/image/audio input | Multi-modal series | 3 |
| Multiple specialists in a production line | Agent chain | 4 |
| Independent tasks that can run at once | Parallel fan-out | 5 |
| Complex flow with both sequential and independent steps | Hybrid series/parallel | 6 |
| Different inputs need different handlers | Conditional routing | 7 |
| Output quality isn't good enough first try | Generator-critic loop | 8 |
| Large task with many subtasks | Hierarchical orchestration | 9 |
| Complex dependencies between tasks | DAG pipeline | 10 |
| Agents need to collaborate freely | Peer-to-peer / blackboard | 11 |
| Triggered by external events (webhooks, timers) | Event-driven | 12 |
| All of the above in production | Full system architecture | 13 |

---

# Code Utilities: Reusable Async Agent Primitives

```python
# ── Core async agent call ────────────────────────────────────────
async def call(system: str, prompt: str, model: str = "claude-sonnet-4-20250514") -> str:
    from anthropic import AsyncAnthropic
    r = await AsyncAnthropic().messages.create(
        model=model, max_tokens=2048,
        system=system, messages=[{"role": "user", "content": prompt}]
    )
    return r.content[0].text

# ── Run tasks in parallel ────────────────────────────────────────
async def parallel(*coroutines) -> list:
    return list(await asyncio.gather(*coroutines))

# ── Run tasks in series, threading output forward ────────────────
async def series(input: str, *fns) -> str:
    result = input
    for fn in fns:
        result = await fn(result)
    return result

# ── Best-of-N: run N times, pick best ────────────────────────────
async def best_of(n: int, task_fn, judge_fn) -> str:
    candidates = await parallel(*[task_fn() for _ in range(n)])
    scores = await parallel(*[judge_fn(c) for c in candidates])
    return candidates[scores.index(max(scores))]

# ── Retry with exponential backoff ───────────────────────────────
import tenacity
@tenacity.retry(stop=tenacity.stop_after_attempt(3), wait=tenacity.wait_exponential())
async def resilient_call(system: str, prompt: str) -> str:
    return await call(system, prompt)

# ── Rate-limited parallel execution (N at a time) ────────────────
async def parallel_limited(coroutines: list, limit: int = 5) -> list:
    semaphore = asyncio.Semaphore(limit)
    async def guarded(coro):
        async with semaphore:
            return await coro
    return list(await asyncio.gather(*[guarded(c) for c in coroutines]))
```

---

*The architecture of your system determines what's possible. Start at Level 1. Add complexity only when the previous level can't handle your use case.*
