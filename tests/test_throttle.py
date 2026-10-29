import json
import os
import tempfile
import unittest

from rung.shadow import _done_ids, predictions_to_records, run_shadow
from rung.throttle import DailyQuotaExhausted, is_daily_quota, is_retryable, suggested_delay, throttled

# The real message from the failed holdout run (shortened to the parts that matter).
REAL_429 = (
    "Error calling model 'gemini-flash-lite-latest' (RESOURCE_EXHAUSTED): 429 RESOURCE_EXHAUSTED. "
    "{'error': {'code': 429, 'message': 'You exceeded your current quota. * Quota exceeded for metric: "
    "generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 15, model: gemini-3.5-flash-lite, "
    "description: Generate content requests per minute limit exceeded on Free Tier.\\nPlease retry in 9.303375146s.', "
    "'status': 'RESOURCE_EXHAUSTED', 'details': [{'quotaId': 'GenerateRequestsPerMinutePerProjectPerModel-FreeTier', "
    "'quotaValue': '15'}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '9s'}]}}"
)
DAILY_429 = REAL_429.replace("PerMinute", "PerDay").replace("per minute", "per day")


class RateLimit(Exception):
    pass


class FakeTime:
    """A clock that only moves when somebody sleeps, so tests are instant and exact."""
    def __init__(self):
        self.now = 1000.0
        self.sleeps = []

    def clock(self):
        return self.now

    def sleep(self, s):
        self.sleeps.append(s)
        self.now += s


class TestClassification(unittest.TestCase):
    def test_real_gemini_message(self):
        exc = RateLimit(REAL_429)
        self.assertTrue(is_retryable(exc))
        self.assertFalse(is_daily_quota(exc))      # a per-minute limit must NOT be treated as the daily one
        self.assertAlmostEqual(suggested_delay(exc), 9.303375146, places=6)

    def test_daily_quota_detected(self):
        self.assertTrue(is_daily_quota(RateLimit(DAILY_429)))

    def test_ordinary_errors_are_not_retried(self):
        self.assertFalse(is_retryable(ValueError("bad schema")))
        self.assertFalse(is_retryable(KeyError("label")))

    def test_server_busy_is_retryable(self):
        self.assertTrue(is_retryable(RuntimeError("503 UNAVAILABLE: model is overloaded")))


class TestThrottled(unittest.TestCase):
    def _wrap(self, fn, t, **kw):
        return throttled(fn, sleep=t.sleep, clock=t.clock, log=lambda _m: None, **kw)

    def test_paces_calls(self):
        t = FakeTime()
        starts = []
        p = self._wrap(lambda title, body="": starts.append(t.now) or "bug", t, min_interval=4.5)
        for _ in range(4):
            p("x", "")
        gaps = [b - a for a, b in zip(starts, starts[1:])]
        self.assertTrue(all(g >= 4.5 - 1e-9 for g in gaps), gaps)
        self.assertLess(60 / 4.5, 15)             # 4.5 s spacing = 13.3 requests a minute, under the 15/min cap

    def test_no_pacing_by_default(self):
        t = FakeTime()
        p = self._wrap(lambda title, body="": "bug", t)
        for _ in range(5):
            p("x", "")
        self.assertEqual(t.sleeps, [])

    def test_retries_same_issue_after_suggested_delay(self):
        t = FakeTime()
        calls = []

        def flaky(title, body=""):
            calls.append(title)
            if len(calls) == 1:
                raise RateLimit(REAL_429)
            return "feature"

        out = self._wrap(flaky, t)("issue A", "")
        self.assertEqual(out, "feature")
        self.assertEqual(calls, ["issue A", "issue A"])          # same issue, not skipped
        self.assertAlmostEqual(t.sleeps[0], 9.303375146 + 1.0, places=6)

    def test_exponential_backoff_without_a_hint(self):
        t = FakeTime()
        n = {"c": 0}

        def flaky(title, body=""):
            n["c"] += 1
            if n["c"] <= 3:
                raise RuntimeError("503 UNAVAILABLE")
            return "bug"

        self.assertEqual(self._wrap(flaky, t)("x", ""), "bug")
        self.assertEqual(t.sleeps, [5.0, 10.0, 20.0])

    def test_gives_up_after_max_retries(self):
        t = FakeTime()
        n = {"c": 0}

        def always(title, body=""):
            n["c"] += 1
            raise RateLimit(REAL_429)

        with self.assertRaises(RateLimit):
            self._wrap(always, t, max_retries=2)("x", "")
        self.assertEqual(n["c"], 3)                               # first try + 2 retries

    def test_real_errors_surface_immediately(self):
        t = FakeTime()
        n = {"c": 0}

        def broken(title, body=""):
            n["c"] += 1
            raise ValueError("schema")

        with self.assertRaises(ValueError):
            self._wrap(broken, t)("x", "")
        self.assertEqual((n["c"], t.sleeps), (1, []))

    def test_daily_quota_stops_without_retrying(self):
        t = FakeTime()
        n = {"c": 0}

        def spent(title, body=""):
            n["c"] += 1
            raise RateLimit(DAILY_429)

        with self.assertRaises(DailyQuotaExhausted):
            self._wrap(spent, t)("x", "")
        self.assertEqual((n["c"], t.sleeps), (1, []))


ISSUES = [
    {"id": f"r#{i}", "created_at": f"2026-01-0{i}T00:00:00Z", "title": f"issue {i}", "body": "",
     "human_labels": ["bug"]} for i in range(1, 6)
]


class TestWithShadowRunner(unittest.TestCase):
    def test_a_rate_limit_mid_run_leaves_one_row_per_issue(self):
        t = FakeTime()
        n = {"c": 0}

        def flaky(title, body=""):
            n["c"] += 1
            if n["c"] == 3:
                raise RateLimit(REAL_429)
            return "bug"

        p = throttled(flaky, min_interval=4.5, sleep=t.sleep, clock=t.clock, log=lambda _m: None)
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "p.jsonl")
            new = run_shadow(ISSUES, p, out)
            with open(out, encoding="utf-8") as f:
                ids = [json.loads(line)["id"] for line in f]
        self.assertEqual(new, 5)
        self.assertEqual(ids, [f"r#{i}" for i in range(1, 6)])   # no gaps, no duplicates
        self.assertEqual(n["c"], 6)                               # 5 issues + 1 retry

    def test_daily_quota_keeps_finished_work_and_resumes(self):
        t = FakeTime()

        def make(limit):
            n = {"c": 0}

            def predict(title, body=""):
                n["c"] += 1
                if n["c"] > limit:
                    raise RateLimit(DAILY_429)
                return "bug"
            return throttled(predict, sleep=t.sleep, clock=t.clock, log=lambda _m: None)

        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "p.jsonl")
            with self.assertRaises(DailyQuotaExhausted):
                run_shadow(ISSUES, make(2), out)
            self.assertEqual(_done_ids(out), {"r#1", "r#2"})      # finished rows survived
            new = run_shadow(ISSUES, make(99), out)               # "tomorrow"
            self.assertEqual(new, 3)
            self.assertEqual(len(predictions_to_records(out)), 5)

    def test_progress_line(self):
        import contextlib
        import io
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(buf):
            run_shadow(ISSUES, lambda title, body="": "bug", os.path.join(d, "p.jsonl"), progress_every=2)
        self.assertEqual(buf.getvalue().count("new predictions so far"), 2)   # after 2 and after 4


if __name__ == "__main__":
    unittest.main()
