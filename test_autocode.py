import unittest
from autocode import complexity_score, decide


class RouterTests(unittest.TestCase):
    def test_simple_task_routes_local(self):
        d = decide("rename a variable in one file", "auto", 5, "qwen3.5:27b")
        self.assertEqual(d.backend, "local")

    def test_complex_task_routes_cloud(self):
        d = decide(
            "Review the production architecture, debug a concurrency race condition and verify a repo-wide database migration with failing tests",
            "auto",
            5,
            "qwen3.5:27b",
        )
        self.assertEqual(d.backend, "cloud")

    def test_forced_modes(self):
        self.assertEqual(decide("hard security architecture", "local", 5, "qwen3.5:27b").backend, "local")
        self.assertEqual(decide("tiny typo", "cloud", 5, "qwen3.5:27b").backend, "cloud")

    def test_score_non_negative(self):
        score, _ = complexity_score("quick simple typo")
        self.assertGreaterEqual(score, 0)


if __name__ == "__main__":
    unittest.main()
