# 🧠 AIGrowth: The Complete AI Agent Integration Roadmap
> From a single API call → to fully autonomous, self-orchestrating multi-agent systems.
> Every level. Every route. No gaps.

---

## How to Use This Document

Each level builds on the previous one. You don't need to finish one entirely before moving to the next, but the concepts compound. Real-world examples are tagged throughout.

**Legend:**
- 🔰 Beginner-safe
- ⚙️ Requires some engineering
- 🔥 Advanced
- 💀 Expert / Production-grade
---

# LEVEL 1 — Single-Shot API Calls
> *"I send a message, I get a response."*
**Difficulty:** 🔰

This is the entry point. You're treating the AI like a smarter Google search — one input, one output, no memory, no tools.

### What It Is
You make an HTTP POST request to an LLM provider's endpoint (OpenAI, Anthropic, Groq, etc.), send a prompt in the body, and receive a text response back.

### How It Works
```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Summarize what Green Hydrogen is in 3 sentences."}
    ]
)

print(response.content[0].text)
```

### Key Concepts
- **Model** — which LLM you're calling (GPT-4o, Claude Sonnet, Llama 3, Gemini, etc.)
- **Max tokens** — how long the reply can be
- **Temperature** — 0.0 = deterministic/precise, 1.0 = creative/random
- **API Key** — your credential for billing and access

### Practical Examples
- Auto-summarize a research paper PDF (you extract text, you send it)
- Classify user messages in a chatbot
- Generate a single piece of content (email, caption, description)

### Providers to Know
| Provider | Models | Free Tier? | Speed |
|---|---|---|---|
| **Anthropic** | Claude Sonnet, Opus, Haiku | No | Fast |
| **OpenAI** | GPT-4o, o1, o3 | Limited | Fast |
| **Groq** | Llama 3, Mixtral | Yes (rate-limited) | Extremely Fast |
| **Google** | Gemini 1.5/2.0 | Yes | Fast |
| **Together AI** | Many open-source | Pay-per-use | Fast |

### What You Can Build
- A simple summarization script
- A single-turn Q&A bot
- A content generator that takes a topic and outputs a blog intro

---

# LEVEL 2 — Prompt Engineering & Conversation Management
> *"I control how the AI thinks, not just what it answers."*
**Difficulty:** 🔰

One API call with a bad prompt gives bad results. This level is about becoming the architect of how the model reasons.

### System Prompts
The system prompt is the AI's identity, constraints, and context. It runs before every user message.

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="""You are a technical analyst specializing in Green Hydrogen
    and electrolysis. Always respond with data-backed analysis.
    Format responses with: Summary | Key Metrics | Risk Factors.""",
    messages=[
        {"role": "user", "content": "Analyze the LCOE for a 100 MW PEM electrolyzer plant."}
    ]
)
```

### Multi-Turn Conversations
You manage memory manually by appending to the message history:

```python
history = []

def chat(user_input):
    history.append({"role": "user", "content": user_input})
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=history
    )
    
    assistant_reply = response.content[0].text
    history.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply
```

### Prompt Patterns to Master
| Pattern | What It Does | Example Use |
|---|---|---|
| **Chain-of-Thought** | Forces step-by-step reasoning | `"Think step by step before answering."` |
| **Few-Shot** | Teach by example in the prompt | Show 2-3 input/output examples before the real task |
| **Role Prompting** | Assign a persona | `"You are a senior process engineer at an ammonia plant."` |
| **Output Formatting** | Control structure | `"Respond only in JSON with keys: title, summary, risk_score"` |
| **Negative Constraints** | What NOT to do | `"Do not use bullet points. Never guess if uncertain."` |
| **Delimiters** | Separate instruction from data | Use `<document>`, `<context>`, `<task>` XML tags |

### Context Window Management
Every model has a token limit (how much text it can "see" at once). When conversations get long:
- Summarize old history and replace it
- Use sliding window (keep only last N turns)
- Store summaries in a database and inject selectively

### What You Can Build
- A domain-expert chatbot (e.g., green energy Q&A assistant)
- A structured output generator for reports
- A persona-based customer service agent

---

# LEVEL 3 — Running Local Models
> *"I own my AI. No API key, no cloud, no per-token billing."*
**Difficulty:** ⚙️

You run the model on your own machine or server. Zero data leaves your environment.

### Why Go Local?
- **Privacy** — sensitive data (industrial data, client specs) never leaves your machine
- **Cost** — no per-call billing
- **Speed** — no network latency for small models
- **Control** — fine-tune, modify, or run quantized versions

### Tools for Running Local Models
#### Ollama (Easiest)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull and run a model
ollama pull llama3.2
ollama run llama3.2

# Use it via API (same format as OpenAI)
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "Hello"}]
}'
```

#### LM Studio (GUI, Windows-friendly)
- Download from lmstudio.ai
- Browse and download GGUF models from Hugging Face
- Runs a local OpenAI-compatible server on `http://localhost:1234`
- Your existing Python code works with zero changes — just change the base URL

#### vLLM (Production GPU Inference)
```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Meta-Llama-3-8B-Instruct
```

### Connecting Local Models to Your Python Code
Since Ollama and LM Studio use OpenAI-compatible APIs:
```python
from openai import OpenAI  # or use httpx directly

client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama
    api_key="ollama"  # any string, ignored locally
)

response = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "Explain electrolysis."}]
)
```

