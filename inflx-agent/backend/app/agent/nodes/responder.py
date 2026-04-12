import logging
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from app.agent.state import AgentState
from app.config import settings

logger = logging.getLogger(__name__)

RESPONDER_SYSTEM_PROMPT = """You are AutoStream's friendly and knowledgeable AI sales assistant.
AutoStream helps content creators automate streaming to multiple platforms simultaneously.

Guidelines:
- First, seamlessly answer the user's immediate question using the provided context. If no context, use general knowledge.
- Be warm, helpful, and concise (2-4 sentences max per response)
- If the user shows buying intent (high_intent), transition to collecting their information.
- ALWAYS answer their questions directly; NEVER aggressively block the conversation just to capture leads.
- If you notice missing lead information (name, email, or platform), append a VERY polite, non-pushy question at the end of your response to ask for JUST ONE missing detail at a time. Do not interrogate.
- If the user provided a fake specific piece of information (fake_reason is present), gently ask them to clarify it using standard professional patterns (e.g. "I noticed that email didn't look quite right, could you double check it?").

If context is provided below, use it to ground your response.
"""


async def responder_node(state: AgentState) -> dict:
    llm = ChatOpenAI(
        model=settings.model_name,
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
        max_tokens=512,
        streaming=True,
    )

    context = state.get("retrieved_context", "")
    collected = state.get("collected", {})
    has_fake = state.get("has_fake_leads", False)
    fake_reason = state.get("fake_reason", "")
    
    missing_fields = [f for f in ["name", "email", "platform"] if f not in collected]

    system_content = RESPONDER_SYSTEM_PROMPT
    if context:
        system_content += f"\n\nRelevant Context:\n{context}"
        
    system_content += f"\n\nLead Extraction State:\nMissing Fields: {', '.join(missing_fields) if missing_fields else 'None'}"
    if has_fake:
        system_content += f"\nWarning: The user recently entered potentially invalid details. Reason: {fake_reason}"

    messages_payload = [SystemMessage(content=system_content)] + state["messages"][-8:]

    # Grok free tier rate limit
    await asyncio.sleep(1)

    tokens = []
    async for chunk in llm.astream(messages_payload):
        token = chunk.content
        if token:
            tokens.append(token)

    full_response = "".join(tokens)
    logger.info(f"Responder generated {len(tokens)} tokens")

    return {
        "messages": [AIMessage(content=full_response)],
        "streaming_tokens": tokens,
    }
