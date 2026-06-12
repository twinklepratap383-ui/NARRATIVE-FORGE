# Demo Script — 3 minutes

Adapted from the strategy doc, tuned to exactly what this build does. Run the
backend, open `http://localhost:8000`, and keep the **Reasoning** toggle ON.

## 0:00–0:20 — Hook
> *"What if an AI character could genuinely lie to you — and mean it?"*

Point at the suspects panel. *"Three suspects. Each is its own agent with memory,
emotions, and a secret it's protecting. This is NarrativeForge — not a chatbot, a
multi-agent narrative intelligence."*

## 0:20–0:45 — The reasoning is visible
Ask **Lady Ashworth**: *"Where were you the night your husband died?"*

As the answer streams in, scroll to the trace under her line. Read it aloud:
- `memory_retrieval` — surfaced her relevant memories
- `foundry_iq` — grounded in narrative craft (partial-truth / period restraint)
- `conflict_analysis` — *stress level, secret goal at risk, choosing deflection*
- `decision` — delivered a line consistent with her hidden goal

> *"Every response is reasoned, not just generated."*

## 0:45–1:30 — Pressure changes behaviour
Press her twice more: *"The butler says the library was empty."* / *"Why was your
gown wet?"* Watch the **tension meter** climb and her **fear/confidence** bars move
in the panel. At higher stress her replies shift from candour to deflection — point
that out. A **clue** appears in the Clue Registry; call it out.

## 1:30–2:15 — Cross-character awareness
Switch to **Mr. Hargrove** (the butler). Ask: *"Did you see anything unusual?"*
Note that he already carries a memory that Lady Ashworth was questioned — the
agents share a world. Then question **Mr. Crane** about the business partnership;
his confidence/anger bars reflect a different personality entirely.

## 2:15–2:45 — Solve it
Select **Mr. Crane** and hit **Make Accusation**. The Consequence agent checks the
accusation against the hidden ground truth and the Narrator delivers the
resolution. (Accuse the wrong suspect first if you want to show the mystery *holds*
— then correct it.)

## 2:45–3:00 — Close
> *"Same engine, any scenario: corporate training, historical education,
> interactive fiction. Grounded in Microsoft Foundry IQ, orchestrated as a
> LangGraph pipeline. We didn't script this story — the agents reasoned it."*

## Tips
- Keep a backup screen recording running.
- If you have Azure keys set, mention the health check shows `azure_openai: live`.
- The mock LLM is deterministic — rehearse the exact questions so pacing is tight.
