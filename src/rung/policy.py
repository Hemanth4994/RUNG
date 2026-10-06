"""Turn evidence into tiers. Deliberately simple for v0: 'auto' or 'review'."""
from __future__ import annotations

from dataclasses import dataclass

from .records import Record
from .stats import CategoryStats, Z_95_ONE_SIDED, category_stats

AUTO = "auto"
REVIEW = "review"


@dataclass(frozen=True)
class PolicyConfig:
    max_error: float = 0.05   # highest error rate we are willing to accept on auto-handled actions
    min_n: int = 30           # never promote a category with fewer observations than this
    z: float = Z_95_ONE_SIDED


def decide(stats: CategoryStats, cfg: PolicyConfig) -> str:
    if stats.n >= cfg.min_n and stats.upper_bound <= cfg.max_error:
        return AUTO
    return REVIEW


def build_policy(records: list[Record], cfg: PolicyConfig) -> dict[str, str]:
    return {c: decide(s, cfg) for c, s in category_stats(records, cfg.z).items()}
