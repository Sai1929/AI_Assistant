# Christianity AI Assistant

A scripture-grounded conversational AI that prevents hallucinations through deterministic verse
verification — every Bible citation is looked up in a pre-built hashmap before it reaches the user.

---

## Features

- **5-Gate Hallucination Prevention** — regex citation extraction, O(1) hashmap lookup against
  KJV/DRA/WEB Bible databases, up to 2 LLM regeneration attempts, historical claims validation,
  and output toxicity review; the system refuses gracefully rather than hallucinate
- **Hybrid Retrieval (BM25 + Dense + RRF)** — Reciprocal Rank Fusion merges BM25 keyword search
  with Jina 1024-dim dense embeddings across dual-chunked verse-level and 5-verse passage windows
- **Denomination-Aware Routing** — Catholic, Protestant, and Orthodox traditions are first-class
  state; translation preference (DRA/KJV/WEB), knowledge base context, and response framing adapt
  automatically; denomination is detected from natural language, no UI dropdown required
- **LangGraph State Machine** — 8-node compiled graph with typed `AssistantState`; routing is
  data-driven, not hard-coded; nodes are independently testable with mocked dependencies
- **Multi-Provider Safety** — Groq vision model independently reviews Gemini-generated images,
  eliminating the circular trust problem of same-provider generation and review
- **Two-Tier Conversation Memory** — 6-turn sliding window with Groq summarization overflow;
  summaries injected as context messages to preserve history without token bloat
- **Defense-in-Depth Safety** — 5 independent safety layers: regex pre-screen (zero LLM cost),
  LLM intent classifier with safety flag, image pre-gen rewrite, post-gen vision review, and
  output heresy check; 10-type pastoral refusal taxonomy
- **FastAPI REST API + Streamlit UI** — production-ready REST backend with 4 endpoints and a
  3-tab Streamlit interface (Chat, Image Generation, Evaluation Dashboard)
- **Offline-Built Indexes** — BM25 and ChromaDB indexes are built once from downloaded Bible
  translations; runtime retrieval requires no indexing overhead
- **Structured Evaluation Suite** — 50 test cases across 6 categories with fast CI mode
  (no API keys) and full end-to-end mode; results feed directly into the Streamlit dashboard

---

## Architecture

The system is built around a LangGraph state machine that routes user input through specialized
nodes — scripture QA, theology, image generation, contradiction handling, and general chat. All
text responses pass through a 5-gate hallucination prevention pipeline and output moderation
before reaching the user. See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design note
including system diagrams, provider rationale, and trade-off analysis.

---

## Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd christianity-ai-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env — add your API keys:
#   GROQ_API_KEY    — https://console.groq.com
#   GEMINI_API_KEY  — https://aistudio.google.com/app/apikey
#   JINA_API_KEY    — https://jina.ai (free tier: 1M chars/day)

# 4. Download Bible translations (KJV, DRA, WEB from scrollmapper)
python scripts/download_bibles.py

# 5. Build search indexes (ChromaDB + BM25, ~15 min)
python scripts/build_index.py

# 6a. Launch the Streamlit UI
streamlit run app/streamlit_app.py

# 6b. Or run the FastAPI backend
uvicorn app.main:app --reload
# API docs available at http://localhost:8000/docs
```

---

## API Reference

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Liveness check — returns `{"status": "ok", "model": "<model>"}` |
| `POST` | `/chat` | Send a message and receive a scripture/theology/image response |
| `DELETE` | `/session/{session_id}` | Clear conversation memory for a session |
| `GET` | `/session/{session_id}/history` | Retrieve conversation history for a session |

### POST /chat

**Request body:**

```json
{
  "session_id": "string",
  "message": "string"
}
```

**Response:**

```json
{
  "session_id": "string",
  "response": "string | null",
  "image_b64": "string | null",
  "intent": "scripture_qa | theology | image_gen | contradiction | general_chat | refuse",
  "denomination": "catholic | protestant | orthodox | null",
  "toxicity_ok": true
}
```

Interactive docs with request examples are available at `http://localhost:8000/docs` when the
server is running.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key (required) | — |
| `GEMINI_API_KEY` | Google Gemini API key (required for image generation) | — |
| `JINA_API_KEY` | Jina AI API key (required for dense embeddings) | — |
| `CHROMA_DB_PATH` | Path to ChromaDB persistence directory | `./data/chroma_db` |
| `BM25_INDEX_PATH` | Path to pickled BM25 index file | `./data/bm25_index.pkl` |
| `BIBLE_DATA_PATH` | Directory containing Bible JSON files | `./data/bibles` |
| `DENOM_DATA_PATH` | Directory containing denomination Markdown files | `./data/denominations` |
| `HISTORICAL_FACTS_PATH` | Path to historical facts JSON | `./data/historical_facts.json` |
| `MAX_REGEN_ATTEMPTS` | Max LLM regeneration attempts in hallucination pipeline | `2` |
| `MEMORY_WINDOW_SIZE` | Sliding window size (turns, not messages) | `6` |
| `BM25_TOP_K` | Number of BM25 results before fusion | `5` |
| `DENSE_TOP_K` | Number of dense results before fusion | `5` |
| `FUSED_TOP_K` | Number of results after RRF fusion | `3` |

