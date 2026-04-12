import logging
from app.agent.state import AgentState
from app.rag.retriever import deterministic_retrieve

logger = logging.getLogger(__name__)


async def retriever_node(state: AgentState) -> dict:
    if not state.get("messages"):
        return {"retrieved_context": "", "citations": []}

    context, citations = await deterministic_retrieve(state["messages"])

    logger.info(f"Deterministic retrieval complete | Citations: {citations}")
    return {"retrieved_context": context, "citations": citations}
