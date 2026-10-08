"""LangGraph triage agent with an evidence-based gate. UNTESTED: LangGraph is not installed in my
build sandbox. The decision logic it calls (gating.py) IS tested; this file only wires it up.

Flow:  propose -> gate -> (auto: apply)  |  (review: pause for human -> apply)
Resume a paused run with:  graph.invoke(Command(resume="approve"), config)
"""
from __future__ import annotations

from typing import Callable, TypedDict

from .gating import gate_tier, resolve_label
from .policy import AUTO


class TriageState(TypedDict, total=False):
    issue_id: str
    title: str
    body: str
    proposal: str
    tier: str
    human_reply: str
    final_label: str | None


def build_graph(classify: Callable[[str, str], str], policy: dict[str, str]):
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import END, START, StateGraph
    from langgraph.types import interrupt

    def propose(state: TriageState) -> dict:
        return {"proposal": classify(state["title"], state.get("body", ""))}

    def gate(state: TriageState) -> dict:
        return {"tier": gate_tier(state["proposal"], policy)}

    def route(state: TriageState) -> str:
        return "apply" if state["tier"] == AUTO else "human_review"

    def human_review(state: TriageState) -> dict:
        reply = interrupt({
            "issue_id": state.get("issue_id"),
            "proposed_label": state["proposal"],
            "instruction": "Reply 'approve', a label (bug/feature/question/docs), or 'reject'.",
        })
        return {"human_reply": reply}

    def apply(state: TriageState) -> dict:
        return {"final_label": resolve_label(state["proposal"], state["tier"], state.get("human_reply"))}

    g = StateGraph(TriageState)
    g.add_node("propose", propose)
    g.add_node("gate", gate)
    g.add_node("human_review", human_review)
    g.add_node("apply", apply)
    g.add_edge(START, "propose")
    g.add_edge("propose", "gate")
    g.add_conditional_edges("gate", route, {"apply": "apply", "human_review": "human_review"})
    g.add_edge("human_review", "apply")
    g.add_edge("apply", END)
    return g.compile(checkpointer=MemorySaver())