### Model Selection Guide
| Model | Size | Best For | RAM Required |
|---|---|---|---|
| **Llama 3.2 3B** | Small | Quick classification, summarization | 4GB |
| **Llama 3.1 8B** | Medium | General tasks, coding | 8GB |
| **Mistral 7B** | Medium | Instruction following | 8GB |
| **Qwen2.5 14B** | Large | Complex reasoning, multilingual | 16GB |
| **DeepSeek-Coder** | Medium | Code generation | 8GB |
| **Phi-3 Mini** | Tiny | Edge deployment, fast inference | 3GB |

### Quantization (Running Big Models on Small Hardware)
- **Q4_K_M** — best quality/size trade-off (recommended)
- **Q8_0** — near-full quality, larger file
- **Q2_K** — tiny but noticeably degraded

A 70B model at Q4 requires ~40GB RAM. An 8B model at Q4 needs ~5GB.

### What You Can Build
- A private document Q&A system (feed internal reports)
- A self-hosted Telegram bot with no API costs
- An offline coding assistant
- A data processing pipeline for sensitive industrial data

---

# LEVEL 4 — Tool Calling / Function Calling
> *"The AI doesn't just respond — it calls real functions."*
**Difficulty:** ⚙️

This is where AI goes from answering questions to *doing things*. You define functions; the model decides when and how to call them.

### What Is Tool Calling?
You describe a set of tools (Python functions) to the model. When the user asks something that requires a tool, the model outputs a structured JSON call instead of plain text — your code executes it, returns the result, and the model continues.

### The Loop
```
User: "What's the current price of hydrogen futures?"
  → Model decides: I need the `get_market_price` tool
  → Model outputs: {"tool": "get_market_price", "args": {"asset": "hydrogen"}}
  → Your code runs the function
  → Result returned to model
  → Model: "Hydrogen futures are currently at $X per kg."
```

### Implementation (Anthropic)
```python
import anthropic
import json

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
]

# Step 1: Send message with tools
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in New Delhi?"}]
)

# Step 2: Check if model wants to use a tool
if response.stop_reason == "tool_use":
    tool_use = next(b for b in response.content if b.type == "tool_use")
    tool_name = tool_use.name
    tool_input = tool_use.input
    
    # Step 3: Execute your actual function
    if tool_name == "get_weather":
        result = fetch_weather_api(tool_input["location"])  # your real function
    
    # Step 4: Return result to model and get final answer
    final_response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=[
            {"role": "user", "content": "What's the weather in New Delhi?"},
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tool_use.id, "content": str(result)}
            ]}
        ]
    )
```

### Types of Tools You Can Give an AI
| Category | Examples |
|---|---|
| **Data Retrieval** | Database queries, REST API calls, web scraping |
| **File Operations** | Read/write files, parse PDFs, process images |
| **Computation** | Run Python scripts, execute calculations, call simulators |
| **Communication** | Send emails, post to Slack/Telegram, trigger webhooks |
| **System Control** | Run shell commands, control browsers, interact with UIs |
| **External Services** | Search the web, call third-party APIs |

### Parallel Tool Calling
Modern models can call multiple tools at the same time:
```
User: "Summarize the latest news on hydrogen AND check our plant's energy usage."
  → Model calls: [fetch_news(topic="hydrogen"), get_plant_metrics(plant_id=1)]
  → Both run concurrently
  → Model synthesizes both results into one response
```

### What You Can Build
- An AI that can search the web, read a URL, and summarize findings
- A financial bot that calls live stock/commodity APIs
- An automation agent that reads emails and triggers actions

---

# LEVEL 5 — Multi-Tool Pipelines (Your Telegram Bot Level)
> *"Chaining OCR + STT + LLM + Storage = One intelligent system."*
**Difficulty:** ⚙️

This is what you've already built with Omni. Instead of one AI doing one thing, you're orchestrating a **pipeline** of specialized AI models and services.

### The Architecture
```
[User Input] → [Input Router] → [Specialized Processor] → [LLM Core] → [Output Handler]
                    |
              ┌─────┴──────┐
              ↓            ↓
          Image?         Audio?
          (OCR/Vision)   (STT/Whisper)
              ↓            ↓
         Extracted     Transcribed
           Text          Text
              └─────┬──────┘
                    ↓
               [LLM Core]
                    ↓
             [Output Router]
              ┌─────┴──────┐
              ↓            ↓
           Text          File
          Response     (gofile.io)
```

### Key Components in a Real Pipeline

#### 1. Speech-to-Text (STT)
```python
import openai

def transcribe_audio(audio_file_path: str) -> str:
    client = openai.OpenAI()
    with open(audio_file_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return transcript.text

# Local alternative: faster-whisper
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu")
segments, _ = model.transcribe("audio.mp3")
text = " ".join(s.text for s in segments)
```

#### 2. Optical Character Recognition (OCR)
```python
# Cloud: Google Vision API
from google.cloud import vision

def extract_text_from_image(image_path: str) -> str:
    client = vision.ImageAnnotatorClient()
    with open(image_path, "rb") as f:
        image = vision.Image(content=f.read())
    response = client.text_detection(image=image)
    return response.text_annotations[0].description

# Local: pytesseract
import pytesseract
from PIL import Image
text = pytesseract.image_to_string(Image.open("document.png"))

# Best local option: surya (modern, multilingual)
# pip install surya-ocr
```

#### 3. Vision / Image Understanding
```python
# Send image directly to Claude or GPT-4o
import base64

with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
            {"type": "text", "text": "What does this P&ID diagram show?"}
        ]
    }]
)
```

#### 4. Text-to-Speech (TTS)
```python
# OpenAI TTS
response = client.audio.speech.create(
    model="tts-1", voice="nova", input="Here is your report summary."
)
response.stream_to_file("output.mp3")

# Local: Coqui TTS, Piper TTS, Kokoro
```

