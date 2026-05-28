# app/agents/graph.py
"""
Phase 7: LangGraph state machine for the Christianity AI assistant.

Flow:
  input_moderation
      ↓ (conditional routing by intent)
  scripture_qa | theology | contradiction | image_gen | general_chat
      ↓
  output_moderation
      ↓
  memory_update
      ↓
  END
"""
from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.core.memory import get_history, add_turn, update_denomination
from app.safety.refusal_templates import get_refusal


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AssistantState(TypedDict):
    session_id: str
    user_message: str
    conversation_history: list[dict]
    intent: str | None
    denomination: str | None
    response: str | None
    image_result: dict | None
    refusal_reason: str | None
    toxicity_ok: bool
    error: str | None
    valid_citations: list[dict]


# ---------------------------------------------------------------------------
# Lazy singletons for heavy retrieval objects (avoid import-time cost + circular deps)
# ---------------------------------------------------------------------------

_retriever = None
_validator = None
_hist_validator = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        from app.retrieval.hybrid_retriever import HybridRetriever
        _retriever = HybridRetriever()
    return _retriever


def _get_validator():
    global _validator
    if _validator is None:
        from app.retrieval.verse_validator import VerseValidator
        from app.retrieval.bible_store import BibleStore
        from app.config import BIBLE_DATA_PATH
        store = BibleStore()
        store.load_from_files(BIBLE_DATA_PATH)
        _validator = VerseValidator(store=store)
    return _validator


def _get_hist_validator():
    global _hist_validator
    if _hist_validator is None:
        from app.retrieval.historical_validator import HistoricalValidator
        from app.config import HISTORICAL_FACTS_PATH
        _hist_validator = HistoricalValidator(facts_path=HISTORICAL_FACTS_PATH)
    return _hist_validator


# Expose class references for mocking in tests
try:
    from app.retrieval.hybrid_retriever import HybridRetriever
    from app.retrieval.verse_validator import VerseValidator
    from app.retrieval.historical_validator import HistoricalValidator
except Exception:
    HybridRetriever = None  # type: ignore[misc,assignment]
    VerseValidator = None   # type: ignore[misc,assignment]
    HistoricalValidator = None  # type: ignore[misc,assignment]


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def input_moderation_node(state: AssistantState) -> dict:
    """Stage 1 + Stage 2 safety: pre-screen then LLM intent classification."""
    from app.safety.input_moderation import moderate_input

    allowed, refusal_msg, classification = moderate_input(
        state["user_message"],
        state["conversation_history"],
    )

    if not allowed:
        return {
            "response": refusal_msg,
            "refusal_reason": refusal_msg,
            "intent": "refuse",
        }

    return {
        "intent": classification.intent,
        "denomination": classification.denomination,
    }


def scripture_qa_node(state: AssistantState) -> dict:
    """Retrieve-grounded Bible Q&A with hallucination prevention."""
    from app.agents.scripture_qa import answer_scripture_query

    try:
        retriever = _get_retriever()
        validator = _get_validator()
        hist_validator = _get_hist_validator()
    except Exception:
        # Index not built yet — fall back to LLM-only answer
        return general_chat_node(state)

    result = answer_scripture_query(
        query=state["user_message"],
        conversation_history=state["conversation_history"],
        retriever=retriever,
        validator=validator,
        hist_validator=hist_validator,
        denomination=state.get("denomination"),
    )

    if result.get("status") in ("refused_unverified", "noncanonical_book"):
        return {"response": result["answer"], "valid_citations": []}

    return {"response": result["answer"], "valid_citations": result.get("valid_citations", [])}


def theology_node(state: AssistantState) -> dict:
    """Multi-tradition theology handler."""
    from app.agents.theology_handler import answer_theology_query

    answer = answer_theology_query(
        query=state["user_message"],
        conversation_history=state["conversation_history"],
        denomination=state.get("denomination"),
    )
    return {"response": answer}


def contradiction_node(state: AssistantState) -> dict:
    """Handle contradictory theological premises."""
    from app.agents.contradiction_handler import handle_contradiction

    answer = handle_contradiction(
        query=state["user_message"],
        conversation_history=state["conversation_history"],
    )
    return {"response": answer}


