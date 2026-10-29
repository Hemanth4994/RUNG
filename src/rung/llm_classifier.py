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


def resolve_model() -> dict:
    """Which concrete model is behind RUNG_MODEL right now? One cheap call, recorded next to the run.

    Floating aliases such as `gemini-flash-lite-latest` move over time, so a result is only
    reproducible if the model that really answered is written down.
    """
    from langchain.chat_models import init_chat_model

    requested = os.environ.get("RUNG_MODEL", "")
    info: dict = {"requested": requested}
    try:
        meta = init_chat_model(requested, temperature=0).invoke("Reply with OK").response_metadata or {}
        info["resolved"] = meta.get("model_version") or meta.get("model_name") or meta.get("model")
    except Exception as exc:   # recording the model must never stop the run itself
        info["resolved"] = None
        info["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
    return info