#### 5. Image Generation
```python
# DALL-E
response = client.images.generate(
    model="dall-e-3",
    prompt="A futuristic hydrogen electrolyzer plant at sunset, photorealistic",
    size="1024x1024"
)

# Via Stable Diffusion API (like your Telegram bot uses Nvidia's API)
# Or local: ComfyUI, Automatic1111
```

### Pipeline Orchestration Pattern (Your Bot's Pattern)
```python
# Aiogram FSM-based multi-modal handler
async def process_user_input(message: Message, state: FSMContext):
    
    if message.content_type == ContentType.VOICE:
        audio_path = await download_voice(message)
        text = await transcribe_audio(audio_path)          # STT
        
    elif message.content_type == ContentType.PHOTO:
        image_path = await download_photo(message)
        text = await extract_text_from_image(image_path)   # OCR or Vision
        
    elif message.content_type == ContentType.TEXT:
        text = message.text
    
    # Common path: LLM processing
    response = await call_llm(text, context=await state.get_data())
    
    # Route output
    if len(response) > 4096:
        file_url = await upload_to_gofile(response)         # File upload
        await message.answer(f"Full response: {file_url}")
    else:
        await message.answer(response)
```

### Async & Queue Architecture
For production pipelines (like your Celery + Redis setup):
```
[Telegram Update] → [Aiogram Handler] → [Celery Task Queue (Redis)]
                                                   ↓
                                        [Worker: OCR / STT / LLM]
                                                   ↓
                                        [Result Store (PostgreSQL)]
                                                   ↓
                                        [Telegram Reply via Bot API]
```

### What You Can Build
- A voice note → AI summary → Telegram reply bot (done ✅)
- A document → structured data extractor pipeline
- An image → captioned social post automation tool
- A PDF report → audio briefing generator

---

# LEVEL 6 — RAG: Retrieval-Augmented Generation
> *"The AI knows YOUR documents, not just its training data."*
**Difficulty:** ⚙️

RAG lets your AI answer questions about data it was never trained on — your PDFs, docs, databases — by retrieving relevant chunks at query time.

### Why RAG vs. Fine-Tuning?
- Fine-tuning changes the model's *behavior*; RAG changes the model's *knowledge*
- RAG is cheaper, faster to update, and doesn't require training
- Perfect for internal docs, company wikis, technical manuals

### The RAG Pipeline
```
                    ┌── INDEXING (one-time) ──┐
                    │                         │
[Your Documents] → [Chunk Text] → [Embed Chunks] → [Store in Vector DB]

                    ┌── QUERYING (every request) ──┐
[User Query] → [Embed Query] → [Search Vector DB] → [Top-K Chunks]
                                                          ↓
                                             [LLM + Chunks as Context]
                                                          ↓
                                              [Grounded Answer]
```

### Implementation with ChromaDB (Local)
```python
import chromadb
from chromadb.utils import embedding_functions
import anthropic

# Setup
chroma_client = chromadb.Client()
ef = embedding_functions.DefaultEmbeddingFunction()  # or OpenAI embeddings
collection = chroma_client.create_collection("my_docs", embedding_function=ef)

# INDEXING: Add your documents
documents = [
    "Green hydrogen is produced by electrolysis powered by renewable energy...",
    "PEM electrolyzers operate at high current densities of up to 3 A/cm²...",
    "LCOH for green hydrogen varies between $3-8/kg depending on electricity costs..."
]

collection.add(
    documents=documents,
    ids=["doc1", "doc2", "doc3"]
)

# QUERYING: Find relevant chunks
def rag_query(user_question: str) -> str:
    results = collection.query(query_texts=[user_question], n_results=3)
    context = "\n\n".join(results["documents"][0])
    
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system=f"Answer based ONLY on this context:\n\n{context}",
        messages=[{"role": "user", "content": user_question}]
    )
    return response.content[0].text

answer = rag_query("What is the typical LCOH for green hydrogen?")
```

### Embedding Models
| Model | Where | Cost | Quality |
|---|---|---|---|
| `text-embedding-3-small` | OpenAI API | Low | Good |
| `text-embedding-3-large` | OpenAI API | Medium | Best |
| `nomic-embed-text` | Local (Ollama) | Free | Good |
| `mxbai-embed-large` | Local (Ollama) | Free | Very Good |

### Vector Databases
| DB | Type | Best For |
|---|---|---|
| **ChromaDB** | Local / Embedded | Small projects, prototyping |
| **Pinecone** | Cloud | Managed, scalable |
| **Weaviate** | Self-hostable | Production with metadata |
| **Qdrant** | Self-hostable | High performance, Rust-based |
| **pgvector** | PostgreSQL extension | If you're already using Postgres |

### Advanced RAG Patterns
- **Hybrid Search** — combine vector similarity + keyword search (BM25)
- **Re-ranking** — after retrieving, use a cross-encoder to re-score results
- **HyDE (Hypothetical Document Embeddings)** — ask the LLM to generate a "fake" ideal answer first, then embed that for retrieval
- **Parent-Child Chunking** — store small chunks for retrieval, but send larger parent chunks to the LLM
- **Graph RAG** — build a knowledge graph from your docs, traverse relationships at query time

### What You Can Build
- A private Q&A bot trained on your company's technical documents
- A green hydrogen research assistant trained on your LCOH models
- A "second brain" over your Notion/Obsidian notes
- A customer support bot trained on your product documentation

---

# LEVEL 7 — MCP Servers (Model Context Protocol)
> *"Standardized, pluggable tool connections that any AI can use."*
**Difficulty:** ⚙️

MCP is a protocol (invented by Anthropic) that standardizes how AI models connect to external tools and data sources. Instead of writing custom tool wiring for every app, you write an MCP server once and any MCP-compatible AI client can use it.

