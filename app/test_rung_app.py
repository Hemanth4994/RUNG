"""Headless tests for the Rung web page (Streamlit's own test runner; no browser, no model, no network).

    pip install -e ".[agent,app]" pytest
    pytest app -q
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).with_name("rung_app.py"))


def fresh() -> AppTest:
    return AppTest.from_file(APP, default_timeout=60).run()


def metrics(at: AppTest) -> dict:
    return {m.label: m.value for m in at.metric}


def test_loads_without_errors_and_shows_the_frozen_result():
    at = fresh()
    assert not at.exception
    m = metrics(at)
    assert m["Handled with no human (holdout)"] == "20.6%"
    assert m["Error on those"] == "2.9%"
    assert m["Wrong if the agent acted on everything"] == "13.4%"
    assert not at.error                                   # no false promotion at the frozen settings


def test_loosening_the_limit_to_10_percent_reproduces_the_post_hoc_check():
    at = fresh()
    at.sidebar.slider(key="limit").set_value(10).run()
    m = metrics(at)
    assert m["Handled with no human (holdout)"] == "74.2%"
    assert m["Error on those"] == "12.9%"
    assert any("False promotion" in e.value and "bug" in e.value for e in at.error)
    assert at.sidebar.warning                              # tells the user they left the frozen settings


def test_five_correct_in_a_row_is_not_enough():
    at = fresh()
    at.number_input(key="calc_n").set_value(5).run()
    at.main.number_input[1].set_value(0).run()             # the "wrong" box: 0 wrong of 5
    m = metrics(at)
    assert m["Raw error"] == "0.0%" and m["Cautious upper bound"] == "35.1%"
    assert m["Decision"].startswith("REVIEW")
    assert any("fewer than" in w.value for w in at.warning)


def test_enough_clean_cases_earns_auto():
    at = fresh()
    at.number_input(key="calc_n").set_value(400).run()
    assert metrics(at)["Decision"] == "AUTO"               # 1 wrong of 400 -> upper bound about 1%


def run_issue(at: AppTest, title: str) -> AppTest:
    at.text_input(key="gate_title").set_value(title).run()
    return at.button(key="run").click().run()


def test_docs_issue_is_applied_with_no_human():
    at = run_issue(fresh(), "Typo in the installation docs")
    assert not at.exception and at.session_state["pending"] is None
    row = at.session_state["history"][0]
    assert row["Agent proposed"] == "docs" and row["Gate"] == "auto" and row["Applied label"] == "docs"


@pytest.mark.parametrize("reply, expected", [("approve", "bug"), ("docs", "docs"), ("reject", "none (rejected)")])
def test_bug_issue_pauses_for_a_human_and_resumes(reply, expected):
    at = run_issue(fresh(), "Crash when calling fit twice")
    assert at.session_state["pending"]["proposal"] == "bug"
    assert not at.session_state["history"]                 # nothing applied while paused
    at = at.button(key=f"reply_{reply}").click().run()
    assert not at.exception and at.session_state["pending"] is None
    row = at.session_state["history"][0]
    assert row["Gate"] == "review" and row["Human said"] == reply and row["Applied label"] == expected


def test_unknown_category_fails_closed():
    at = run_issue(fresh(), "Refactor the build system")
    assert at.session_state["pending"]["proposal"] == "other"
    at = at.button(key="reply_reject").click().run()
    assert at.session_state["history"][0]["Applied label"] == "none (rejected)"


def test_the_gate_follows_the_policy_sidebar():
    at = fresh()
    at.sidebar.slider(key="limit").set_value(10).run()     # bug now earns auto on the dev numbers
    at = run_issue(at, "Crash when calling fit twice")
    assert at.session_state["pending"] is None
    assert at.session_state["history"][0]["Gate"] == "auto"
