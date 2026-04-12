import logging
from langchain_core.messages import AIMessage
from app.agent.state import AgentState
from app.tools.mock_lead import mock_lead_capture

logger = logging.getLogger(__name__)

def lead_capture_node(state: AgentState) -> dict:
    collected = dict(state.get("collected", {}))
    
    result = mock_lead_capture(
        name=collected.get("name", "Unknown"),
        email=collected.get("email", "Unknown"),
        platform=collected.get("platform", "Unknown"),
    )
    logger.info(f"Lead captured internally: {result}")

    polite_string = "Thank you! I've successfully collected your information. Our team will reach out to you shortly to get you started!"
    
    messages = list(state.get("messages", []))
    messages.append(AIMessage(content=polite_string))

    return {
        "lead_captured": True,
        "streaming_tokens": [word + " " for word in polite_string.split(" ")],
        "messages": messages
    }
