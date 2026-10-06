"""Conservative error estimates. The core idea: never trust a raw error rate from a small sample."""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

from .records import Record

Z_95_ONE_SIDED = 1.645


def wilson_upper(errors: int, n: int, z: float = Z_95_ONE_SIDED) -> float:
    """Upper confidence bound on the true error rate (Wilson score interval).

    With n == 0 we know nothing, so the bound is 1.0.
    """
    if n <= 0:
        return 1.0
    p = errors / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return min(1.0, (centre + margin) / denom)


@dataclass(frozen=True)
class CategoryStats:
    category: str
    n: int
    errors: int
    error_rate: float
    upper_bound: float


def category_stats(records: list[Record], z: float = Z_95_ONE_SIDED) -> dict[str, CategoryStats]:
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # [n, errors]
    for r in records:
        counts[r.category][0] += 1
        counts[r.category][1] += 0 if r.correct else 1
    out = {}
    for cat, (n, errs) in counts.items():
        out[cat] = CategoryStats(cat, n, errs, errs / n, wilson_upper(errs, n, z))
    return out
