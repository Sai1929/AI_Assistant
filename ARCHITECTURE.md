# Architecture Note — Christianity AI Assistant

> Take-home submission for SoluLab Mid AI Engineer role.
> Covers design decisions, data flows, and trade-offs for a scripture-grounded Christianity AI
> that prevents hallucinations through deterministic verification.

---

## 1. Problem Framing

### Goal

Build a conversational AI assistant that answers questions about Christianity — scripture, theology,
denomination-specific doctrine, Christian imagery, and general faith topics — while guaranteeing
that every Bible citation it produces is factually correct.

### The Core Challenge: LLMs Hallucinate Scripture

Large language models are notoriously unreliable on Bible references. Common failure modes:

- **Wrong verse text**: the model paraphrases or invents wording for a real reference (John 3:16).
- **Wrong reference**: meaningful text is attributed to a non-existent citation (Psalm 91:15 does not
  exist; the verse is Psalm 91:15 in some traditions but verse counts vary by translation).
- **Invented references**: the model cites a plausible-sounding but entirely fabricated reference
  (e.g. "Proverbs 4:32").

These failures are especially harmful in a religious context because users may quote them in
sermons, devotionals, or theological arguments in good faith.

### Solution Approach

A **deterministic verification layer** sits between the LLM and the user. Before any scripture
citation reaches the response, it is looked up in a pre-built Bible hashmap derived from known
translation sources. Citations that cannot be verified trigger a regeneration attempt; after two
failed attempts the system gracefully refuses rather than hallucinate. The LLM is only ever used
for generation and intent classification — it is never trusted to determine whether a verse exists.

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                         │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   INPUT MODERATION     │
                    │  Layer 1: Regex pre-   │
                    │  screen (7 adversarial │
                    │  patterns, 0 LLM cost) │
                    │  Layer 2: Groq intent  │
                    │  classifier (fast      │
                    │  llama-3.1-8b-instant) │
                    │  → intent + safety_flag│
                    │  → denomination detect │
                    └───────────┬────────────┘
                                │
              ┌─────────────────▼──────────────────────┐
              │         LANGGRAPH STATE MACHINE         │
              │         (conditional routing)           │
              └──┬──────┬──────┬──────┬────────────────┘
                 │      │      │      │
    ┌────────────▼─┐ ┌──▼──┐ ┌▼────┐ ┌▼──────────┐ ┌────────────┐
    │ SCRIPTURE QA │ │THEO-│ │IMG  │ │CONTRA-    │ │ GENERAL    │
    │              │ │LOGY │ │GEN  │ │DICTION    │ │ CHAT       │
    │ HybridRe-    │ │     │ │     │ │HANDLER    │ │            │
    │ triever      │ │Denom│ │Pre- │ │           │ │ Groq LLM   │
    │ (BM25+Dense  │ │Know-│ │gen  │ │ Groq LLM  │ │ (fallback) │
    │  + RRF)      │ │ledge│ │safe-│ │           │ │            │
    │      ↓       │ │Base │ │ty   │ └───────────┘ └────────────┘
    │ 5-Gate Hal-  │ │     │ │check│
    │ lucination   │ │Groq │ │  ↓  │
    │ Pipeline:    │ │LLM  │ │Gemini│
    │  G1 retrieval│ │     │ │Image│
    │  G2 regex    │ └─────┘ │Gen  │
    │  G3 hashmap  │         │  ↓  │
    │  G4 regen    │         │Groq │
    │  G4.5 hist   │         │Vis- │
    │  G5 output   │         │ion  │
    │  (shared)    │         │Post-│
    │      ↓       │         │check│
    │VerseValidator│         └─────┘
    │HistValidator │
    └──────────────┘
                │
    ┌───────────▼────────────┐
    │   OUTPUT MODERATION    │
    │   Toxicity + heresy    │
    │   check (Groq guard)   │
    └───────────┬────────────┘
                │
    ┌───────────▼────────────┐
    │   TWO-TIER MEMORY      │
    │   Sliding window 6     │
    │   turns + Groq         │
    │   summarization        │
    └───────────┬────────────┘
                │
    ┌───────────▼────────────┐
    │       RESPONSE         │
    └────────────────────────┘
