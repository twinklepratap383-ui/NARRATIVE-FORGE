# NarrativeForge
### Interactive Cinematic Story Engine — Multi-Agent Narrative Intelligence

> **"What if an AI character could genuinely lie to you — and mean it?"**

NarrativeForge is not a chatbot. It is a small **operating system for stories**:
a set of cooperating AI agents that each maintain memory, emotions, and a hidden
agenda, and reason — step by step — before they speak. Built for **Microsoft
Agents League 2026**, it runs fully offline on a deterministic mock model and
switches to **Azure OpenAI + Azure AI Foundry (Foundry IQ)** the instant
credentials are supplied — no code changes required.

![status](https://img.shields.io/badge/demo-runs%20offline-2e8b57)
![python](https://img.shields.io/badge/python-3.12-blue)
![fastapi](https://img.shields.io/badge/backend-FastAPI-009688)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Table of Contents

1. [What is NarrativeForge?](#what-is-narrativeforge)
2. [Why it's different](#why-its-different)
3. [The demo scenario — The Ashworth Affair](#the-demo-scenario--the-ashworth-affair)
4. [How to use it](#how-to-use-it)
   - [Quick start (offline, 60 seconds)](#quick-start-offline-60-seconds)
   - [Using the frontend — a walkthrough](#using-the-frontend--a-walkthrough)
   - [Using the API directly](#using-the-api-directly)
   - [Running with Docker](#running-with-docker)
   - [Going live: Azure OpenAI + Foundry IQ](#going-live-azure-openai--foundry-iq)
5. [Architecture](#architecture)
6. [Meet the agents](#meet-the-agents)
7. [Real-world use cases](#real-world-use-cases)
8. [Project structure](#project-structure)
9. [API reference](#api-reference)
10. [Testing](#testing)
11. [Extending NarrativeForge](#extending-narrativeforge)
12. [Roadmap](#roadmap)
13. [Troubleshooting](#troubleshooting)
14. [The pitch](#the-pitch)
15. [License](#license)

---

## What is NarrativeForge?

The player takes the role of an **investigator** questioning suspects after a
murder at a fog-bound English country house in 1887. Each suspect — Lady
Ashworth, the butler Hargrove, and the business partner Crane — is powered by
its own **Character Agent**, which:

- remembers everything that's happened so far (and what it told you, and when),
- holds a **secret goal** it will never state directly,
- tracks six emotions (fear, trust, anger, love, loyalty, confidence),
- grounds its reasoning in narrative craft via **Foundry IQ**,
- and **deflects, redirects, or lies** when cornered — consistently, in character.

Behind the scenes, a small society of agents collaborates every time you ask a
question:

```
You ask a question
        │
        ▼
 ┌─────────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────┐
 │  Character  │──▶│ Consequence  │──▶│ Director │──▶│ Narrator │──▶ scene
 │ (in-character│   │ (world state,│   │ (tension,│   │ (cinematic│
 │  reasoning)  │   │  clues,      │   │  pacing) │   │  prose)  │
 │              │   │  emotions)   │   │          │   │          │
 └─────────────┘   └──────────────┘   └──────────┘   └──────────┘
        ▲
        │
   ┌─────────┐
   │ Memory  │  recency + importance-weighted recall
   └─────────┘
```

Every agent's reasoning is **visible** — toggle "Reasoning" in the UI and watch
the actual decision trail: what memory was recalled, what narrative principle was
applied, how stressed the character is, and why they chose to deflect rather than
answer plainly.

---

## Why it's different

| | A typical AI chatbot character | NarrativeForge character |
|---|---|---|
| **Memory** | None, or a sliding context window | Weighted recall — recent *and* important events always surface |
| **Goals** | None — just answers the prompt | A secret goal that shapes every line without ever being stated |
| **Consistency** | Drifts over long conversations | Consequence Agent enforces a single, persistent world-truth |
| **Emotion** | Static tone | Six-axis emotional state that shifts every turn and changes behaviour |
| **Reasoning** | Hidden inside one model call | A visible, inspectable multi-agent trace |
| **Grounding** | Hallucination-prone | Grounded in a narrative-theory knowledge base (Foundry IQ) |
| **Pacing** | None — every answer is "flat" | A Director Agent manages tension like a writer manages a script |

This is the difference between **generating a response** and **portraying a
character**.

---

## The demo scenario — The Ashworth Affair

| Suspect | Public stance | Secret goal |
|---|---|---|
| **Lady Eleanor Ashworth** — the widow | Cooperative, grief-stricken, wants this settled quickly | Protect her son Julian from scandal at any cost |
| **Mr. Hargrove** — the butler | Discreet, plain-spoken, dutiful | Shield Lady Ashworth, whom he's served for 30 years |
| **Mr. Sebastian Crane** — the late lord's business partner | Distance himself, protect the firm's name | Hide that he was about to be cut out of the business |

The hidden ground truth (never shown to the player, checked by the Consequence
Agent against any accusation): **Crane** killed Lord Ashworth to stop being
forced out of the firm, entering through the garden window. Lady Ashworth saw
him — but stays silent to protect her son from suspicion.

You win by **questioning each suspect**, watching clues accumulate in the Clue
Registry and tension rise on the meter, then making the correct **Accusation**.

---

## How to use it

### Quick start (offline, 60 seconds)

No Azure account, no API keys, no internet required.

```bash
cd narrativeforge/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** — the full cinematic UI is served directly by the
backend. Interactive API docs (Swagger) are at **http://localhost:8000/docs**.

If installing the full requirements is slow (it includes optional Azure/LangGraph
SDKs), this minimal set is enough to run and test everything:

```bash
pip install fastapi==0.115.5 'pydantic==2.10.3' 'pydantic-settings==2.6.1' \
            'uvicorn[standard]==0.32.1' 'httpx==0.27.2' \
            pytest==8.3.4 pytest-asyncio==0.24.0
```

Check what mode you're running in at any time:

```bash
curl localhost:8000/api/health
# {"status":"ok","azure_openai":"mock","foundry_iq":"offline-kb", ...}
```

---

### Using the frontend — a walkthrough

When the page loads, a story is created automatically and the opening narration
appears: *"The gaslight gutters in its sconce..."*

**1. Choose who to question.**
Three pill-shaped buttons sit above the input box: **Ashworth**, **Hargrove**,
**Crane**. The highlighted (gold) one is who you're currently addressing.

**2. Ask a question.**
Type into "Question the witness…" and press **Ask** (or Enter). Good opening
questions:
- *"Where were you the night your husband died?"*
- *"What can you tell me about the study?"*
- *"Did you notice anything unusual that evening?"*

**3. Read the response.**
A narrator line (italic, scene-setting) appears, followed by the character's
in-character reply.

**4. Turn on Reasoning.**
Click **"Reasoning ▸ OFF"** to flip it to **ON**. Now every response expands to
show the full agent trace:
- `memory_retrieval` — which past memories were recalled and why
- `foundry_iq` — the narrative-craft principle grounding this response
- `conflict_analysis` — the character's current stress level and whether it's
  choosing candour or deflection
- `decision` — confirmation the response stayed consistent with memory and goal
- `clue_registered` / `world_update` — what changed in the world
- `emotion_update` — how the character's feelings shifted
- `pacing` — how much the tension meter moved, and why

**5. Watch the meters.**
- **TENSION** (top bar) rises as the investigation gets closer to the truth.
- **ACT** advances (I → II → III) as tension crosses thresholds.
- In the right-hand **suspects panel**, each character's emotion bars (fear,
  trust, anger, confidence, loyalty) shift after every exchange.

**6. Watch for clues.**
New entries appear in the **Clue Registry** on the right as the investigation
progresses.

**7. Cross-examine.**
Switch suspects mid-investigation. Other characters silently gain awareness that
someone else was questioned — ask the butler about Lady Ashworth after
questioning her, and notice his memory already reflects it.

**8. Make your accusation.**
When you're confident, select a suspect and click **"Make Accusation"**. Confirm
the prompt. The Consequence Agent checks your choice against the hidden truth:
- **Correct (Crane)** → the case is solved, tension maxes out, a full confession
  scene plays.
- **Incorrect** → the suspect denies it coldly, and the mystery continues — you
  can keep investigating and accuse again.

---

### Using the API directly

Everything the frontend does is a plain JSON API call — useful for scripting,
testing, or building an alternative UI.

```bash
# 1. Create a story
curl -s -X POST localhost:8000/api/stories \
  -H 'content-type: application/json' \
  -d '{"scenario_id":"victorian_murder"}' | tee story.json

STORY_ID=$(python3 -c "import json;print(json.load(open('story.json'))['id'])")

# 2. Ask a character a question
curl -s -X POST localhost:8000/api/stories/$STORY_ID/turn \
  -H 'content-type: application/json' \
  -d '{"speak_to":"ashworth","message":"Where were you that night?"}' | python3 -m json.tool

# 3. Check live analytics (tension, emotions, clues, relationships)
curl -s localhost:8000/api/stories/$STORY_ID/analytics | python3 -m json.tool

# 4. Make an accusation
curl -s -X POST localhost:8000/api/stories/$STORY_ID/turn \
  -H 'content-type: application/json' \
  -d '{"accuse":"crane"}' | python3 -m json.tool
```

---

### Running with Docker

```bash
cd narrativeforge
cp .env.example .env        # optionally fill in Azure keys — see below
docker compose up --build
```

This starts the backend (port 8000) plus a Redis container for shared story
state. Without Azure keys it runs identically to the local quick start, on the
offline mock.

---

### Going live: Azure OpenAI + Foundry IQ

Fill in `.env` (or set container environment variables). The moment all three
Azure OpenAI values are present, the engine **automatically routes to the real
model** — there is no flag to flip and no code to change.

| Variable | Purpose |
|---|---|
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | API key |
| `AZURE_OPENAI_DEPLOYMENT` | GPT-4o deployment — used for narration and character dialogue |
| `AZURE_OPENAI_DEPLOYMENT_MINI` | GPT-4o-mini deployment — used for the Consequence/Director/Emotion JSON reasoning steps |
| `AZURE_OPENAI_API_VERSION` | API version (default `2024-10-21`) |
| `FOUNDRY_PROJECT_ENDPOINT` | Azure AI Foundry project endpoint |
| `FOUNDRY_KB_ID` | Foundry IQ knowledge base ID (narrative theory corpus) |
| `REDIS_URL` | Optional — shares story state across multiple backend replicas |
| `CORS_ORIGINS` | Comma-separated allowed origins (default `*`) |

**Why the model split?** Player-facing narration (Narrator, Character dialogue)
uses GPT-4o for quality. The internal JSON reasoning steps (Consequence, Director,
Emotion — none of which the player reads directly) use the cheaper GPT-4o-mini.
This keeps per-turn cost down even though five agents run on every exchange.

**Why Foundry IQ matters here, specifically:** the Character Agent doesn't just
retrieve facts — it retrieves *narrative craft* (e.g. "under pressure, suspects
deflect with a technically-true but misleading detail") and lets that shape *how*
it lies. The Director Agent also writes to **procedural memory**: tactics that
raised player engagement in past sessions are recalled and preferred in future
ones.

Confirm you're live:

```bash
curl localhost:8000/api/health
# {"status":"ok","azure_openai":"live","foundry_iq":"live", ...}
```

---

## Architecture

```
┌─────────────┐        HTTP/JSON         ┌──────────────────────────────┐
│  Frontend   │ ───────────────────────► │          FastAPI             │
│ index.html  │ ◄─────────────────────── │  /api/stories  /api/turn ... │
└─────────────┘                          └───────────────┬──────────────┘
                                                          │
                                          ┌───────────────▼──────────────┐
                                          │         Orchestrator         │
                                          │  (one acyclic turn pipeline)  │
                                          └───┬─────┬──────┬─────┬────────┘
                                              │     │      │     │
                                       Character Consequence Director Narrator
                                              │     │      │     │
                                          ┌───▼─────▼──────▼─────▼───┐
                                          │   Story state (pydantic) │
                                          │  characters · world ·    │
                                          │  clues · tension · scenes│
                                          └───────────┬──────────────┘
                                                      │
                                       ┌──────────────▼──────────────┐
                                       │  StoryStore (memory | Redis)│
                                       └──────────────────────────────┘

      LLM layer:  Azure OpenAI (GPT-4o / GPT-4o-mini)  ──or──  offline mock
      Grounding:  Foundry IQ knowledge base            ──or──  bundled corpus
```

**Design principles:**

- **Single source of truth.** All turn logic lives in `Orchestrator`. The same
  agent instances are also wrapped as a LangGraph `StateGraph` in `graph.py` for
  judges who want to see the explicit graph topology — it can never drift from
  the runtime because it calls the same code.
- **State is plain data.** The entire `Story` is one pydantic model. It
  serialises cleanly to Redis (or later, Cosmos DB) and resumes exactly where it
  left off. Tests run the engine directly, with no HTTP layer at all.
- **Cloud is a config flag, not a fork.** `llm.py` and `foundry.py` each check
  whether Azure credentials are present and route accordingly. The offline mock
  and bundled knowledge base exist so a live demo never depends on network
  conditions on stage.
- **No circular dependencies.** Execution order is strictly:
  `player input → Character → Consequence → Director → Narrator → output`.
  Only the addressed character runs the full pipeline; other characters get a
  cheap memory write so they stay "aware" without adding latency.

---

## Meet the agents

| Agent | Responsibility | Reads / writes | Model |
|---|---|---|---|
| **Character** | Generates the in-character line. Retrieves memory, grounds in Foundry IQ, weighs stress, and chooses candour vs. deflection toward its hidden goal. | character memory, emotions, knowledge | GPT-4o |
| **Memory** | Recency + importance-weighted recall. Recent memories score higher; high-importance memories (secrets, emotional peaks) always surface regardless of age. | character memory | — (ranking only) |
| **Consequence** | The keeper of ground truth. Mutates world facts, registers new clues, computes emotion deltas, and evaluates accusations against the hidden solution. | world state, clues, emotions | GPT-4o-mini |
| **Director** | Paces the story like a showrunner. Adjusts the tension meter in waves (not a straight line), advances acts, and records which tactics engaged the player into procedural memory. | tension, act, procedural memory | GPT-4o-mini |
| **Narrator** | Stateless. Renders one atmospheric sentence of cinematic prose, tuned to the current tension level. | — | GPT-4o |

Every agent emits a structured `AgentTrace { agent, step, detail }`, which is
exactly what populates the Reasoning Panel.

---

## Real-world use cases

The agent architecture is **scenario-agnostic** — the murder mystery is the
showcase, but the same five-agent pipeline applies to:

- **Corporate training simulations** — practice difficult conversations
  (performance reviews, negotiations, conflict de-escalation) against
  characters with realistic, evolving emotional responses.
- **Interactive fiction & games** — narrative experiences where every NPC has
  memory and motive instead of a fixed dialogue tree.
- **Historical & language education** — period-grounded characters (via Foundry
  IQ's domain knowledge bases) for immersive, conversational learning.
- **Therapeutic narrative practice** *(with appropriate clinical oversight —
  NarrativeForge itself is not a clinical tool)* — low-stakes rehearsal of
  difficult conversations.
- **Tabletop RPG "Dungeon Master" assistance** — an always-available world-state
  keeper, consequence tracker, and pacing director.

Adding a new scenario means adding one dict to
`backend/app/scenarios/__init__.py`: characters, personalities, secret goals,
starting emotions, world facts, and the hidden truth. No other code changes.

---

## Project structure

```
narrativeforge/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── base.py          # shared Agent base class + trace helper
│   │   │   ├── character.py     # Character Agent
│   │   │   ├── consequence.py   # Consequence Agent
│   │   │   ├── director.py      # Director Agent
│   │   │   ├── memory.py        # Memory Agent (recall ranking)
│   │   │   └── narrator.py      # Narrator Agent
│   │   ├── routes/
│   │   │   ├── stories.py       # /api/stories, /turn
│   │   │   └── meta.py          # /api/health, /analytics
│   │   ├── scenarios/
│   │   │   └── __init__.py      # bundled scenarios (The Ashworth Affair)
│   │   ├── orchestrator.py      # the turn pipeline — single source of truth
│   │   ├── graph.py             # same pipeline as a LangGraph StateGraph
│   │   ├── llm.py               # Azure OpenAI client + offline mock LLM
│   │   ├── foundry.py           # Foundry IQ grounding + procedural memory
│   │   ├── store.py             # in-memory / Redis story store
│   │   ├── schemas.py           # shared pydantic models (the "blackboard")
│   │   ├── config.py            # env-driven settings
│   │   └── main.py              # FastAPI app entrypoint
│   ├── tests/
│   │   ├── test_engine.py       # agent pipeline tests (offline)
│   │   └── test_api.py          # HTTP API tests (offline)
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   └── index.html               # no-build cinematic UI (served by FastAPI)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── AGENTS.md
│   ├── DEMO_SCRIPT.md
│   └── ROADMAP.md
├── .github/workflows/ci.yml     # GitHub Actions test pipeline
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## API reference

Full interactive schema (request/response models, try-it-out) is always at
**`/docs`** when the server is running. Summary:

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Server status, and whether Azure OpenAI / Foundry IQ are live or mocked |
| `GET` | `/api/scenarios` | List all playable scenarios |
| `POST` | `/api/stories` | Create a new story (`{"scenario_id": "victorian_murder"}`) — returns the full story including opening narration |
| `GET` | `/api/stories/{id}` | Fetch the full current story state |
| `POST` | `/api/stories/{id}/turn` | Play a turn — either `{"speak_to": "<character_id>", "message": "..."}` or `{"accuse": "<character_id>"}` |
| `GET` | `/api/stories/{id}/analytics` | Tension history, per-character emotions, relationships, clues, memory counts, solved status |

Character IDs in the bundled scenario: `ashworth`, `hargrove`, `crane`.

---

## Testing

```bash
cd backend
pytest -q
```

12 tests, fully offline (no network, no API keys required), covering:

- Opening scene generation
- A full dialogue turn producing both narration and character dialogue scenes
- Presence of every expected reasoning-trace step
- Memory accumulation across multiple turns
- Cross-character awareness (one character "hears about" another being questioned)
- Correct accusation → story solved, act advances to III
- Incorrect accusation → mystery remains open
- Invalid actions raise clear errors
- Tension stays bounded in `[0, 1]` over many turns
- Full HTTP flow: create → play → analytics → accuse → 409 on further turns
- Unknown scenario → 404

CI runs this same suite on every push via GitHub Actions
(`.github/workflows/ci.yml`).

---

## Extending NarrativeForge

- **New scenario** — add an entry to `SCENARIOS` in
  `backend/app/scenarios/__init__.py`: define characters (personality, public/
  secret goals, starting emotions, knowledge), the world state, relationships,
  and the hidden `truth` checked on accusation.
- **New agent** — subclass `Agent` in `backend/app/agents/base.py`, wire it into
  `Orchestrator._handle_dialogue` (and mirror it in `graph.py` if you want it in
  the LangGraph view).
- **Persistent storage** — implement a new `StoryStore` backend (e.g. Cosmos DB)
  matching the existing async `save`/`get`/`list_ids` interface.
- **Streaming** — the frontend already renders scenes incrementally; adding a
  `/ws/stories/{id}` WebSocket endpoint that streams Narrator/Character tokens is
  the highest-impact next step for live demos.
- **New frontend** — `frontend/index.html` is a no-build reference client. Any
  framework (Next.js, React, etc.) can drive the same JSON API.

See `docs/ROADMAP.md` for a prioritized list of next steps.

---

## Roadmap

| Status | Item |
|---|---|
| ✅ | Five-agent pipeline + Memory recall, fully offline-runnable |
| ✅ | LangGraph `StateGraph` mirror of the pipeline |
| ✅ | Azure OpenAI routing (4o / 4o-mini split) with offline mock fallback |
| ✅ | Foundry IQ semantic grounding + procedural memory (offline corpus included) |
| ✅ | The Ashworth Affair scenario with hidden ground truth |
| ✅ | FastAPI backend, OpenAPI docs, in-memory + Redis store |
| ✅ | Cinematic frontend with live Reasoning Panel, tension meter, clue registry |
| ✅ | 12 offline tests, CI, Docker, Compose |
| ⏭ | WebSocket token streaming for live narration |
| ⏭ | Consistency Guarantor — regenerate responses that drift from memory |
| ⏭ | Second scenario (e.g. corporate negotiation) to prove genre-agnosticism |
| 🔮 | Next.js/React frontend, Cosmos DB store, Azure Container Apps + IaC |

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Browser shows "backend offline" | Make sure `uvicorn` is running on port 8000; the UI is served from `/` by the backend itself |
| `pip install -r requirements.txt` is slow / fails on Azure SDKs | Use the minimal dependency set in [Quick start](#quick-start-offline-60-seconds) — the Azure/LangGraph packages are optional |
| `/api/health` shows `"azure_openai": "mock"` when you expected `"live"` | All three of `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_DEPLOYMENT` must be set |
| Docker build can't reach a package mirror | Corporate networks may block registries — build on an unrestricted network, or fall back to the local `uvicorn` path |
| `404 Not Found` for `/favicon.ico` in logs | Harmless — no favicon is bundled; doesn't affect functionality |
| Story state lost on restart | Expected with the default in-memory store; set `REDIS_URL` for persistence across restarts/replicas |

---

## The pitch

> Stories are how humans make sense of the world. NarrativeForge is the first AI
> system that builds stories the way humans do — through reasoning, memory,
> conflict, and consequence. Every character reasons before it speaks, remembers
> what you told it turns ago, and lies when its goals demand it. The same engine
> that runs a Victorian murder mystery runs corporate training, historical
> education, and interactive fiction — grounded in Microsoft Foundry IQ,
> orchestrated as a LangGraph pipeline, and fully inspectable through a live
> Reasoning Panel.
>
> **We didn't script this story. Our agents discovered it.**

---

## License

MIT.
