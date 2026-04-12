import json
import logging
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import AgentState
from app.config import settings

logger = logging.getLogger(__name__)

EXTRACTOR_SYSTEM_PROMPT = """Analyze the conversaton and extract any mentioned user details.
Look specifically for:
1. name
2. email
3. platform (e.g. YouTube, Twitch, Kick, Facebook, LinkedIn)

If the user gives clearly fake or invalid data (e.g. "test@test.com", "fake", "xyz123"), set `has_fake_leads` to true and provide a `fake_reason`.

Always return EXACTLY this JSON format:
{
  "name": "extracted_name_or_null",
  "email": "extracted_email_or_null",
  "platform": "extracted_platform_or_null",
  "has_fake_leads": false,
  "fake_reason": null
}
"""


async def extractor_node(state: AgentState) -> dict:
    recent_messages = state["messages"][-6:]
    
    if not recent_messages:
        return {"collected": state.get("collected", {}), "has_fake_leads": False}

    llm = ChatOpenAI(
        model=settings.model_name,
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
        max_tokens=150,
        temperature=0,
    )

    conversation_text = "\n".join(
        [f"{m.type.capitalize()}: {m.content}" for m in recent_messages]
    )

    # Grok free tier rate limit
    await asyncio.sleep(1)

    try:
        req = f"Focus on this conversation history:\n{conversation_text}"
        response = await llm.ainvoke([
            SystemMessage(content=EXTRACTOR_SYSTEM_PROMPT),
            HumanMessage(content=req)
        ])
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        
        result = json.loads(content)
        
        collected = dict(state.get("collected", {}))
        for key in ["name", "email", "platform"]:
            if result.get(key) is not None and result.get(key) != "null":
                collected[key] = result[key]

        has_fake = bool(result.get("has_fake_leads", False))
        fake_reason = result.get("fake_reason")

        logger.info(f"Extraction result | Collected: {collected} | Fake: {has_fake}")

        return {
            "collected": collected,
            "has_fake_leads": has_fake,
            "fake_reason": fake_reason,
        }
    except Exception as e:
        logger.error(f"Extractor failed: {e}")
        return {"collected": state.get("collected", {}), "has_fake_leads": False}
