"""Pace and retry model calls, so a free-tier rate limit slows a run down instead of killing it.

Pacing and retrying never change what a successful call returns, and a call that failed leaves no
prediction behind, so this cannot alter any result; it only changes how long a run takes.

    python -m rung.shadow data/holdout_issues.jsonl --predictor llm ...   # paced at 4.5 s/call by default

Two different limits exist on the Gemini free tier, and they need different handling:
  * per-minute (e.g. 15 requests/min): wait the delay the API suggests, then retry the same issue;
  * per-day: retrying is pointless, so stop with a clear message. Progress is already saved, rerun tomorrow.
"""
from __future__ import annotations

import re
import time
from typing import Callable

Predictor = Callable[[str, str], str]


class DailyQuotaExhausted(RuntimeError):
    """The per-day quota is spent. Nothing is lost: finished predictions are already on disk."""


def _text(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def is_daily_quota(exc: BaseException) -> bool:
    t = _text(exc)
    return "PerDay" in t or "per day" in t.lower()


def is_retryable(exc: BaseException) -> bool:
    """Rate limit (429) or a temporary server-side error (503). Anything else is a real bug: re-raise it."""
    t = _text(exc)
    low = t.lower()
    if getattr(exc, "status_code", None) in (429, 503) or getattr(exc, "code", None) in (429, 503):
        return True
    return any(s in t for s in ("RateLimit", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "ServiceUnavailable")) \
        or "rate limit" in low or "overloaded" in low


_DELAY_PATTERNS = (
    re.compile(r"retry in ([0-9]+(?:\.[0-9]+)?)\s*s", re.I),
    re.compile(r"retryDelay'?\"?:\s*'?\"?([0-9]+(?:\.[0-9]+)?)s", re.I),
)


def suggested_delay(exc: BaseException) -> float | None:
    """Seconds the API asked us to wait, if its message says so."""
    t = _text(exc)
    for pat in _DELAY_PATTERNS:
        m = pat.search(t)
        if m:
            return float(m.group(1))
    return None


def throttled(
    predict: Predictor,
    min_interval: float = 0.0,
    max_retries: int = 6,
    base_backoff: float = 5.0,
    max_backoff: float = 65.0,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
    log: Callable[[str], None] = print,
) -> Predictor:
    """Wrap `predict`: at least `min_interval` seconds between calls, and retry on rate limits.

    15 requests/minute is one call per 4 s; the default 4.5 s used by the CLI leaves headroom.
    """
    last_start: list[float | None] = [None]

    def wrapped(title: str, body: str = "") -> str:
        attempt = 0
        while True:
            if last_start[0] is not None:
                wait = min_interval - (clock() - last_start[0])
                if wait > 0:
                    sleep(wait)
            last_start[0] = clock()
            try:
                return predict(title, body)
            except Exception as exc:
                if not is_retryable(exc):
                    raise
                if is_daily_quota(exc):
                    raise DailyQuotaExhausted(
                        "daily quota is used up; finished predictions are saved, rerun the same command later"
                    ) from exc
                attempt += 1
                if attempt > max_retries:
                    raise
                hint = suggested_delay(exc)
                delay = hint + 1.0 if hint is not None else min(base_backoff * 2 ** (attempt - 1), max_backoff)
                log(f"  rate limited (attempt {attempt}/{max_retries}); waiting {delay:.0f}s then retrying the same issue")
                sleep(delay)

    return wrapped
