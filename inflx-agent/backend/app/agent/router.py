from app.agent.state import AgentState

REQUIRED_FIELDS = ["name", "email", "platform"]

def route_after_responder(state: AgentState) -> str:
    collected = state.get("collected", {})
    all_collected = all(field in collected for field in REQUIRED_FIELDS)
    has_fake = state.get("has_fake_leads", False)
    
    if all_collected and not has_fake and not state.get("lead_captured", False):
        return "capture"
    return "end"
