"""Generate fake shadow-mode data to sanity-check the pipeline (NOT a result).

Planted behaviour: 'label:bug' is reliable; 'label:feature' is decent; 'label:question' is poor;
'label:docs' is reliable early, then degrades (the case a backtest must catch).
"""
import random
from datetime import datetime, timedelta, timezone

from rung.records import Record, save_records

random.seed(7)
start = datetime(2026, 1, 1, tzinfo=timezone.utc)
recs = []
for i in range(1200):
    ts = start + timedelta(hours=6 * i)
    cat = random.choices(["label:bug", "label:feature", "label:question", "label:docs"],
                         weights=[40, 25, 20, 15])[0]
    err = {"label:bug": 0.02, "label:feature": 0.07, "label:question": 0.25,
           "label:docs": 0.02 if i < 700 else 0.20}[cat]
    recs.append(Record(f"synthetic#{i}", ts, cat, random.random() > err))
save_records("data/synthetic.jsonl", recs)
print("wrote data/synthetic.jsonl")
