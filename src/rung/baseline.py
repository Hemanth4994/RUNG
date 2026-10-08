"""A dumb keyword classifier. It is the bar the LLM agent has to beat, and it needs no API key."""
from __future__ import annotations

import re

_RULES = [
    ("docs", r"\b(docs?|documentation|readme|typo|tutorial)\b"),
    ("question", r"\b(how (do|can|to)|question|is it possible|help me|why does)\b"),
    ("feature", r"\b(feature|enhancement|proposal|would be nice|add support|support for|request)\b"),
    ("bug", r"\b(bug|crash(es|ed)?|error|exception|traceback|fails?|failed|broken|regression)\b"),
]


def predict(title: str, body: str = "") -> str:
    text = f"{title}\n{body}".lower()
    for label, pattern in _RULES:
        if re.search(pattern, text):
            return label
    return "bug"  # most common label in most repos; a deliberate, documented default