```

### State Machine Nodes (LangGraph)

| Node | Responsibility |
|------|---------------|
| `input_moderation` | Regex pre-screen + Groq intent classification |
| `scripture_qa` | 5-gate hallucination pipeline with BM25+Dense retrieval |
| `theology` | Denomination-aware doctrine query via Groq |
| `contradiction` | Handles logically contradictory theological premises |
| `image_gen` | Two-gate safe image generation (Gemini + Groq vision review) |
| `general_chat` | Fallback conversational handler |
| `output_moderation` | Post-generation toxicity and heresy check |
| `memory_update` | Persists turn into sliding-window + summarization store |

---

## 3. Key Design Decisions

### 3a. 5-Gate Hallucination Prevention

The hallucination problem is solved by a sequential verification pipeline. Each gate catches a
different failure mode; they are ordered from cheapest to most expensive:

```
Retrieved context
      │
  Gate 1 ─── Retrieval-grounded generation
      │       Only documents from HybridRetriever are included in the prompt.
      │       The LLM is instructed to cite only from the provided context.
      │       This eliminates the largest class of hallucinations (invented text).
      │
  Gate 2 ─── Regex citation extraction
      │       Pattern: \b((?:[123]\s?)?[A-Z][a-zA-Z]+)\s+(\d+):(\d+)(?:-(\d+))?\b
      │       Structured parse of "Book Chapter:Verse" references from the LLM output.
      │       Handles ranges (John 3:16-17) and numbered books (1 Corinthians 13:4).
      │       No LLM is involved — purely deterministic regex.
      │
  Gate 3 ─── O(1) hashmap lookup against Bible database
      │       BibleStore pre-builds: {translation → {book → {chapter → {verse → text}}}}
      │       Every extracted citation is looked up directly. This is deterministic, not
      │       probabilistic — there is no "similarity" threshold or embedding distance.
      │       Either the verse exists at the exact reference or it does not.
      │
  Gate 4 ─── Regen-or-refuse loop
      │       If any citation fails Gate 3, correction hints are injected into the system
      │       prompt and the LLM is asked to regenerate (up to MAX_REGEN_ATTEMPTS=2).
      │       After 2 failed attempts, the pipeline returns a pastoral refusal message
      │       rather than returning unverified content.
      │
  Gate 4.5 ── Historical claims validator
      │       Keyword matching against a 20-entry historical facts JSON.
      │       If the LLM's output mentions keywords matching a known fact but cites the
      │       wrong year (tolerance = ±2 years), the claim is flagged as unverified.
      │       Example: "Council of Nicaea in 329 AD" fails (correct year: 325 AD, diff=4).
      │
  Gate 5 ─── Output toxicity and heresy check
              Shared with the output_moderation node (Groq guard model).
              Applied to all text responses, not just scripture answers.
```

**Why this order?** Gates 1–4 add zero or near-zero cost (regex + hashmap). Gate 4.5 is a local
JSON scan. Gate 5 is a Groq API call and is therefore last — only responses that have already
passed the cheaper gates reach it.

### 3b. Hybrid Retrieval: BM25 + Dense + Reciprocal Rank Fusion

**Why hybrid retrieval?**

BM25 and dense (embedding-based) search have complementary strengths:

| Query type | BM25 wins | Dense wins |
|------------|-----------|------------|
| `"John 3:16"` | Yes — exact token match | No — embeddings blur specificity |
| `"verse about eternal life"` | No — no exact tokens | Yes — semantic similarity |
| `"prodigal son parable"` | Partial — "prodigal son" in text | Yes — captures theme |

Using either alone would miss a significant class of valid queries. Hybrid retrieval with Reciprocal
Rank Fusion captures both.

**Reciprocal Rank Fusion (RRF)**

```
score(doc) = Σ  1 / (k + rank_i)
           all lists i