### The Analogy
Think of MCP like **USB-C** for AI tools. Before USB-C, every device had its own connector. MCP is the universal connector between AI models and external systems.

### Without MCP vs. With MCP
```
WITHOUT MCP:
App A → Custom Tool Wiring A → Database
App B → Custom Tool Wiring B → Database
App C → Custom Tool Wiring C → Database

WITH MCP:
App A ──┐
App B ──┤→ [MCP Server: Database] → Database
App C ──┘
```

### MCP Architecture
```
[MCP Client (Claude, your app)]
        ↕  (JSON-RPC over stdio or HTTP/SSE)
[MCP Server]
  ├── Tools (functions the AI can call)
  ├── Resources (data the AI can read)
  └── Prompts (reusable prompt templates)
```

### Writing a Simple MCP Server (Python)
```python
# pip install mcp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

app = Server("my-hydrogen-tools")

@app.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="get_electrolyzer_efficiency",
            description="Returns efficiency % for a given electrolyzer type and load",
            inputSchema={
                "type": "object",
                "properties": {
                    "electrolyzer_type": {"type": "string", "enum": ["PEM", "AEL", "SOEC"]},
                    "load_percent": {"type": "number"}
                },
                "required": ["electrolyzer_type", "load_percent"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_electrolyzer_efficiency":
        eff_type = arguments["electrolyzer_type"]
        load = arguments["load_percent"]
        # Your actual business logic here
        efficiency = calculate_efficiency(eff_type, load)
        return [types.TextContent(type="text", text=f"{efficiency:.1f}%")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

import asyncio
asyncio.run(main())
```

### Connecting MCP to Claude Desktop
```json
// ~/.claude/claude_desktop_config.json
{
  "mcpServers": {
    "hydrogen-tools": {
      "command": "python",
      "args": ["/path/to/your/mcp_server.py"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/docs"]
    }
  }
}
```

### Pre-Built MCP Servers You Can Use Today
| Server | What It Gives AI Access To |
|---|---|
| `@modelcontextprotocol/server-filesystem` | Read/write local files |
| `@modelcontextprotocol/server-github` | GitHub repos, PRs, issues |
| `@modelcontextprotocol/server-postgres` | Query your PostgreSQL DB |
| `@modelcontextprotocol/server-brave-search` | Web search |
| `mcp-server-sqlite` | Local SQLite databases |
| `@modelcontextprotocol/server-slack` | Send/read Slack messages |
| `mcp-server-redis` | Redis key-value operations |

### MCP vs. Tool Calling
| | Tool Calling | MCP |
|---|---|---|
| **Scope** | Single application | Universal, any client |
| **Discovery** | You hardcode tools | Client auto-discovers tools |
| **Reusability** | One app | Any MCP-compatible app |
| **Standard** | OpenAI/Anthropic specific | Open protocol |

### What You Can Build
- A single MCP server exposing your green hydrogen data models — usable from Claude Desktop, your Telegram bot, and your Next.js app simultaneously
- An MCP server wrapping your PostgreSQL DB so any AI client can query it with natural language
- A private MCP registry for your team's tools

---

# LEVEL 8 — Agent Frameworks
> *"Stop wiring everything manually. Use a framework."*
**Difficulty:** 🔥

Frameworks abstract the repetitive parts of building agents — conversation history management, tool routing, error handling, retries, and multi-step planning.

### The Big Frameworks

#### LangChain / LangGraph (Most Popular)
```python
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate

@tool
def get_hydrogen_price(region: str) -> str:
    """Get current green hydrogen price for a region."""
    # your logic
    return f"$4.50/kg in {region}"

llm = ChatAnthropic(model="claude-sonnet-4-20250514")
tools = [get_hydrogen_price]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a green energy market analyst."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = executor.invoke({"input": "What's the hydrogen price in India?"})
```

#### LangGraph (Stateful, Graph-Based Agents)
LangGraph models agent behavior as a **state machine graph** — nodes are actions, edges are transitions. Best for complex, conditional workflows.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    messages: list
    next_step: str

# Define nodes (actions)
def analyze(state):
    # call LLM
    return {"next_step": "research" if needs_research else "respond"}

def research(state):
    # call search tool
    return {"messages": state["messages"] + [search_result]}

def respond(state):
    # generate final answer
    return {"messages": state["messages"] + [final_answer]}

# Build graph
graph = StateGraph(AgentState)
graph.add_node("analyze", analyze)
graph.add_node("research", research)
graph.add_node("respond", respond)
graph.add_edge("analyze", "research")  # conditional
graph.add_edge("research", "respond")
graph.add_edge("respond", END)
```

#### CrewAI (Role-Based Multi-Agent)
```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Green Hydrogen Researcher",
    goal="Find the latest cost reduction trends in green hydrogen",
    backstory="Expert in electrolyzer technology and renewable energy economics",
    llm=llm,
    tools=[web_search_tool, arxiv_tool]
)

writer = Agent(
    role="Technical Report Writer",
    goal="Write a clear executive summary from research findings",
    backstory="Skilled at translating technical findings for business audiences",
    llm=llm
)

research_task = Task(description="Research latest LCOH trends", agent=researcher)
write_task = Task(description="Write executive summary", agent=writer)

crew = Crew(agents=[researcher, writer], tasks=[research_task, write_task])
result = crew.kickoff()
```

#### Microsoft AutoGen (Conversational Multi-Agent)
AutoGen agents talk to each other in a conversation loop until the task is complete.

```python
import autogen

config = [{"model": "claude-sonnet-4-20250514", "api_key": "..."}]

