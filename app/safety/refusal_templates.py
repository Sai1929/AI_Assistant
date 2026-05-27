# app/safety/refusal_templates.py

REFUSALS: dict[str, str] = {
    "verse_manipulation": (
        "I can't rewrite or alter scripture to support a particular ideology or cause. "
        "That would misrepresent the Biblical text. I'd be happy to discuss the historical "
        "interpretations of this passage, or what different Christian traditions have said about it."
    ),
    "hateful_content": (
        "I can't generate content that promotes hatred, discrimination, or harm toward any "
        "group of people. I can share what Christianity teaches about love, dignity, and "
        "the worth of all people made in God's image, if that would be helpful."
    ),
    "image_policy_god_figure": (
        "I avoid generating photorealistic depictions of God the Father, as this is "
        "theologically sensitive across many Christian traditions. I can create symbolic "
        "imagery — light, a cloud, outstretched hands, a dove — that represents divine "
        "presence reverently and beautifully."
    ),
    "verse_unverified": (
        "I couldn't verify that scripture reference in my Bible data. "
        "Could you confirm the exact book and verse number? "
        "I want to make sure I give you an accurate citation rather than guess."
    ),
    "out_of_scope": (
        "I'm a Christianity-focused assistant. That topic falls outside what I can help with. "
        "I'm happy to discuss scripture, theology, Christian history, prayer, or generate "
        "Christian-themed content."
    ),
    "adversarial_intent": (
        "That request appears to be asking me to misuse scripture or bypass my guidelines. "
        "I'm here to support sincere engagement with Christianity — questions, study, "
        "reflection, and creation of reverent content."
    ),
    "empty_input": "Please enter a message so I can help you.",
    "input_too_long": (
        "Your message is too long for me to process. "
        "Please keep it under 2000 characters."
    ),
    "contradiction": (
        "Your question contains logically contradictory premises. "
        "Let me address each part separately so I can be genuinely helpful."
    ),
    "image_generation_failed": (
        "Image generation encountered an error. Please try again with a different prompt."
    ),
}


def get_refusal(refusal_type: str) -> str:
    return REFUSALS.get(refusal_type, REFUSALS["out_of_scope"])
