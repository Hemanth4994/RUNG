"""LLM-backed predictor (provider-agnostic via LangChain). UNTESTED: needs network + an API key.

    pip install -e ".[agent]" langchain
    export RUNG_MODEL="<provider>:<model-name>"   # e.g. whatever your account supports
    export LANGSMITH_TRACING=true LANGSMITH_API_KEY=...   # optional: traces every call
"""
from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, Field

SYSTEM = (
    "You triage GitHub issues. Choose exactly one label: bug (something is broken), "
    "feature (new capability requested), question (user needs help or usage guidance), "
    "docs (documentation problem). Reply only through the structured output."
)


class Proposal(BaseModel):
    label: Literal["bug", "feature", "question", "docs"] = Field(description="The single best label")


def make_predictor():
    from langchain.chat_models import init_chat_model

    model = os.environ.get("RUNG_MODEL")
    if not model:
        raise SystemExit("Set RUNG_MODEL, e.g. export RUNG_MODEL='<provider>:<model>'")
    llm = init_chat_model(model, temperature=0).with_structured_output(Proposal)

    def predict(title: str, body: str = "") -> str:
        out = llm.invoke([("system", SYSTEM), ("human", f"Title: {title}\n\nBody:\n{body[:1500]}")])
        return out.label

    return predict
