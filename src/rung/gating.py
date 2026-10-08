"""Pure decision logic for the runtime gate (no LangGraph imports, so it is fully unit-tested)."""
from __future__ import annotations

from .policy import AUTO, REVIEW
from .taxonomy import COARSE


def gate_tier(proposal: str, policy: dict[str, str]) -> str:
    """Fail closed: anything the policy has not explicitly promoted needs a human."""
    return AUTO if policy.get(f"label:{proposal}") == AUTO else REVIEW


def resolve_label(proposal: str, tier: str, human_reply: str | None) -> str | None:
    """Final label to apply, or None if nothing should be applied.

    auto   -> the agent's proposal
    review -> 'approve' keeps the proposal; a valid label replaces it; anything else rejects
    """
    if tier == AUTO:
        return proposal
    reply = (human_reply or "").strip().lower()
    if reply == "approve":
        return proposal
    if reply in COARSE:
        return reply
    return None