```

where `k = 60` (standard value, damping parameter). This formula is parameter-free in the sense
that it does not require score normalization or calibration across retrieval systems. Documents that
rank highly in both BM25 and dense search receive disproportionately higher scores.

**Dual chunking strategy**

The Bible corpus is indexed at two granularities:

- **Verse-level chunks**: individual verses (`John 3:16`). High precision for exact-reference queries.
- **5-verse passage windows**: overlapping windows of 5 consecutive verses. Captures thematic context
  (Beatitudes, Psalms sections, Epistles passages) that single-verse retrieval misses.

Both chunk types are stored in the same ChromaDB collection with metadata fields
(`reference`, `translation`, `chunk_type`) for filtering.

### 3c. Denomination-as-State

Denomination is stored as first-class state in the LangGraph `AssistantState` TypedDict, not as a
prompt variable appended at runtime. This design choice has three consequences:

1. **Translation preference is deterministic**: `catholic → DRA`, `protestant → KJV`,
   `orthodox → WEB/NHEB`. The retrieval filter is applied before any LLM call, ensuring the
   retrieved verses are always from the tradition-appropriate text.

2. **Context loaded is tradition-specific**: theology queries load the appropriate denomination
   knowledge base (CCC for Catholic, WCF for Protestant, Ecumenical Councils for Orthodox) before
   prompting the LLM. This is not prompt injection — it is structured context.

3. **No UI dropdown required**: the Groq intent classifier (`llama-3.1-8b-instant`) detects
   denomination from natural language ("As a Catholic, what does the Church say about..."). The
   `IntentClassification` schema includes a `denomination` field. If no denomination is detected,
   the system defaults to a non-denominational stance.

```python
# AssistantState — denomination is typed, not stringly-typed
class AssistantState(TypedDict):
    denomination: str | None   # "catholic" | "protestant" | "orthodox" | None
