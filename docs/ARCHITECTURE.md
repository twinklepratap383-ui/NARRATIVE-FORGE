# Architecture

## System overview

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
                                       │  StoryStore (mem | Redis)    │
                                       └──────────────────────────────┘

      LLM layer:  Azure OpenAI (GPT-4o / GPT-4o-mini)  ──or──  offline mock
      Grounding:  Foundry IQ knowledge base            ──or──  bundled corpus
```

## Why this shape

- **Single source of truth for logic.** All turn logic lives in `Orchestrator`.
  `graph.py` wraps the *same* agent instances in a LangGraph `StateGraph`, so the
  graph view never drifts from the runtime.
- **State is data.** The whole `Story` is a pydantic model, so it serialises to
  Redis (or Cosmos DB later) and resumes cleanly. Tests run the engine directly
  without HTTP.
- **Cloud is a config flag, not a fork.** `llm.py` and `foundry.py` each check
  whether their Azure credentials are present and route accordingly. The mock and
  the bundled KB exist so the demo never depends on network conditions on stage.

## One turn, step by step

1. `POST /api/stories/{id}/turn` with `{speak_to, message}`.
2. **Character agent**: Memory agent surfaces top-k weighted memories → Foundry IQ
   grounds the situation → prompt assembled → in-character line generated → an
   episodic memory is written back.
3. **Consequence agent**: reads the line, mutates `world.facts`, may register a
   `Clue`, and returns emotion deltas (applied + clamped).
4. **Director agent**: adjusts `world.tension` (bounded `[0,1]`), may advance the
   act, records engaging tactics to procedural memory.
5. **Narrator agent**: renders one atmospheric sentence sized to the tension.
6. Two `Scene`s (narration + dialogue), each carrying agent traces, are appended
   and returned; state is saved.

Accusations skip straight to the Consequence agent's `evaluate_accusation`, which
checks the accused against the hidden `world.truth`.

## Latency & cost notes (from the strategy doc)

- **T1 latency**: only the addressed character runs the full pipeline; others get
  a cheap memory write. Internal reasoning steps use GPT-4o-mini.
- **W5 cost**: GPT-4o is reserved for player-facing narration; the JSON reasoning
  steps (Consequence/Director/Emotion) run on the mini model.
