import csv
import os
import logging
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

from schemas import TicketResult
from faiss_retriever import FaissRetriever
from llm_client import classify_ticket, draft_reply
from config import CONFIDENCE_THRESHOLD

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pipeline")

retriever = FaissRetriever()


class TicketState(TypedDict):
    ticket_id: str
    subject: str
    body: str
    category: Optional[str]
    confidence: Optional[float]
    retrieved_context: Optional[str]
    draft_reply: Optional[str]
    action: Optional[str]
    flagged_reason: Optional[str]


def classify_node(state: TicketState) -> TicketState:
    result = classify_ticket(state["subject"], state["body"])
    logger.info(f"[{state['ticket_id']}] classified as {result.category} ({result.confidence:.2f})")
    return {**state, "category": result.category, "confidence": result.confidence}


def retrieve_node(state: TicketState) -> TicketState:
    context = retriever.retrieve(state["category"])
    return {**state, "retrieved_context": context}


def draft_node(state: TicketState) -> TicketState:
    reply = draft_reply(state["subject"], state["body"], state["retrieved_context"])
    return {**state, "draft_reply": reply}


def decide_node(state: TicketState) -> TicketState:
    category = state["category"]
    confidence = state["confidence"]
    body = state["body"].lower()

    if category == "Unroutable":
        action, reason = "needs_human_review", "Could not classify ticket (empty/unclear input)"
    elif "refund" in body:
        # Safety net: any ticket mentioning "refund" always goes to human
        # review, regardless of which category the classifier assigned
        # catches multi-issue tickets like T-7 where a refund-relevant
        # ticket gets classified under a different primary category
        # (e.g. Shipping) and would otherwise slip through as auto-approved.
        action, reason = "needs_human_review", "Ticket mentions refund, requires human sign-off regardless of category"
    elif confidence < CONFIDENCE_THRESHOLD:
        action, reason = "needs_human_review", f"Low confidence ({confidence:.2f})"
    elif category == "Refund":
        action, reason = "needs_human_review", "Refund tickets always require human sign-off (v1 policy)"
    else:
        action, reason = "auto_approved", None

    return {**state, "action": action, "flagged_reason": reason}


def build_graph():
    graph = StateGraph(TicketState)
    graph.add_node("classify", classify_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("draft", draft_node)
    graph.add_node("decide", decide_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "draft")
    graph.add_edge("draft", "decide")
    graph.add_edge("decide", END)

    return graph.compile()


_compiled_graph = build_graph()


def log_result(result: TicketResult, path: str = "results.csv") -> None:
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.model_dump().keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(result.model_dump())


def run_pipeline(ticket_id: str, subject: str, body: str) -> TicketResult:
    initial_state: TicketState = {
        "ticket_id": ticket_id,
        "subject": subject,
        "body": body,
        "category": None,
        "confidence": None,
        "retrieved_context": None,
        "draft_reply": None,
        "action": None,
        "flagged_reason": None,
    }
    final_state = _compiled_graph.invoke(initial_state)
    result = TicketResult(**{k: v for k, v in final_state.items()})
    log_result(result)
    return result


if __name__ == "__main__":
    sample = run_pipeline(
        ticket_id="T-1001",
        subject="Card charged twice",
        body="I was charged twice for order #4521, please refund the extra charge.",
    )
    print(sample.model_dump_json(indent=2))