---

## Running Tests

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run a specific test module
python -m pytest tests/test_verse_validator.py -v
python -m pytest tests/test_safety.py -v
python -m pytest tests/test_historical_validator.py -v

# Tests that do NOT require API keys (run in CI):
#   test_verse_validator.py   — regex + hashmap logic
#   test_historical_validator.py — keyword + year matching
#   test_safety.py            — regex pre-screen patterns
#   test_retrieval.py         — BM25 + RRF logic (mocked ChromaDB)
#   test_graph.py             — LangGraph node logic (mocked LLM)

# Tests that require API keys (Groq + Gemini + Jina):
#   test_api.py               — FastAPI endpoints calling run_assistant
#   test_eval.py              — Full evaluation pipeline
```

---

## Running Evaluation

```bash
# Fast mode — no API keys required, tests safety gates only (~seconds)
python scripts/run_eval.py

# Full mode — end-to-end pipeline, requires API keys + built indexes (~minutes)
python scripts/run_eval.py --full

# Custom output path
python scripts/run_eval.py --output evaluation/my_results.json

# Custom test cases file
python scripts/run_eval.py --cases evaluation/test_cases.json
```

Fast mode validates the regex pre-screen and Groq intent classifier across all 50 test cases.
This is suitable for CI where API keys may not be available. The critical `safety_refusal` category
(12 adversarial inputs) is fully exercised in fast mode because adversarial patterns are caught
by the regex pre-screen before any LLM call.

Full mode invokes the complete `run_assistant` pipeline including retrieval, image generation, and
the 5-gate hallucination pipeline. Results are saved to `evaluation/results.json` and displayed
in the Streamlit Evaluation tab.

---

## Design Highlights

The most significant technical choice is the **deterministic verse verification layer**: rather
than asking the LLM to check its own citations (which fails because the model cannot reliably
introspect its own knowledge), the system extracts citations via regex and performs an O(1)
hashmap lookup against pre-built Bible data — a lookup that either succeeds or fails with no
probabilistic middle ground. The **Reciprocal Rank Fusion** approach to hybrid retrieval is
parameter-free in the sense that it requires no score calibration between BM25 and dense systems,
which makes it robust to distribution shift across translations. The **circular trust problem**
in image safety is solved by using Groq's vision model to review images generated by Gemini —
the generator and reviewer are always different providers with different training data and
incentives. Finally, **denomination-as-state** (not prompt variable) means translation filtering
happens at the retrieval level before the LLM sees any context, ensuring that a Catholic user
asking about John 3:16 always gets the Douay-Rheims text without requiring the LLM to apply the
correct translation label.

---

## Tech Stack

| Provider | Model | Used For |
|----------|-------|----------|
| Groq | `llama-3.3-70b-versatile` | Primary text generation (scripture, theology, chat) |
| Groq | `llama-3.1-8b-instant` | Fast intent classification + structured JSON output |
| Groq | `llama-3.2-90b-vision-preview` | Post-generation image safety review |
| Groq | `llama-guard-4-12b` | Output toxicity + heresy check |
| Gemini | `gemini-2.0-flash-exp` | Image generation |
| Jina | `jina-embeddings-v3` (1024-dim) | Dense embeddings for ChromaDB |
| LangGraph | 0.2.35 | State machine orchestration |
| ChromaDB | 0.5.18 | Dense vector store (dual-chunk Bible corpus) |
| rank-bm25 | 0.2.2 | BM25Okapi keyword index |
| FastAPI | 0.115.5 | REST API backend |
| Streamlit | 1.40.1 | Chat + image + evaluation UI |