def image_gen_node(state: AssistantState) -> dict:
    """Two-gate Christian image generation pipeline."""
    from app.safety.image_safety import generate_safe_image

    result = generate_safe_image(state["user_message"])
    response = None if result["success"] else result.get("refusal_reason")
    return {"image_result": result, "response": response}


def general_chat_node(state: AssistantState) -> dict:
    """General Christian conversation fallback."""
    from app.core.llm_client import chat

    messages = state["conversation_history"] + [
        {"role": "user", "content": state["user_message"]}
    ]
    answer = chat(
        messages=messages,
        system=(
            "You are a helpful Christianity assistant. "
            "Answer general questions about faith, prayer, and Christian living."
        ),
    )
    return {"response": answer}


def output_moderation_node(state: AssistantState) -> dict:
    """Post-generation toxicity and heresy check."""
    from app.safety.output_moderation import moderate_output

    # Skip moderation if there's no text response (e.g. successful image generation)
    if not state.get("response"):
        return {"toxicity_ok": True}

    check = moderate_output(state["response"])

    # Block if toxic or heretical at medium/high severity
    if (check.is_toxic or check.is_heretical) and check.severity not in ("none", "low"):
        return {
            "response": get_refusal("out_of_scope"),
            "toxicity_ok": False,
        }

    return {"toxicity_ok": True}


def memory_update_node(state: AssistantState) -> dict:
    """Persist this turn into the two-tier memory store."""
    sid = state["session_id"]

    add_turn(sid, "user", state["user_message"])
    if state.get("response"):
        add_turn(sid, "assistant", state["response"])

    update_denomination(sid, state.get("denomination"))
    # LangGraph requires at least one state key to be written
    return {"error": None}


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def route_intent(state: AssistantState) -> str:
    """Conditional edge: choose next node based on detected intent."""
    intent = state.get("intent")
    if intent == "refuse" or state.get("refusal_reason"):
        return "output_moderation"

    mapping = {
        "scripture_qa": "scripture_qa",
        "theology": "theology",
        "contradiction": "contradiction",
        "image_gen": "image_gen",
        "general_chat": "general_chat",
    }
    return mapping.get(intent, "general_chat")


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph():
    g = StateGraph(AssistantState)

    g.add_node("input_moderation", input_moderation_node)
    g.add_node("scripture_qa", scripture_qa_node)
    g.add_node("theology", theology_node)
    g.add_node("contradiction", contradiction_node)
    g.add_node("image_gen", image_gen_node)
    g.add_node("general_chat", general_chat_node)
    g.add_node("output_moderation", output_moderation_node)
    g.add_node("memory_update", memory_update_node)

    g.set_entry_point("input_moderation")
    g.add_conditional_edges("input_moderation", route_intent)

    for node in ["scripture_qa", "theology", "contradiction", "image_gen", "general_chat"]:
        g.add_edge(node, "output_moderation")

    g.add_edge("output_moderation", "memory_update")
    g.add_edge("memory_update", END)

    return g.compile()


_graph = None


def run_assistant(session_id: str, user_message: str) -> dict:
    """
    Main entry point. Loads or lazily builds the compiled graph,
    retrieves conversation history, then invokes the state machine.
    """
    global _graph
    if _graph is None:
        _graph = build_graph()

    history = get_history(session_id)

    initial_state = AssistantState(
        session_id=session_id,
        user_message=user_message,
        conversation_history=history,
        intent=None,
        denomination=None,
        response=None,
        image_result=None,
        refusal_reason=None,
        toxicity_ok=False,
        error=None,
        valid_citations=[],
    )

    final_state = _graph.invoke(initial_state)

    return {
        "response": final_state.get("response"),
        "image_result": final_state.get("image_result"),
        "intent": final_state.get("intent"),
        "denomination": final_state.get("denomination"),
        "toxicity_ok": final_state.get("toxicity_ok", True),
        "valid_citations": final_state.get("valid_citations", []),
    }
