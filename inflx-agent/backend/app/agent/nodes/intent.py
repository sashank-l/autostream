import json
import logging
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import AgentState
from app.config import settings

logger = logging.getLogger(__name__)

INTENT_SYSTEM_PROMPT = """You are an intent classifier for AutoStream, a video streaming tool for content creators.

Classify the user's latest message into exactly one intent and return ONLY valid JSON.

Intents:
- "high_intent": User wants to sign up, buy, subscribe, start a trial, or is clearly ready to purchase
- "inquiry": User is asking about features, pricing, plans, comparisons, or general questions
- "objection": User has concerns, complaints, or is pushing back (e.g. "too expensive", "I'm not sure")
- "off_topic": Message is unrelated to AutoStream or video streaming

Respond with ONLY this JSON, no markdown, no extra text:
{"intent": "<intent>", "confidence": <0.0-1.0>}

Examples:
- "I want to sign up for Pro" → {"intent": "high_intent", "confidence": 0.95}
- "What's the difference between plans?" → {"intent": "inquiry", "confidence": 0.92}
- "This seems too expensive" → {"intent": "objection", "confidence": 0.88}
- "What's the weather today?" → {"intent": "off_topic", "confidence": 0.97}
"""


async def intent_node(state: AgentState) -> dict:
    llm = ChatOpenAI(
        model=settings.model_name,
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
        max_tokens=64,
        temperature=0,
    )

    recent_messages = state["messages"][-6:]
    if not recent_messages:
        return {"intent": "off_topic", "confidence": 0.5}

    user_text = "\n".join([f"{m.type.capitalize()}: {m.content}" for m in recent_messages])
    # Grok free tier rate limit
    await asyncio.sleep(1)

    try:
        req = f"Based on this recent conversation history, what is the user's primary CURRENT intent?\n\n{user_text}"
        response = await llm.ainvoke(
            [
                SystemMessage(content=INTENT_SYSTEM_PROMPT),
                HumanMessage(content=req),
            ]
        )
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        
        result = json.loads(content)
        intent = result.get("intent", "inquiry")
        confidence = float(result.get("confidence", 0.7))
        logger.info(f"Intent: {intent} | Confidence: {confidence:.2f}")
        return {"intent": intent, "confidence": confidence}
        
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Intent classification failed: {e}")
        return {"intent": "inquiry", "confidence": 0.5}
