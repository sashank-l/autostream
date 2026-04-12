import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.agent.graph import run_graph
from app.agent.state import AgentState

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory session store: session_id → AgentState
_sessions: dict[str, AgentState] = {}


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str


def _get_or_create_session(session_id: str | None) -> tuple[str, AgentState]:
    if session_id and session_id in _sessions:
        return session_id, _sessions[session_id]

    new_id = session_id or str(uuid.uuid4())
    state: AgentState = {
        "session_id": new_id,
        "messages": [],
        "intent": None,
        "confidence": None,
        "retrieved_context": None,
        "citations": None,
        "collected": {},
        "has_fake_leads": False,
        "fake_reason": None,
        "lead_captured": False,
        "turn_count": 0,
        "streaming_tokens": [],
    }
    _sessions[new_id] = state
    return new_id, state


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id, state = _get_or_create_session(request.session_id)

    try:
        updated_state = await run_graph(session_id, request.message, state)
        _sessions[session_id] = updated_state
    except Exception as e:
        logger.error(f"Graph run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(session_id=session_id)


@router.get("/stream/{session_id}")
async def stream(session_id: str):
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = _sessions[session_id]

    async def event_generator() -> AsyncGenerator[str, None]:
        tokens = state.get("streaming_tokens", [])

        # Stream tokens
        for token in tokens:
            payload = json.dumps({"type": "token", "content": token})
            yield f"data: {payload}\n\n"
            await asyncio.sleep(0.01)  # slight delay for visual streaming effect

        # Emit metadata
        meta = {
            "type": "metadata",
            "intent": state.get("intent"),
            "confidence": state.get("confidence"),
            "citations": state.get("citations", []),
            "lead_captured": state.get("lead_captured", False),
        }
        yield f"data: {json.dumps(meta)}\n\n"

        # Done
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
