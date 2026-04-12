from typing import TypedDict, Optional, Any
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import Annotated


class AgentState(TypedDict):
    session_id: str
    messages: Annotated[list[BaseMessage], add_messages]
    intent: Optional[str]          # "inquiry" | "high_intent" | "objection" | "off_topic"
    confidence: Optional[float]    # 0.0 – 1.0
    retrieved_context: Optional[str]
    citations: Optional[list[str]]
    collected: dict[str, str]      # {"name": "...", "email": "...", "platform": "..."}
    has_fake_leads: bool
    fake_reason: Optional[str]
    lead_captured: bool
    turn_count: int
    streaming_tokens: list[str]
