"""Tests for the LangGraph wiring in rung.agent.

They use a fake classifier, so no API key or network is needed. They are skipped
if langgraph is not installed.
"""
import unittest

try:
    from langgraph.types import Command

    from rung.agent import build_graph

    HAVE_LANGGRAPH = True
except ImportError:  # pragma: no cover
    HAVE_LANGGRAPH = False

ISSUE = {"issue_id": "1", "title": "Something is broken", "body": "Traceback ..."}


def run(label, policy):
    """Build a graph whose classifier always answers `label`, and run one issue."""
    graph = build_graph(lambda title, body: label, policy)
    config = {"configurable": {"thread_id": "t1"}}
    result = graph.invoke(dict(ISSUE), config)
    return graph, config, result


@unittest.skipUnless(HAVE_LANGGRAPH, "langgraph not installed")
class AgentFlowTests(unittest.TestCase):
    def test_promoted_category_applies_without_a_human(self):
        _, _, result = run("docs", {"label:docs": "auto"})
        self.assertFalse(result.get("__interrupt__"))
        self.assertEqual(result["tier"], "auto")
        self.assertEqual(result["final_label"], "docs")

    def test_unpromoted_category_pauses_for_review(self):
        graph, config, result = run("bug", {"label:docs": "auto"})
        self.assertTrue(result.get("__interrupt__"))
        self.assertIsNone(result.get("final_label"))
        self.assertEqual(graph.get_state(config).next, ("human_review",))

    def test_empty_policy_fails_closed(self):
        graph, config, result = run("docs", {})
        self.assertTrue(result.get("__interrupt__"))
        self.assertEqual(graph.get_state(config).values["tier"], "review")

    def _resume(self, reply):
        graph, config, _ = run("bug", {})
        return graph.invoke(Command(resume=reply), config)

    def test_approve_keeps_the_proposal(self):
        self.assertEqual(self._resume("approve").get("final_label"), "bug")

    def test_human_can_override_the_label(self):
        self.assertEqual(self._resume("feature").get("final_label"), "feature")

    def test_reject_applies_nothing(self):
        self.assertIsNone(self._resume("reject").get("final_label"))

    def test_unrecognised_reply_applies_nothing(self):
        self.assertIsNone(self._resume("sure thing").get("final_label"))


if __name__ == "__main__":
    unittest.main()
