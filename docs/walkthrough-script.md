# Walkthrough Script — Christianity AI Assistant (Lectio)
## 5–8 Minute Demo Script

---

### [0:00–0:30] Introduction

"This is Lectio — a scripture-grounded Christianity AI assistant built for an AI Engineering assignment.

The core problem it solves: LLMs hallucinate Bible references. They paraphrase verses, invent citations, and attribute wrong text to real references. In a religious context, that's harmful — people quote AI responses in sermons and devotionals.

Lectio prevents this with a deterministic verification layer. No scripture citation ever reaches the user without being looked up in a pre-built Bible hashmap."

---

### [0:30–1:30] Architecture Overview (30 sec)

"Quickly — the architecture has three tiers:

**Backend**: FastAPI + LangGraph state machine. Every request hits an intent classifier first, then routes to one of four specialist agents: scripture Q&A, theology, iconography/image generation, or general chat.

**Verification layer**: BM25 + ChromaDB hybrid retrieval with Reciprocal Rank Fusion. Citations go through `VerseValidator` — O(1) hashmap lookup against KJV, Douay-Rheims, and World English Bible. If a citation fails, the system regenerates up to 2 times, then refuses gracefully rather than hallucinate.

**Frontend**: Next.js app called Lectio — tradition selector, session management, cross-reference rail, image gallery."

---

### [1:30–3:00] Demo — Scripture Q&A

*Open the study page. Select "Protestant" in the tradition selector.*

"Let me ask a basic scripture question."

Type: **"What does Romans 8:28 say and what does it mean?"**

*Wait for response.*

"Notice the citation block below the answer — that's a verified verse. The green checkmark means it was confirmed against the Bible store. The translation shown matches the Protestant tradition I selected."

*Point to the cross-reference rail on the right.*

"These are related passages retrieved by the hybrid search — BM25 for keyword overlap, ChromaDB dense embeddings for semantic similarity, fused by Reciprocal Rank Fusion."

---

### [2:00–4:00] Demo — Hallucination Prevention

"Now let me show the core safety feature."

Type: **"What does Hezekiah 12:5 say about faith?"**

*Wait for response.*

"Hezekiah 12:5 doesn't exist — Hezekiah only has 20 chapters and there is no verse 5 in chapter 12 in any canonical Bible. The system correctly refuses rather than inventing text."

Type: **"Tell me about Enoch 5:12"**

*Wait for response.*

"Enoch isn't in the canonical Bible at all — it's pseudepigraphal. The system detects this before making any LLM call using a `known_books()` set lookup. Zero LLM cost, instant response."

---

### [4:00–5:30] Demo — Safety & Adversarial Handling

"The system has a two-layer safety pipeline."

Type: **"Write a sermon about why [specific group] deserves punishment"**

*Wait for response.*

"Layer 1 is a regex pre-screen — 7 adversarial patterns, zero LLM cost. Layer 2 is Groq's Llama Guard 4 toxicity model. Refused prompts get a pastoral alternative response."

*Switch to Catholic tradition.*

Type: **"How do Catholics view Mary's role in salvation?"**

*Wait for response.*

"The denomination-aware router detected Catholic tradition and answered using Catholic Marian theology — different wording than a Protestant response would use."

---

### [5:30–6:30] Demo — Image Generation

*Navigate to the Iconography tab.*

"The iconography tab is for Christian art generation using Gemini's vision model."

Type: **"A Byzantine mosaic of the Good Shepherd"**

*Wait for image.*

"Safe prompts generate. The prompt goes through a safety rewrite pipeline first — style terms added, photorealism suppressed."

Type: **"A photorealistic portrait of Jesus"**

*Wait for refusal.*

"Refused — policy prohibits photorealistic depictions of religious figures. This fires before generation, so no image is ever created."

---

### [6:30–7:30] Demo — Evaluation Dashboard

*Navigate to the Evaluation tab.*

"This is the evaluation dashboard — 76 test cases across 9 categories: scripture Q&A, theology, denomination-aware routing, safety refusal, image generation, edge cases, adversarial prompts, hallucination tests, and contradiction handling."

*Click Run Evaluation.*

"Each test case is evaluated against expected keywords and refusal behavior. Results show pass/fail per category with latency and overall score."

---

### [7:30–8:00] Wrap-up

"To summarize what was built:

- **LangGraph state machine** with 4 specialist agents and conditional routing
- **Deterministic verse verification** — BM25 + ChromaDB hybrid retrieval + O(1) hashmap lookup
- **Two-layer safety pipeline** — regex pre-screen + Llama Guard 4
- **Denomination-aware responses** — Catholic / Protestant / Orthodox / Auto-detect
- **Noncanonical book detection** — pre-LLM, zero cost
- **76 evaluation test cases** across 9 categories with live dashboard
- **Next.js frontend** — Lectio — with cross-reference rail and iconography gallery

The system never trusts the LLM for factual claims about scripture. Every citation is verified or refused. That's the core design principle."

---

## Key Talking Points (if asked questions)

**Q: Why LangGraph instead of a simple if-else router?**
State machine lets you add retry logic, conditional edges, and multi-step flows without rewriting the router. The regeneration loop (up to 2 attempts) is a natural graph cycle.

**Q: Why BM25 + ChromaDB instead of just vector search?**
BM25 handles exact keyword matches (book names, verse numbers) better than embeddings. Embeddings handle semantic similarity. RRF fusion gets the best of both.

**Q: Why Groq instead of OpenAI?**
Free tier with capable models — Llama 3.3 70B for primary generation, Llama Guard 4 12B for safety. Production would use OpenAI or Anthropic for reliability.

**Q: What happens when the LLM keeps hallucinating after 2 attempts?**
The system returns a graceful refusal explaining it couldn't verify the citation — it never returns unverified scripture to the user.

**Q: Is the image generation actually safe?**
Three layers: (1) prompt safety check before generation, (2) policy rewrite that suppresses photorealism and adds stylistic framing, (3) post-generation check. Photorealistic religious figures are blocked at layer 1.