assistant = autogen.AssistantAgent("assistant", llm_config={"config_list": config})
user_proxy = autogen.UserProxyAgent("user_proxy", code_execution_config={"work_dir": "."})

user_proxy.initiate_chat(
    assistant,
    message="Write and test a Python function that calculates LCOH given input parameters."
)
# The two agents converse until the code works
```

### Framework Comparison
| Framework | Best For | Learning Curve | Flexibility |
|---|---|---|---|
| **LangChain** | Quick prototypes, lots of integrations | Medium | High |
| **LangGraph** | Complex stateful workflows | High | Very High |
| **CrewAI** | Role-based multi-agent teams | Low | Medium |
| **AutoGen** | Code generation, iterative tasks | Low-Medium | Medium |
| **Haystack** | RAG-heavy pipelines | Medium | High |
| **Pydantic AI** | Type-safe, structured agents | Medium | High |

---

# LEVEL 9 — Multi-Agent Systems
> *"Teams of AIs. Each an expert. Together: unstoppable."*
**Difficulty:** 🔥

Instead of one agent trying to do everything, you design a system of specialized agents that collaborate, delegate, and verify each other's work.

### Why Multi-Agent?
- **Parallelism** — multiple agents work simultaneously
- **Specialization** — each agent is expert in one thing
- **Error Checking** — one agent verifies another's output
- **Scalability** — add agents without redesigning the whole system

### Common Multi-Agent Patterns

#### 1. Orchestrator-Worker (Most Common)
```
[Orchestrator Agent]
  ├── "Research latest electrolysis papers"  → [Research Agent]
  ├── "Analyze cost data"                    → [Analysis Agent]
  ├── "Generate visualizations"             → [Code Agent]
  └── "Write final report"                  → [Writing Agent]
                                                    ↓
                                           [Final Output to User]
```

#### 2. Critic-Generator Loop
```
[Generator Agent] → produces output
        ↓
[Critic Agent] → scores and gives feedback
        ↓
[Generator Agent] → revises based on feedback
        ↓
Repeat until quality score ≥ threshold
```

#### 3. Debate / Consensus
```
Agent A: "PEM is the best electrolyzer for this application"
Agent B: "Actually AEL is more cost-effective at this scale"
Agent C (Moderator): Reviews both arguments → synthesizes consensus
```

#### 4. Pipeline with Handoffs
```
[Ingestion Agent] → [Processing Agent] → [Validation Agent] → [Output Agent]
```

### Practical Example: Research Report System
```python
import anthropic
import asyncio

client = anthropic.Anthropic()

async def researcher(topic: str) -> str:
    """Searches and summarizes information on a topic."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are a research specialist. Find and summarize key information.",
        messages=[{"role": "user", "content": f"Research: {topic}"}]
    )
    return response.content[0].text

async def analyst(raw_research: str) -> str:
    """Analyzes research and extracts key insights."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are a senior analyst. Extract actionable insights from research.",
        messages=[{"role": "user", "content": raw_research}]
    )
    return response.content[0].text

async def writer(insights: str) -> str:
    """Writes a polished report from insights."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are a technical writer. Create a clear, concise executive report.",
        messages=[{"role": "user", "content": insights}]
    )
    return response.content[0].text

async def multi_agent_report(topic: str):
    research = await researcher(topic)
    insights = await analyst(research)
    report = await writer(insights)
    return report

# Run parallel research on multiple topics
topics = ["PEM electrolyzer costs 2025", "Green ammonia market trends", "Hydrogen storage solutions"]
results = await asyncio.gather(*[researcher(t) for t in topics])
# All three run simultaneously!
```

### Agent Communication Methods
| Method | How | When to Use |
|---|---|---|
| **Direct function calls** | Agent A calls Agent B directly | Simple linear pipelines |
| **Message queues** | Agents publish/subscribe to topics (Redis, RabbitMQ) | Async, decoupled systems |
| **Shared state** | Agents read/write to a common database | Complex stateful systems |
| **Conversation** | Agents literally converse via chat (AutoGen style) | Iterative refinement tasks |

---

# LEVEL 10 — Memory & Persistent Agents
> *"The AI remembers everything. Across sessions. Across time."*
**Difficulty:** 🔥

Stateless agents forget everything when the conversation ends. Memory systems give agents continuity — the ability to learn from past interactions.

### Types of Memory

#### 1. In-Context Memory (Short-Term)
The conversation history in the current context window. Limited by token limits. Lost when session ends.

#### 2. External Memory (Long-Term)
Stored in a database. Retrieved and injected into context when relevant.

```python
import json
from datetime import datetime

class AgentMemory:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def save(self, user_id: str, key: str, value: str):
        """Store a memory."""
        self.db.execute(
            "INSERT INTO memories (user_id, key, value, created_at) VALUES (?, ?, ?, ?)",
            (user_id, key, value, datetime.now())
        )
    
    def recall(self, user_id: str, query: str, limit: int = 5) -> list:
        """Retrieve relevant memories using vector search."""
        query_embedding = embed(query)  # your embedding function
        return self.db.similarity_search(query_embedding, user_id=user_id, limit=limit)
    
    def get_all(self, user_id: str) -> list:
        """Get all memories for a user."""
        return self.db.execute("SELECT * FROM memories WHERE user_id = ?", (user_id,))
```

#### 3. Episodic Memory (Past Interactions)
Summaries of past conversations stored and retrievable.

```python
async def summarize_and_store_conversation(messages: list, user_id: str):
    """After a conversation, summarize and store key facts."""
    conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
    
    summary = client.messages.create(
        model="claude-sonnet-4-20250514",
        system="Extract and list: key facts learned about the user, decisions made, important context.",
        messages=[{"role": "user", "content": conversation_text}]
    )
    
    memory.save(user_id, "conversation_summary", summary.content[0].text)
```

#### 4. Semantic Memory (Knowledge Base)
Facts the agent knows, stored as embeddings and retrieved via similarity search. This is basically RAG applied to the agent's memory.

### Memory-Enhanced Agent Loop
```python
async def agent_with_memory(user_id: str, user_input: str) -> str:
    # 1. Recall relevant past context
    past_memories = memory.recall(user_id, user_input, limit=3)
    memory_context = "\n".join(m['value'] for m in past_memories)
    
    # 2. Build enhanced system prompt
    system = f"""You are a personal assistant.
    