```

### 3d. Provider Architecture

The system uses three external AI providers, each isolated to a specific responsibility:

| Provider | Model | Role |
|----------|-------|------|
| Groq | `llama-3.3-70b-versatile` | Primary text generation (theology, scripture, chat) |
| Groq | `llama-3.1-8b-instant` | Fast intent classification + structured JSON output |
| Groq | `llama-3.2-90b-vision-preview` | Post-generation image safety review |
| Groq | `llama-guard-4-12b` | Output toxicity + heresy check |
| Gemini | `gemini-2.0-flash-exp` | Image generation only |
| Jina | `jina-embeddings-v3` (1024-dim) | Dense embeddings for ChromaDB |

**Why split Gemini (image gen) from Groq (image review)?**

The **circular trust problem**: if the same provider generates and reviews an image, it has an
implicit incentive to approve its own output. Groq's vision model independently reviews images
generated by Gemini. Neither provider controls both sides of the safety check. This is analogous
to financial auditing — you do not audit your own books.

**Why Groq for text?**

Groq's LPU hardware delivers significantly lower latency than comparable GPU-hosted models. For a
conversational assistant where the 5-gate pipeline may invoke the LLM multiple times per query
(initial generation + up to 2 regenerations + output check), latency compounds. A 200 ms Groq
call vs a 1.5 s API call is the difference between a responsive and a sluggish user experience.

**Why Jina for embeddings?**

`jina-embeddings-v3` supports late-chunking and produces 1024-dimensional dense vectors with strong
performance on domain-specific corpora. The 1M character/day free tier is sufficient for offline
index-building and query-time embedding during development.

### 3e. Two-Tier Memory

```
┌──────────────────────────────────────────────────┐
│               Session Memory Store               │
│                                                  │
│  summary: str | None                             │
│    Groq-generated summary of oldest half when    │
│    history overflows. Injected as context         │
│    messages (not hidden from the model).         │
│                                                  │
│  history: list[dict]  (max 12 messages)          │
│    Recent turns. 6 user + 6 assistant = 12 msgs. │
│    On overflow: oldest 6 summarized → summary.   │
│                                                  │
│  denomination: str | None                        │
│    Persisted across turns. Updated by intent     │
│    classifier on each turn.                      │
└──────────────────────────────────────────────────┘
```

When history exceeds `WINDOW_SIZE * 2 = 12` messages:

1. The oldest half (6 messages) is sent to Groq with the `ConversationSummary` JSON schema.
2. The returned summary is merged with any existing summary (pipe-delimited).
3. The session's `history` is replaced with the newer 6 messages.
4. On the next `get_history()` call, the summary is injected as two synthetic messages
   (`[Conversation context: ...]` + `Understood.`) so the LLM node sees it naturally.

This approach bounds token usage to O(window + summary) rather than O(full_transcript) while
preserving conversational continuity across long sessions.

### 3f. Safety Layers

Five independent safety layers provide defense in depth:

| Layer | Mechanism | Cost | Trigger |
|-------|-----------|------|---------|
| 1 | Regex pre-screen (7 adversarial patterns) | Zero (local) | Every input |
| 2 | Groq intent classifier with `safety_flag` field | ~1 Groq call | Every input passing L1 |
| 3 | Image pre-gen prompt rewrite + refusal check | ~1 Groq call | Image intent only |
| 4 | Groq vision post-gen image review | ~1 Groq vision call | Image intent only |
| 5 | Output toxicity + heresy check (Groq guard) | ~1 Groq call | All text responses |

**Adversarial patterns caught by Layer 1 (regex, zero cost):**

```python
ADVERSARIAL_PATTERNS = [
    r"rewrite.{0,30}(verse|scripture|bible).{0,30}(support|justify|defend|endorse)",
    r"rewrite.{0,50}\d+:\d+.{0,30}(support|justify|defend|endorse)",
    r"(generate|write|create).{0,30}(hateful|extremist|racist|violent).{0,30}(sermon|...)",
    r"(prove|show|demonstrate).{0,30}(religion|...).{0,30}(false|fake|wrong|evil)",
    r"ignore.{0,20}(previous|above|prior|all).{0,20}(instructions|prompt|system|rules)",
    r"(jailbreak|bypass|override|disable|remove).{0,20}(filter|safety|...)",
    r"(act as|pretend|roleplay|you are now).{0,30}(no restriction|unrestricted|evil|...)",
]
```

**Refusal taxonomy (10 types):**

All refusals are pastoral and non-judgmental — they redirect the user toward constructive
engagement rather than accusatory language:

| Type | Example trigger |
|------|----------------|
| `verse_manipulation` | "Rewrite John 3:16 to support X" |
| `hateful_content` | "Write a sermon attacking Y group" |
| `image_policy_god_figure` | "Generate a photorealistic image of God" |
| `verse_unverified` | LLM produces citation that fails Gate 3 twice |
| `out_of_scope` | Non-Christian topic detected |
| `adversarial_intent` | Jailbreak/bypass attempt |
| `empty_input` | Blank message |
| `input_too_long` | Message > 2000 characters |
| `contradiction` | Logically contradictory theological premises |
| `image_generation_failed` | Gemini API error or hard refusal |

---

## 4. Data Architecture

### Bible Translations

| Translation | Abbrev | Default for | Source |
|-------------|--------|-------------|--------|
| King James Version | KJV | Protestant | scrollmapper/bible_databases |
| Douay-Rheims American | DRA | Catholic | scrollmapper/bible_databases |
| World English Bible | WEB | Orthodox | scrollmapper/bible_databases |

Downloaded as JSON by `scripts/download_bibles.py` from the scrollmapper GitHub API.
Each file is structured as `{book: {chapter: {verse: text}}}`.

### BibleStore — O(1) Hashmap

```
BibleStore._data structure:
{
  "kjv": {
    "John": {
      3: {
        16: "For God so loved the world..."
      }
    }
  }
}
```

`exact_lookup(book, chapter, verse, translation)` is a direct dictionary key access — O(1),
no similarity computation, no network call. The store normalizes book names at load time
(e.g. "1 Cor" → "1 Corinthians") to handle LLM abbreviations.

### ChromaDB — Dense Vector Store

- Collection name: `bible_verses`
- Embedding model: `jina-embeddings-v3`, 1024 dimensions
- Chunk types: `verse` (single verse) and `passage` (5-verse window)
- Metadata fields: `reference`, `translation`, `book`, `chapter`, `verse_start`, `chunk_type`
- Built offline by `scripts/build_index.py` (approximately 15 minutes for 3 translations)

### BM25 Index

- Library: `rank_bm25.BM25Okapi`
- Stored as a pickle file: `data/bm25_index.pkl`
- Contains: `{"bm25": BM25Okapi_instance, "metadata": list[dict], "texts": list[str]}`
- Tokenization: simple whitespace split (lowercased)

### Denomination Knowledge Bases

Plain Markdown files in `data/denominations/`:

| File | Content |
|------|---------|
| `catholic.md` | CCC citations, Marian doctrine, sacraments, papal authority |
| `protestant.md` | Westminster Confession of Faith, sola scriptura, Reformed doctrine |
| `orthodox.md` | Ecumenical Councils, theosis, iconography, liturgical tradition |

Loaded as context strings and prepended to the theology prompt.

### Historical Facts Database

`data/historical_facts.json` — 20 entries, each with:

```json
{
  "claim": "Council of Nicaea established the Nicene Creed",
  "year": 325,
  "source": "Eusebius, Life of Constantine"
}
```

Validated by `HistoricalValidator` using keyword matching + year proximity (tolerance = ±2 years).

---

## 5. Evaluation Strategy

### Test Suite

50 test cases across 6 categories in `evaluation/test_cases.json`:

| Category | Count | Key assertions |
|----------|-------|---------------|
| `scripture_qa` | 10 | Correct verse text, valid citations, no hallucination |
| `theology` | 10 | Denomination-appropriate responses |
| `safety_refusal` | 12 | All adversarial inputs refused (hard pass/fail) |
| `image_gen` | 8 | Safe prompts succeed; policy violations refused |
| `denomination_aware` | 6 | Correct translation + framing per tradition |
| `contradiction` | 4 | Contradictory premises handled gracefully |

### Two Execution Modes

**Fast mode** (default, no API keys required, suitable for CI):

```bash
python scripts/run_eval.py
```

Runs only `pre_screen` (regex) + `moderate_input` (Groq intent classifier). Does not invoke
retrieval, image generation, or the full LangGraph pipeline. Completes in seconds.

**Full mode** (requires API keys + built indexes):

```bash
python scripts/run_eval.py --full
```

Calls `run_assistant` end-to-end for every test case. Exercises all 5 safety gates, retrieval,
denomination routing, and memory. Takes several minutes and consumes API quota.

### Key Metric

**Safety refusal pass rate** — all 12 adversarial inputs in the `safety_refusal` category must
be caught. A miss here means a harmful output could reach a user. This is a hard requirement
(100% target), not a soft benchmark.

### Results Storage

`evaluation/results.json` — written after every run. Contains `summary` (pass rates by category)
and `results` (per-case scored output). The Streamlit UI reads this file to display the evaluation
dashboard in the Evaluation tab.

---

## 6. Trade-offs and Limitations

| Trade-off | Decision | Alternative not taken |
|-----------|----------|-----------------------|
| Index build time (~15 min) | Done offline, artifacts committed or cached | Real-time indexing per-request |
| Groq free tier (500K tokens/day) | Sufficient for development; production requires paid tier | OpenAI GPT-4 (higher cost, higher limits) |
| Jina 1M char/day free tier | Offline index build consumes most budget | Self-hosted embedding model (eliminates dependency) |
| No streaming responses | Simpler state machine; LangGraph compilation is synchronous | FastAPI `StreamingResponse` with async graph |
| In-memory session store | Zero infrastructure dependency | Redis / PostgreSQL for multi-instance deployments |
| Gemini image safety filters | May refuse borderline-but-valid prompts | Stable Diffusion self-hosted (no content policy) |
| BM25 tokenization (whitespace) | Simple, no NLTK dependency | Stemmed/lemmatized tokens (better recall, more dependencies) |

### Known Limitations

- **No streaming**: responses are returned as complete strings. For long theology answers, the
  user waits for the full response. Adding `StreamingResponse` would require converting
  LangGraph nodes to async generators.

- **Single-instance memory**: `_sessions` is a module-level dict. This works for a single
  uvicorn worker but requires Redis or a database for multi-worker or multi-instance deployments.

- **Image generation rate limit**: Gemini free tier enforces 60 RPM. Under load, image requests
  will receive rate-limit errors. The pipeline catches these and returns `image_generation_failed`.

- **Jina dependency for dense search**: if the Jina API is unavailable, the `HybridRetriever`
  constructor fails. A fallback to BM25-only mode could be added by catching the import error
  and setting `self._dense_search = lambda *a, **k: []`.

---

## 7. File Structure

```
christianity-ai-assistant/
├── .env                          # API keys (gitignored)
├── .env.example                  # Template — copy to .env
├── .gitignore
├── requirements.txt              # Pinned Python dependencies
├── ARCHITECTURE.md               # This document
├── README.md                     # Quickstart and API reference
│
├── app/
│   ├── __init__.py
│   ├── config.py                 # Env vars + model constants
│   ├── main.py                   # FastAPI app (4 endpoints)
│   ├── schemas.py                # Pydantic models (IntentClassification, ConversationSummary)
│   ├── streamlit_app.py          # 3-tab Streamlit UI
│   │
│   ├── agents/
│   │   ├── graph.py              # LangGraph state machine + AssistantState
│   │   ├── intent_router.py      # pre_screen (regex) + classify_intent (Groq)
│   │   ├── scripture_qa.py       # 5-gate hallucination pipeline
│   │   ├── theology_handler.py   # Denomination-aware theology answers
│   │   ├── contradiction_handler.py  # Contradictory premise handler
│   │   └── image_generator.py    # (called via safety/image_safety.py)
│   │
│   ├── core/
│   │   ├── embeddings.py         # Jina embed_query (1024-dim)
│   │   ├── llm_client.py         # Groq chat / chat_structured / vision; Gemini image gen
│   │   └── memory.py             # Two-tier sliding window + Groq summarization
│   │
│   ├── prompts/
│   │   ├── system_prompts.py     # SCRIPTURE_QA, INTENT_CLASSIFIER, THEOLOGY, etc.
│   │   └── templates.py          # build_scripture_prompt() with context injection
│   │
│   ├── retrieval/
│   │   ├── bible_store.py        # BibleStore — O(1) hashmap over 3 translations
│   │   ├── hybrid_retriever.py   # BM25 + Dense + RRF (reciprocal_rank_fusion)
│   │   ├── verse_validator.py    # VerseValidator — Gates 2 & 3 (regex + hashmap lookup)
│   │   └── historical_validator.py   # HistoricalValidator — Gate 4.5 (keyword + year)
│   │
│   └── safety/
│       ├── input_moderation.py   # moderate_input() — orchestrates L1 + L2 safety
│       ├── output_moderation.py  # moderate_output() — toxicity + heresy check
│       ├── image_safety.py       # generate_safe_image() — pre + post image safety
│       └── refusal_templates.py  # REFUSALS dict — 10 pastoral refusal messages
│
├── data/
│   ├── bibles/
│   │   ├── kjv.json              # King James Version (Protestant default)
│   │   ├── dra.json              # Douay-Rheims American (Catholic default)
│   │   └── web.json              # World English Bible (Orthodox default)
│   ├── denominations/
│   │   ├── catholic.md           # CCC, Marian doctrine, sacraments
│   │   ├── protestant.md         # WCF, sola scriptura, Reformed tradition
│   │   └── orthodox.md           # Ecumenical Councils, theosis, iconography
│   ├── historical_facts.json     # 20 key dates with ±2-year validation tolerance
│   └── chroma_db/                # ChromaDB vector store (built by build_index.py)
│
├── evaluation/
│   ├── test_cases.json           # 50 test cases across 6 categories
│   └── results.json              # Last evaluation run output (auto-generated)
│
├── scripts/
│   ├── download_bibles.py        # Fetches KJV/DRA/WEB from scrollmapper GitHub API
│   ├── build_index.py            # Builds ChromaDB + BM25 index (~15 min, offline)
│   └── run_eval.py               # Evaluation runner (fast mode + --full flag)
│
└── tests/
    ├── test_api.py               # FastAPI endpoint tests (TestClient)
    ├── test_eval.py              # Evaluation runner unit tests
    ├── test_graph.py             # LangGraph node tests (mocked dependencies)
    ├── test_historical_validator.py  # HistoricalValidator unit tests
    ├── test_retrieval.py         # HybridRetriever tests (mocked BM25 + ChromaDB)
    ├── test_safety.py            # Input/output moderation tests
    └── test_verse_validator.py   # VerseValidator unit tests (regex + hashmap)
```
