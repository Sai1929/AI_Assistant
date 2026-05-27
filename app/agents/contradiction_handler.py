# app/agents/contradiction_handler.py
def handle_contradiction(query: str, conversation_history: list[dict]) -> str:
    from app.core.llm_client import chat
    from app.prompts.system_prompts import CONTRADICTION_HANDLER

    messages = conversation_history[-4:] + [
        {"role": "user", "content": f"User prompt (contains contradictions): {query}"}
    ]
    return chat(messages=messages, system=CONTRADICTION_HANDLER)