What you remember about this user:
{memory_context}

Use this context naturally in your response."""
    
    # 3. Generate response
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system=system,
        messages=[{"role": "user", "content": user_input}]
    )
    
    # 4. Save new information from this interaction
    await extract_and_save_new_memories(user_id, user_input, response.content[0].text)
    
    return response.content[0].text
```

### Memory Frameworks
- **Mem0** (`pip install mem0ai`) — drop-in memory layer for any AI app
- **Zep** — long-term memory and fact extraction platform
- **LangChain Memory** — various memory types built into LangChain
- **Custom Vector DB** — ChromaDB/Qdrant + your own retrieval logic

---

# LEVEL 11 — Agentic Code Execution
> *"The AI writes code. Then runs it. Then fixes it. Autonomously."*
**Difficulty:** 🔥

This is the level of Claude Code and GitHub Copilot Workspace. The agent doesn't just suggest code — it writes it, runs it in a sandboxed environment, reads the output, fixes errors, and iterates.

### The Code Agent Loop
```
[Task Description]
      ↓
[LLM writes code]
      ↓
[Sandboxed execution]
      ↓
[Read stdout/stderr]
      ↓
Did it work? ──No──→ [LLM reads error + rewrites]
      │                       ↑
      │                       └── (loop)
     Yes
      ↓
[Return result]
```

### Implementation with E2B (Sandboxed Code Execution)
```python
from e2b_code_interpreter import Sandbox

async def code_agent(task: str) -> str:
    sandbox = Sandbox()
    messages = [{"role": "user", "content": task}]
    
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            tools=[{
                "name": "execute_python",
                "description": "Execute Python code and return output",
                "input_schema": {
                    "type": "object",
                    "properties": {"code": {"type": "string"}},
                    "required": ["code"]
                }
            }],
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            return response.content[0].text
        
        # Execute code tool
        for block in response.content:
            if block.type == "tool_use" and block.name == "execute_python":
                execution = sandbox.run_code(block.input["code"])
                result = execution.text or execution.error
                
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": [{"type": "tool_result", "tool_use_id": block.id, "content": result}]
                })
                break
```

### Code Execution Environments
| Tool | Type | Security | Use Case |
|---|---|---|---|
| **E2B** | Cloud sandbox | High | Production code agents |
| **Docker** | Container | High | Self-hosted sandboxing |
| **Subprocess** | Local execution | Low | Dev/trusted environments only |
| **WebAssembly** | Browser sandbox | Medium | Client-side code execution |
| **Jupyter/IPython** | Notebook kernel | Low-Medium | Data science agents |

---

# LEVEL 12 — Autonomous Long-Horizon Agents
> *"Give it a goal. Come back in an hour. It figured it out."*
**Difficulty:** 💀

These agents execute complex, open-ended tasks over minutes or hours, making dozens of decisions, recovering from failures, and working without human intervention.

### What Changes at This Level
- Tasks span **hundreds of steps**, not 5-10
- The agent must **plan, re-plan, and recover** from errors
- Requires **persistent state** (the agent's working memory across steps)
- Needs **human escalation** logic (when to ask for help vs. proceed)
- Must handle **partial failures** gracefully

### Planning Architectures

#### ReAct (Reason + Act) — Most Common
```
Thought: I need to analyze the electrolyzer market report. First I'll search for it.
Action: web_search("electrolyzer market size 2025 report")
Observation: Found article at example.com/report
Thought: Let me fetch the full article.
Action: fetch_url("example.com/report")
Observation: [article content]
Thought: I have enough data. Now I'll structure the analysis.
Action: write_file("analysis.md", structured_content)
Observation: File written successfully.
Thought: Task complete.
```

#### Plan-and-Execute
```python
# Step 1: Generate a plan
plan = llm.plan("""
Task: Research and write a technical comparison of PEM vs AEL electrolyzers.

