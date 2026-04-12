import json
import logging
import asyncio
from pathlib import Path
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.config import settings

logger = logging.getLogger(__name__)

kb_path = Path(settings.knowledge_base_path)
with open(kb_path, "r", encoding="utf-8") as f:
    knowledge_base = json.load(f)


@tool
def get_pricing(dummy: str = "") -> str:
    """Use this tool when the user asks about costs, pricing, or how much a plan costs. Returns pricing summary for all plans."""
    plans = knowledge_base.get("plans", [])
    text = "Pricing summary:\n" + "\n".join([f"- {p['name']}: ${p['price_monthly']}/mo" for p in plans])
    summary = knowledge_base.get("pricing_summary", {})
    if summary:
        text += "\n\nQuick reference:\n" + "\n".join([f"- {k}: {v}" for k, v in summary.items()])
    return text


@tool
def get_plans(dummy: str = "") -> str:
    """Use this tool when the user compares plans, asks about features, limits, or which plan is best for them."""
    plans = knowledge_base.get("plans", [])
    text = "Plan comparison and features:\n"
    for p in plans:
        text += f"\n{p['name']} (${p['price_monthly']}/mo):\n"
        text += f"Best for: {p.get('best_for', 'N/A')}\n"
        text += f"Features: {', '.join(p.get('features', []))}\n"
        limitations = p.get("limitations", [])
        if limitations:
            text += f"Limitations: {', '.join(limitations)}\n"
    return text


@tool
def get_policy(dummy: str = "") -> str:
    """Use this tool for policy questions about refunds, cancellations, support availability, upgrades, or trial information."""
    policies = knowledge_base.get("policies", [])
    text = "Policies:\n\n" + "\n\n".join(
        [f"{pol['title']}: {pol.get('detail', pol.get('content', ''))}" for pol in policies]
    )
    return text


@tool
def get_faq(query: str) -> str:
    """Use this tool for how-to, technical, operational, or general product questions about AutoStream. Pass the user question as the query argument."""
    query_words = set(query.lower().replace("?", "").split())
    best_faq = None
    best_score = 0

    for faq in knowledge_base.get("faqs", []):
        q_text = faq.get("question", faq.get("q", ""))
        question_words = set(q_text.lower().replace("?", "").split())
        overlap = len(query_words.intersection(question_words))
        if overlap > best_score:
            best_score = overlap
            best_faq = faq

    if best_score >= 1 and best_faq:
        a_text = best_faq.get("answer", best_faq.get("a", ""))
        q_text = best_faq.get("question", best_faq.get("q", ""))
        return f"FAQ: Q: {q_text}\nA: {a_text}"
    return "No exact FAQ match found."


@tool
def general_info(dummy: str = "") -> str:
    """Use this tool for generic conversation, greetings, or questions that are completely off-topic and unrelated to AutoStream."""
    return ""


TOOLS_MAP = {
    "get_pricing": get_pricing,
    "get_plans": get_plans,
    "get_policy": get_policy,
    "get_faq": get_faq,
    "general_info": general_info
}


async def deterministic_retrieve(messages: list) -> tuple[str, list[str]]:
    llm = ChatOpenAI(
        model=settings.model_name,
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
        max_tokens=100,
        temperature=0,
    )

    llm_with_tools = llm.bind_tools(list(TOOLS_MAP.values()))

    await asyncio.sleep(1)


    conversation_text = "\n".join(
        [f"{m.type.capitalize()}: {m.content}" for m in messages[-5:]]
    )

    try:
        req = (
            "Analyze the following recent conversation snippet (especially the latest user question) "
            "and select the most appropriate retrieval tool to gather the correct context to answer the user.\n"
            f"Conversation:\n{conversation_text}"
        )
        resp = await llm_with_tools.ainvoke([HumanMessage(content=req)])

        tool_calls = resp.tool_calls

        if tool_calls:
            tool_call = tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            logger.info(f"LLM Router selected tool: {tool_name}")

            tool_func = TOOLS_MAP.get(tool_name, general_info)
            context = tool_func.invoke(tool_args)

            citations = []
            if tool_name == "get_pricing":
                citations.append("Pricing Data")
            elif tool_name == "get_plans":
                citations.append("Plan Knowledge Base")
            elif tool_name == "get_policy":
                citations.append("Policies")
            elif tool_name == "get_faq" and context != "No exact FAQ match found.":
                citations.append("FAQ Database")

            return context, citations
        else:
            logger.warning("LLM Router returned no tool calls. Defaulting to general.")
            return "", []

    except Exception as e:
        logger.error(f"Tool-based intent routing failed: {e}")
        return "", []
