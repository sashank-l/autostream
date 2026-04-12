import logging
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes.extractor import extractor_node
from app.agent.nodes.intent import intent_node
from app.agent.nodes.retriever import retriever_node
from app.agent.nodes.responder import responder_node
from app.agent.nodes.lead_capture import lead_capture_node
from app.agent.router import route_after_responder

logger = logging.getLogger(__name__)

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("extract", extractor_node)
    graph.add_node("classify_intent", intent_node)
    graph.add_node("retrieve", retriever_node)
    graph.add_node("respond", responder_node)
    graph.add_node("capture", lead_capture_node)

    graph.set_entry_point("extract")

    graph.add_edge("extract", "classify_intent")
    graph.add_edge("classify_intent", "retrieve")
    graph.add_edge("retrieve", "respond")

    graph.add_conditional_edges(
        "respond",
        route_after_responder,
        {
            "capture": "capture",
            "end": END,
        },
    )

    graph.add_edge("capture", END)

    return graph.compile()


_compiled_graph = build_graph()


async def run_graph(session_id: str, message: str, state: AgentState) -> AgentState:
    state["messages"] = list(state.get("messages", [])) + [HumanMessage(content=message)]
    state["turn_count"] = state.get("turn_count", 0) + 1

    updated = await _compiled_graph.ainvoke(state)
    logger.info(f"Graph run complete | session={session_id} | intent={updated.get('intent')}")
    return updated

