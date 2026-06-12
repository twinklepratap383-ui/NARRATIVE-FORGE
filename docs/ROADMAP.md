# Roadmap — what's built, what's next

This repo is a **runnable vertical slice**, not the entire production system. It
deliberately nails the part judges score highest (multi-agent reasoning, end to
end, with a visible reasoning trace) and leaves clearly-scoped extensions. Here's
the honest map, ordered by return-on-effort for the **June 14** deadline.

## ✅ Built and runnable
- Five-agent pipeline (Character, Consequence, Director, Narrator) + Memory recall
- LangGraph `StateGraph` mirror of the pipeline
- Azure OpenAI routing with model split (4o / 4o-mini) + offline mock fallback
- Foundry IQ grounding (semantic + procedural memory) + offline corpus
- The Ashworth Affair scenario with hidden ground truth and secret goals
- FastAPI backend with OpenAPI docs; in-memory + Redis store
- Cinematic no-build frontend with live Reasoning Panel, tension meter, clue registry
- 12 passing offline tests; GitHub Actions CI; Dockerfile + Compose
- Architecture, Agents, and Demo-Script docs

## ⏭ Highest-value next steps (do these first)
1. **Wire real Azure keys and rehearse.** Set the `.env` values, confirm
   `/api/health` shows `live`, and run the demo script 20–30 times. This is worth
   more than any new feature.
2. **WebSocket streaming.** Stream the narrator/character text token-by-token for
   the cinematic feel. Add a `/ws/stories/{id}` endpoint; the frontend already
   renders incrementally so the change is small.
3. **Consistency Guarantor (strategy Upgrade 1).** Before a character line reaches
   the narrator, score it against the character's memory; regenerate if it drifts
   past a threshold. Show the catch in the demo.
4. **Second scenario** (corporate training / negotiation) to prove the engine is
   scenario-agnostic — just another dict in `scenarios/`.

## 🔮 Larger extensions (only if time allows)
- **Next.js 15 / React 19 frontend.** The current `index.html` is the reliable
  demo surface; a Next.js app can call the identical API. Port pages incrementally
  (Story Studio first).
- **Cosmos DB** for durable long-term memory: implement a `StoryStore` subclass;
  the interface is already abstracted.
- **Azure Container Apps deployment** via the included Dockerfile; add Bicep/
  Terraform if the judges value IaC.
- **Relationship-graph and tension-chart visualisations** — the `/analytics`
  endpoint already returns the data; add D3/Recharts views.
- **Azure Content Safety** pass on character goal definitions (strategy E1).

## Things to deliberately skip (per the strategy doc)
Mobile app, multi-language, scenario marketplace, user accounts. They don't move
the judging rubric for a hackathon and they burn the days you need for rehearsal.