Break this into specific, executable steps.
""")
# → ["Search for recent papers", "Compare efficiency data", "Analyze costs", "Write report"]

# Step 2: Execute each step in sequence (or parallel where safe)
results = []
for step in plan:
    result = agent.execute(step, context=results)
    results.append(result)
    
    # Re-plan if a step fails or reveals new requirements
    if result.needs_replanning:
        plan = llm.replan(original_task=task, completed=results, failed_step=step)
```

#### Reflexion (Self-Critique Loop)
```
[Attempt task]
      ↓
[Evaluate own output against success criteria]
      ↓
Good enough? ──No──→ [Generate critique of own work]
      │                         ↓
      │               [Attempt again with critique]
     Yes                        ↑
      ↓                         └── (loop, max N times)
[Return result]
```

### Human-in-the-Loop Escalation
```python
CONFIDENCE_THRESHOLD = 0.85

async def agent_with_escalation(task: str, user_id: str):
    result = await agent.attempt(task)
    
    if result.confidence < CONFIDENCE_THRESHOLD:
        # Pause and ask human
        await notify_user(user_id, 
            f"I'm not confident about this step: '{result.uncertain_step}'. "
            f"My best approach: {result.proposed_action}. Proceed? [Y/N]"
        )
        user_approval = await wait_for_user_response(user_id, timeout=300)
        
        if user_approval:
            return await agent.continue_from(result.checkpoint)
        else:
            return await agent.take_alternative_action(result)
```

### Production Considerations
- **Checkpointing** — save agent state periodically so you can resume if it crashes
- **Token budgets** — cap how many tokens an autonomous run can consume
- **Action sandboxing** — dangerous actions (delete files, send emails) require approval
- **Audit logging** — log every decision and action for debugging
- **Timeout handling** — long-running tasks need heartbeats and timeout recovery

---

# LEVEL 13 — Agent Harness Engineering
> *"You're not building apps anymore. You're building the runtime."*
**Difficulty:** 💀

This is the level studied in the claw-code repo. Rather than using a framework, you design the entire agent execution runtime yourself — the tool dispatcher, the context manager, the loop controller.

### What Is a "Harness"?
A harness is the engine room of an agent:
- How tools are registered, discovered, and dispatched
- How the context window is managed across long runs
- How errors propagate and get handled
- How the model's output is parsed and routed
- How state persists across tool calls and turns

### Core Harness Components
```
┌─────────────────────────────────────────────────────┐
│                  AGENT HARNESS                      │
│                                                     │
│  ┌───────────┐   ┌────────────┐   ┌──────────────┐ │
│  │  Tool     │   │  Context   │   │   Loop       │ │
│  │ Registry  │   │  Manager   │   │ Controller   │ │
│  │           │   │            │   │              │ │
│  │ - register│   │ - window   │   │ - max_turns  │ │
│  │ - discover│   │ - compress │   │ - stop_cond  │ │
│  │ - dispatch│   │ - inject   │   │ - error_hand │ │
│  └───────────┘   └────────────┘   └──────────────┘ │
│                                                     │
│  ┌───────────┐   ┌────────────┐   ┌──────────────┐ │
│  │  State    │   │  Output    │   │   Safety     │ │
│  │  Store    │   │  Parser    │   │   Guards     │ │
│  └───────────┘   └────────────┘   └──────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Minimal Harness Implementation
```python
import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

@dataclass
class Tool:
    name: str
    description: str
    schema: dict
    handler: Callable[..., Awaitable[str]]

class AgentHarness:
    def __init__(self, model: str, system: str, max_turns: int = 20):
        self.model = model
        self.system = system
        self.max_turns = max_turns
        self.tools: dict[str, Tool] = {}
        self.messages: list = []
    
    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool
    
    def _build_tool_schemas(self) -> list:
        return [{"name": t.name, "description": t.description, "input_schema": t.schema}
                for t in self.tools.values()]
    
    async def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        
        for turn in range(self.max_turns):
            response = client.messages.create(
                model=self.model,
                system=self.system,
                tools=self._build_tool_schemas(),
                messages=self.messages
            )
            
            # Append model's response to history
            self.messages.append({"role": "assistant", "content": response.content})
            
            if response.stop_reason == "end_turn":
                return next(b.text for b in response.content if hasattr(b, 'text'))
            
            # Execute all tool calls in parallel
            tool_results = await asyncio.gather(*[
                self._execute_tool(block)
                for block in response.content
                if block.type == "tool_use"
            ])
            
            self.messages.append({"role": "user", "content": tool_results})
        
        raise RuntimeError(f"Agent exceeded {self.max_turns} turns without completing task")
    
    async def _execute_tool(self, tool_use_block) -> dict:
        tool = self.tools.get(tool_use_block.name)
        if not tool:
            result = f"ERROR: Unknown tool '{tool_use_block.name}'"
        else:
            try:
                result = await tool.handler(**tool_use_block.input)
            except Exception as e:
                result = f"ERROR: {str(e)}"
        
        return {"type": "tool_result", "tool_use_id": tool_use_block.id, "content": result}
```

---

# LEVEL 14 — Self-Improving & Meta-Agents
> *"Agents that write agents. Agents that improve themselves."*
**Difficulty:** 💀

The frontier of agent research. These systems can analyze their own performance, generate better prompts for themselves, write new tools, and recursively improve.

### Prompt Optimization Agents
```python
async def optimize_prompt(task: str, current_prompt: str, examples: list) -> str:
    """An agent that improves its own prompts based on failure cases."""
    
    failures = [ex for ex in examples if ex['score'] < 0.7]
    
    optimizer = client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are a prompt engineering expert. Analyze failures and improve the prompt.",
        messages=[{"role": "user", "content": f"""
Task: {task}

Current prompt: {current_prompt}

Failure cases (input → expected → actual):
{json.dumps(failures, indent=2)}

