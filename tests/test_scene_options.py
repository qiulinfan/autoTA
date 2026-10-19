import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "skills/auto-ta/scripts/validate_scene_options.py"
SPEC = importlib.util.spec_from_file_location("scene_options", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SceneOptionsTests(unittest.TestCase):
    def test_autonomous_clean_default_and_independent_results(self):
        first = MODULE.normalize({})
        self.assertEqual(first["weathering"], "off")
        self.assertEqual(first["human_review_stages"], ["final"])
        first["human_review_stages"].append("blockout")
        self.assertEqual(MODULE.normalize({})["human_review_stages"], ["final"])

    def test_no_reviews_no_blockout_is_valid(self):
        options = {"blockout": "off", "human_review_stages": [], "weathering": "on"}
        self.assertEqual(MODULE.normalize(options)["human_review_stages"], [])

    def test_explicit_reconstruction_does_not_force_human_review(self):
        result = MODULE.normalize({"intent": "strict_reconstruction", "human_review_stages": []})
        self.assertEqual(result["human_review_stages"], [])

    def test_invalid_or_conflicting_policy_rejected(self):
        cases = [[], {"weathering": True}, {"blockout": "off", "human_review_stages": ["blockout"]},
                 {"human_review_stages": "final"}, {"human_review_stages": [["final"]]},
                 {"human_review_stages": ["final", "final"]}, {"paid_budget": 100},
                 {"repair_attempts_per_issue": True}, {"repair_attempts_per_issue": -1}]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                MODULE.normalize(case)


if __name__ == "__main__":
    unittest.main()
