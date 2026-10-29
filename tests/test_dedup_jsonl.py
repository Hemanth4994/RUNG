import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "dedup_jsonl.py")
sys.path.insert(0, os.path.dirname(SCRIPT))
import dedup_jsonl  # noqa: E402

ROWS = [{"id": "a#1", "v": 1}, {"id": "a#2", "v": 2}, {"id": "a#1", "v": 99}, {"id": "a#3", "v": 3}, {"id": "a#2", "v": 98}]


def _write(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(json.dumps(r) for r in rows) + "\n")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


class TestDedupJsonl(unittest.TestCase):
    def test_keeps_first_and_order(self):
        kept, removed = dedup_jsonl.dedup_lines([json.dumps(r) + "\n" for r in ROWS])
        self.assertEqual(removed, 2)
        self.assertEqual([json.loads(k) for k in kept], [ROWS[0], ROWS[1], ROWS[3]])

    def test_in_place_makes_backup_once(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            _write(p, ROWS)
            subprocess.run([sys.executable, SCRIPT, p, "--in-place"], check=True, capture_output=True)
            self.assertEqual([r["id"] for r in _read(p)], ["a#1", "a#2", "a#3"])
            backup = os.path.join(d, "r.with_duplicates.jsonl")
            self.assertEqual(len(_read(backup)), 5)
            subprocess.run([sys.executable, SCRIPT, p, "--in-place"], check=True, capture_output=True)  # second run: no-op
            self.assertEqual(len(_read(backup)), 5)               # original copy not overwritten
            self.assertEqual(len(_read(p)), 3)

    def test_clean_file_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            _write(p, ROWS[:2])
            subprocess.run([sys.executable, SCRIPT, p, "--in-place"], check=True, capture_output=True)
            self.assertFalse(os.path.exists(os.path.join(d, "r.with_duplicates.jsonl")))

    def test_needs_one_destination(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            _write(p, ROWS)
            r = subprocess.run([sys.executable, SCRIPT, p], capture_output=True)
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
