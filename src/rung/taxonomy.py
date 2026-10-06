"""Collapse messy repo-specific GitHub labels into a small, shared taxonomy."""
from __future__ import annotations

import re

COARSE = ("bug", "feature", "question", "docs")

_KEYWORDS = {
    "bug": {"bug", "defect", "regression", "crash"},
    "feature": {"feature", "enhancement", "feat", "proposal"},
    "question": {"question", "support", "usage"},
    "docs": {"doc", "docs", "documentation"},
}


def coarse_labels(labels: list[str]) -> set[str]:
    """Map raw label names to coarse labels. 'help wanted' etc. are intentionally ignored."""
    found: set[str] = set()
    for name in labels:
        tokens = {t for t in re.split(r"[^a-z0-9]+", name.lower()) if t}
        for coarse, kws in _KEYWORDS.items():
            if tokens & kws:
                found.add(coarse)
    return found
