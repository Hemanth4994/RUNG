"""One shadow-mode observation: the agent proposed an action, a human did the real thing."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Record:
    id: str
    ts: datetime        # when the human decision happened (used for time-ordered backtests)
    category: str       # action category the agent proposed, e.g. "label:bug"
    correct: bool       # did the agent's proposal agree with what the human actually did?


def load_records(path: str | Path) -> list[Record]:
    out: list[Record] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            out.append(Record(d["id"], datetime.fromisoformat(d["ts"].replace("Z", "+00:00")),
                              d["category"], bool(d["correct"])))
    return out


def save_records(path: str | Path, records: list[Record]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps({"id": r.id, "ts": r.ts.isoformat(),
                                "category": r.category, "correct": r.correct}) + "\n")