Generate an improved prompt that addresses these failures.
"""}]
    )
    return optimizer.content[0].text
```

### Tool-Writing Agents
An agent can write new Python tools for itself when it lacks capability:

```python
TOOL_SANDBOX = {}

async def agent_with_tool_creation(task: str):
    """An agent that creates new tools when it needs them."""
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system="""You are an agent that can create new tools when needed.
        If you need a capability you don't have, output a Python function as a tool.
        Format: <new_tool name="tool_name">def tool_name(...): ...</new_tool>""",
        messages=[{"role": "user", "content": task}]
    )
    
    # Parse and register any new tools the agent wrote
    if "<new_tool" in response.content[0].text:
        tool_code = extract_tool_code(response.content[0].text)
        exec(tool_code, TOOL_SANDBOX)
        new_tool_fn = TOOL_SANDBOX[extract_tool_name(response.content[0].text)]
        harness.register_tool(Tool(name=..., handler=new_tool_fn, ...))
        
        # Re-run now that the new tool is available
        return await agent_with_tool_creation(task)
```

### Evaluation-Driven Self-Improvement
```
[Agent attempts N tasks]
        ↓
[Evaluator scores each attempt]
        ↓
[Pattern Analysis: where does it fail consistently?]
        ↓
[Generate improved system prompt]
        ↓
[Run evaluation again → measure delta]
        ↓
[Keep if better, discard if worse]
        ↓
Loop forever → continuous improvement
```

---

# LEVEL 15 — Production Agent Infrastructure
> *"This thing is running 24/7 for real users. Don't break it."*
**Difficulty:** 💀

### Architecture for Production
```
[Load Balancer]
      ↓
[API Gateway] — Rate limiting, auth, logging
      ↓
[Agent Orchestrator Service]
      ↓
[Task Queue] ← [Celery / BullMQ / Temporal]
      ↓
[Agent Workers] ← [Docker containers, auto-scaling]
    ├── Tool Executor Service
    ├── LLM Proxy Service (retry, fallback models)
    └── Memory Service
      ↓
[Persistent Storage]
    ├── PostgreSQL (structured state, history)
    ├── Redis (session cache, queue)
    └── Vector DB (semantic memory)
      ↓
[Monitoring Stack]
    ├── LangFuse (LLM observability, trace every call)
    ├── Prometheus + Grafana (metrics)
    └── Sentry (error tracking)
```

### LLM Observability with LangFuse
```python
from langfuse.decorators import observe, langfuse_context

@observe()
async def my_agent(user_input: str, user_id: str) -> str:
    langfuse_context.update_current_trace(user_id=user_id, input=user_input)
    
    result = await harness.run(user_input)
    
    langfuse_context.update_current_observation(output=result)
    return result
# Every call is now traced: latency, tokens, cost, errors
```

### Fallback & Resilience
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def resilient_llm_call(messages: list, model: str = "claude-sonnet-4-20250514"):
    try:
        return await client.messages.create(model=model, messages=messages, ...)
    except anthropic.RateLimitError:
        # Fall back to a different model or provider
        return await groq_client.chat.completions.create(model="llama-3.1-70b", messages=messages)
```

### Cost Management
- **Token budgets per user** — hard caps to prevent runaway spend
- **Model tiering** — use Haiku/small models for simple tasks, Sonnet/Opus for complex
- **Caching** — semantic caching (same query ≈ same answer → serve cached)
- **Batching** — Anthropic's Message Batches API for up to 50% cost reduction on bulk tasks

### Security Considerations
- **Prompt Injection** — users embed instructions in their data to hijack your agent
  - Mitigate: use delimiters, validate tool inputs, never run user-supplied code directly
- **Data Exfiltration** — agent tools could leak sensitive data
  - Mitigate: sandbox tool execution, log all tool I/O, restrict network access in tools
- **Infinite Loops** — a buggy agent loops forever spending tokens
  - Mitigate: hard turn limits, token budgets, circuit breakers
- **Tool Misuse** — agent calls dangerous tools incorrectly
  - Mitigate: human approval for irreversible actions, dry-run modes

---

# Putting It All Together: Your Stack Recommendation

Based on your current skills (Python, Aiogram, Celery, Redis, PostgreSQL, Docker, Next.js):

| Level | Your Entry Point | Suggested Next Step |
|---|---|---|
| 1-2 | ✅ Already doing this (Groq in your bot) | Upgrade to structured outputs + better system prompts |
| 3 | Try Ollama locally for a private model | Use with your Telegram bot via base_url swap |
| 4-5 | ✅ Doing this (multi-modal Telegram pipeline) | Add tool calling + structured tool results |
| 6 | Add ChromaDB + nomic-embed to your bot | Build a "ask your documents" feature |
| 7 | Create one MCP server for your green energy data | Connect to Claude Desktop for daily analysis |
| 8 | Add LangGraph to your Next.js ClipFlow project | Stateful content generation workflow |
| 9 | Multi-agent report generator (research → write → verify) | Side project / productize |
| 10 | Add Mem0 to your Telegram bot | Persistent user memory across sessions |
| 11-12 | Study LangGraph source + claw-code architecture | Build your own harness for Omni |
| 13-14 | Build eval suite + prompt optimizer for your bot | Continuous improvement loop |
| 15 | Docker + LangFuse + Prometheus for Omni on Oracle Cloud | Production-grade deployment |

---

# Quick Reference: Tools & Libraries

| Category | Tool | Install |
|---|---|---|
| **LLM Clients** | anthropic, openai, groq | `pip install anthropic openai groq` |
| **Local Models** | Ollama | `ollama.ai` |
| **Agent Framework** | LangGraph | `pip install langgraph` |
| **Multi-Agent** | CrewAI | `pip install crewai` |
| **RAG** | ChromaDB | `pip install chromadb` |
| **Memory** | Mem0 | `pip install mem0ai` |
| **MCP** | mcp | `pip install mcp` |
| **Observability** | LangFuse | `pip install langfuse` |
| **STT** | faster-whisper | `pip install faster-whisper` |
| **OCR** | surya | `pip install surya-ocr` |
| **Code Execution** | E2B | `pip install e2b-code-interpreter` |
| **Embeddings** | sentence-transformers | `pip install sentence-transformers` |
| **Vector DB** | Qdrant | `pip install qdrant-client` |
| **Async Queue** | Celery + Redis | `pip install celery redis` ✅ |

---

*Last Updated: April 2026 — The AI agent ecosystem moves fast. Check each library's docs for latest patterns.*
