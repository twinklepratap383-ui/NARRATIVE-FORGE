# Agents

NarrativeForge runs five agents per turn plus a memory helper. Each emits
reasoning traces surfaced in the demo's Reasoning Panel.

| Agent | Responsibility | State | Model |
|---|---|---|---|
| **Character** | In-character response toward a hidden goal; deflects under pressure | per-character: memory, emotions, knowledge | GPT-4o |
| **Memory** | Recency + importance weighted recall feeding the Character agent | reads character memory | none (ranking) |
| **Consequence** | Mutates world facts, extracts clues, computes emotion deltas, scores accusations | world state (ground truth) | GPT-4o-mini |
| **Director** | Paces tension in waves, advances acts, records winning tactics | tension, act, procedural memory | GPT-4o-mini |
| **Narrator** | Cinematic connective prose around each beat | stateless | GPT-4o |

## Execution order (acyclic — strategy doc T2)

```
player input → Character → Consequence → Director → Narrator → output
```

No circular dependencies: the Character speaks first, the Consequence agent reads
that line to update the world, the Director reads the updated world to pace, the
Narrator frames the result. Other (non-addressed) characters only take a cheap
memory write so they stay aware without adding latency (T1 mitigation).

## Character reasoning

Each Character Agent builds its system prompt from:

1. **Identity** — name, role, personality, public stance.
2. **Secret goal** — never stated, but colours every line (e.g. Lady Ashworth
   protects her son; Crane hides being cut out of the firm).
3. **Foundry IQ grounding** — narrative-craft passages retrieved for the current
   dramatic situation (partial-truth technique, period restraint, etc.).
4. **Memory** — recency/importance-weighted recall.
5. **Stress** — derived from the emotion state; above 0.6 the character switches
   from candour to deflection.

## Foundry IQ — beyond retrieval

`foundry.py` does two things to address the "thin integration" critique (W2):

- **Semantic grounding** — ranks narrative-theory passages for the situation.
- **Procedural memory** — records tactics that raised player engagement, so across
  sessions the Director can prefer what worked (strategy doc Upgrade 3).

Offline it uses a bundled corpus; with a Foundry project configured the same calls
hit the real knowledge base.

## Emotions

Six axes per character in `[0,1]`: fear, trust, anger, love, loyalty, confidence.
A single derived `stress` signal drives Character deflection and Director pacing.
The Consequence agent emits per-turn deltas; the engine clamps them to range.
