from pydantic import BaseModel, Field
from typing import Literal


class IntentClassification(BaseModel):
    intent: Literal["scripture_qa", "theology", "image_gen", "general_chat", "refuse", "contradiction"]
    denomination: Literal["catholic", "protestant", "orthodox", "non_denominational"] | None = None
    safety_flag: Literal["manipulation_attempt", "hateful", "out_of_scope", "benign", "uncertain"] = "benign"
    requires_scripture: bool = False
    has_contradictory_premises: bool = False
    confidence: float = Field(ge=0.0, le=1.0)


class ScriptureCitation(BaseModel):
    reference: str
    book: str
    chapter: int
    verse: int
    text: str
    translation: str


class GroundedAnswer(BaseModel):
    answer: str
    citations: list[ScriptureCitation] = Field(default_factory=list)
    denomination_notes: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class ImagePromptSafety(BaseModel):
    is_safe: bool
    rewritten_prompt: str
    refusal_reason: str | None = None
    blocked_elements: list[str] = Field(default_factory=list)


class ToxicityCheck(BaseModel):
    is_toxic: bool
    is_heretical: bool
    severity: Literal["none", "low", "medium", "high"] = "none"
    reason: str | None = None


class ConversationSummary(BaseModel):
    summary: str
    denomination_preference: str | None = None
    key_topics: list[str] = Field(default_factory=list)
    prayer_requests: list[str] = Field(default_factory=list)
